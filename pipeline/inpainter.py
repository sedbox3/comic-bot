"""Inpainting engine with adaptive dilation and context-aware background sampling."""

import os
import gc
import cv2
import numpy as np
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

MODEL_DIR = Path(__file__).parent.parent / "models"
LAMA_URL = "https://huggingface.co/Carve/LaMa-ONNX/resolve/main/lama_fp32.onnx"


def compute_adaptive_kernel(bh: int) -> int:
    """Dynamic kernel: 4px for tiny fonts, up to 8px for large titles."""
    return max(4, min(8, int(bh * 0.05)))


def sample_surrounding_color(crop_bgr: np.ndarray, dilated_mask: np.ndarray, kernel_size: int) -> tuple:
    """Sample the 3-pixel outer ring around the dilated mask to get background color."""
    ring_kernel = cv2.getStructuringElement(
        cv2.MORPH_ELLIPSE, (kernel_size + 4, kernel_size + 4)
    )
    outer_mask = cv2.dilate(dilated_mask, ring_kernel, iterations=1)
    sample_ring = cv2.bitwise_xor(outer_mask, dilated_mask)

    surrounding_pixels = crop_bgr[sample_ring > 0]
    if len(surrounding_pixels) > 0:
        bg_variance = np.var(surrounding_pixels, axis=0).mean()
        median_bg = np.median(surrounding_pixels, axis=0).astype(int)
        return median_bg, bg_variance
    return np.array([255, 255, 255]), 999


class SmartInpainter:
    """
    Ultra-high precision inpainting with adaptive dilation and context-aware fill.
    
    - Adaptive kernel based on box height
    - Local background color sampling
    - Dual branch: solid fill for flat bubbles, LaMa for textured/gradient
    - Fixed 512x512 tensor input for LaMa ONNX
    """

    def __init__(self, model_path: str = None):
        self.model_path = model_path or str(MODEL_DIR / "lama_fp32.onnx")
        self.session = None
        self.input_names = []
        self.output_names = []
        self._load_model()

    def _load_model(self):
        try:
            import onnxruntime as ort
            if os.path.exists(self.model_path) and os.path.getsize(self.model_path) > 1000:
                # Leverage GPU if available, otherwise fast CPU
                available_providers = ort.get_available_providers()
                providers = ['CUDAExecutionProvider', 'CPUExecutionProvider'] if 'CUDAExecutionProvider' in available_providers else ['CPUExecutionProvider']
                
                sess_options = ort.SessionOptions()
                sess_options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
                sess_options.execution_mode = ort.ExecutionMode.ORT_SEQUENTIAL
                sess_options.enable_cpu_mem_arena = False  # Disable to prevent OOM
                sess_options.intra_op_num_threads = 1
                sess_options.inter_op_num_threads = 1
                
                self.session = ort.InferenceSession(
                    self.model_path,
                    sess_options=sess_options,
                    providers=providers,
                )
                self.input_names = [inp.name for inp in self.session.get_inputs()]
                self.output_names = [out.name for out in self.session.get_outputs()]
                logger.info(f"LaMa ONNX loaded: {self.model_path} (mem_arena=False, sequential)")
            else:
                logger.warning("LaMa ONNX not found, using OpenCV fallback only")
        except ImportError:
            logger.warning("onnxruntime not installed, using OpenCV fallback only")
        except Exception as e:
            logger.warning(f"LaMa ONNX load failed: {e}")

    def inpaint(self, image: np.ndarray, mask: np.ndarray, bbox: tuple = None) -> np.ndarray:
        """
        Context-aware inpainting.
        
        Args:
            image: Full BGR image
            mask: Binary mask of text strokes (uint8, 0 or 255)
            bbox: (x, y, w, h) of the bubble for adaptive dilation
        """
        if np.sum(mask) == 0:
            return image.copy()

        result = image.copy()
        x, y, w, h = bbox if bbox else (0, 0, mask.shape[1], mask.shape[0])

        # Clamp to image bounds
        x1 = max(0, x)
        y1 = max(0, y)
        x2 = min(image.shape[1], x + w)
        y2 = min(image.shape[0], y + h)

        if x2 <= x1 or y2 <= y1:
            return result

        crop_bgr = image[y1:y2, x1:x2].copy()
        crop_mask = mask[y1:y2, x1:x2].copy()

        if np.sum(crop_mask) == 0:
            return result

        # Step 1: Adaptive dilation based on box height
        kernel_size = compute_adaptive_kernel(h)
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (kernel_size, kernel_size))
        dilated_mask = cv2.dilate(crop_mask, kernel, iterations=1)

        # Step 2: Sample surrounding background color
        median_bg, bg_variance = sample_surrounding_color(crop_bgr, dilated_mask, kernel_size)

        # Step 3: Dual execution branch
        if bg_variance < 20:
            # Solid/flat bubble - direct fill (fast, crisp)
            logger.debug(f"Solid fill: variance={bg_variance:.1f}, color={median_bg}")
            crop_bgr[dilated_mask > 0] = median_bg.astype(np.uint8)
        else:
            # Art/gradient/texture - use LaMa or OpenCV inpaint
            logger.debug(f"Inpaint fill: variance={bg_variance:.1f}")
            
            if self.session is not None:
                # LaMa with feathered mask
                feathered = cv2.GaussianBlur(dilated_mask, (3, 3), 0)
                crop_bgr = self._lama_inpaint_region(crop_bgr, feathered)
            else:
                # OpenCV fallback with feathered edges
                feathered = cv2.GaussianBlur(dilated_mask, (3, 3), 0)
                crop_bgr = cv2.inpaint(crop_bgr, feathered, 7, cv2.INPAINT_TELEA)

        result[y1:y2, x1:x2] = crop_bgr
        return result

    def _lama_inpaint_region(self, crop_bgr: np.ndarray, crop_mask: np.ndarray) -> np.ndarray:
        """
        Pads/resizes variable-sized crops to fixed 512x512 tensor for LaMa ONNX,
        then maps the reconstructed region seamlessly back to original dimensions.
        """
        orig_h, orig_w = crop_bgr.shape[:2]
        if orig_h == 0 or orig_w == 0:
            return crop_bgr

        # 1. Aspect-ratio preserving scale to fit inside 512x512
        target_size = 512
        scale = min(target_size / orig_h, target_size / orig_w)
        
        # Only resize if actually larger than target
        if scale < 1.0:
            new_w = int(orig_w * scale)
            new_h = int(orig_h * scale)
            resized_img = cv2.resize(crop_bgr, (new_w, new_h), interpolation=cv2.INTER_CUBIC)
            resized_mask = cv2.resize(crop_mask, (new_w, new_h), interpolation=cv2.INTER_NEAREST)
        else:
            new_w, new_h = orig_w, orig_h
            resized_img = crop_bgr.copy()
            resized_mask = crop_mask.copy()

        # 2. Pad to exactly 512x512 (Letterboxing with edge reflection)
        pad_top = (target_size - new_h) // 2
        pad_bottom = target_size - new_h - pad_top
        pad_left = (target_size - new_w) // 2
        pad_right = target_size - new_w - pad_left

        padded_img = cv2.copyMakeBorder(resized_img, pad_top, pad_bottom, pad_left, pad_right, cv2.BORDER_REFLECT)
        padded_mask = cv2.copyMakeBorder(resized_mask, pad_top, pad_bottom, pad_left, pad_right, cv2.BORDER_CONSTANT, value=0)

        # 3. Normalize to [0, 1] NCHW tensors
        img_tensor = padded_img.astype(np.float32) / 255.0
        img_tensor = np.transpose(img_tensor, (2, 0, 1))
        img_tensor = np.expand_dims(img_tensor, axis=0)  # Shape: (1, 3, 512, 512)

        mask_tensor = (padded_mask > 0).astype(np.float32)
        mask_tensor = np.expand_dims(mask_tensor, axis=(0, 1))  # Shape: (1, 1, 512, 512)

        # Map inputs dynamically based on model signature
        inputs = {}
        for inp_name in self.input_names:
            if "mask" in inp_name.lower():
                inputs[inp_name] = mask_tensor
            else:
                inputs[inp_name] = img_tensor

        # Free memory before inference
        del resized_img, resized_mask, padded_img, padded_mask
        gc.collect()

        # 4. Run Inference
        try:
            preds = self.session.run(self.output_names, inputs)[0]
        except Exception as e:
            logger.warning(f"LaMa inference failed: {e}. Falling back to fast OpenCV Telea.")
            return cv2.inpaint(crop_bgr, crop_mask, 3, cv2.INPAINT_TELEA)
        finally:
            # Always free tensors after inference
            del inputs, img_tensor, mask_tensor
            gc.collect()

        # 5. Extract output and unpad back to original crop resolution
        out_img = preds[0]
        if out_img.shape[0] == 3:
            out_img = np.transpose(out_img, (1, 2, 0))  # Convert CHW to HWC
        
        # Clamp & convert to uint8 BGR
        out_img = np.clip(out_img * 255.0 if out_img.max() <= 1.0 else out_img, 0, 255).astype(np.uint8)

        # Crop out padding
        unpadded = out_img[pad_top:pad_top + new_h, pad_left:pad_left + new_w]
        
        # Resize back to exact original crop dimensions
        restored = cv2.resize(unpadded, (orig_w, orig_h), interpolation=cv2.INTER_CUBIC)

        # Blend only modified mask pixels back onto original canvas
        mask_3ch = cv2.cvtColor(crop_mask, cv2.COLOR_GRAY2BGR) / 255.0
        final_crop = (restored * mask_3ch + crop_bgr * (1.0 - mask_3ch)).astype(np.uint8)
        
        # Free memory
        del out_img, unpadded, restored, mask_3ch
        gc.collect()
        
        return final_crop


class LaMaInpainter:
    """Legacy wrapper for backward compatibility."""

    def __init__(self, model_path: str = None):
        self.model_path = model_path or str(MODEL_DIR / "lama_fp32.onnx")
        self.session = None
        self._load_model()

    def _load_model(self):
        try:
            import onnxruntime as ort
            if os.path.exists(self.model_path) and os.path.getsize(self.model_path) > 1000:
                sess_options = ort.SessionOptions()
                sess_options.execution_mode = ort.ExecutionMode.ORT_SEQUENTIAL
                sess_options.enable_cpu_mem_arena = False
                sess_options.intra_op_num_threads = 1
                
                self.session = ort.InferenceSession(
                    self.model_path,
                    sess_options=sess_options,
                    providers=["CPUExecutionProvider"],
                )
                self.input_name = self.session.get_inputs()[0].name
                self.mask_name = self.session.get_inputs()[1].name
                logger.info(f"LaMa ONNX loaded (legacy): {self.model_path}")
            else:
                logger.warning("LaMa ONNX not found or too small, using fallback")
        except ImportError:
            logger.warning("onnxruntime not installed, using OpenCV fallback")
        except Exception as e:
            logger.warning(f"LaMa ONNX load failed: {e}")

    def inpaint(self, image: np.ndarray, mask: np.ndarray) -> np.ndarray:
        """Inpaint using LaMa or fallback to smart OpenCV."""
        result = image.copy()

        # Step 1: Fill solid-color regions first (fast, sharp)
        solid_mask = self._detect_solid(image, mask)
        result = self._fill_solid(result, mask, solid_mask)

        # Step 2: Handle remaining (complex) regions
        remaining = cv2.bitwise_and(mask, cv2.bitwise_not(solid_mask))
        if np.sum(remaining) > 0:
            if self.session is not None:
                result = self._lama_inpaint(result, remaining)
            else:
                # Fallback: better OpenCV with larger radius
                result = cv2.inpaint(result, remaining, 7, cv2.INPAINT_TELEA)

        return result

    def _detect_solid(self, image: np.ndarray, mask: np.ndarray) -> np.ndarray:
        """Detect solid-color regions (white bubbles, etc)."""
        solid = np.zeros_like(mask)
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            if w < 10 or h < 10:
                continue

            roi = image[y:y + h, x:x + w]
            mask_roi = mask[y:y + h, x:x + w]

            # Sample border pixels
            border_px = 5
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (border_px * 2, border_px * 2))
            dilated = cv2.dilate(mask_roi, kernel)
            border = cv2.subtract(dilated, mask_roi)

            total_border = np.sum(border > 0)
            if total_border < 30:
                continue

            border_pixels = roi[border > 0]
            std_color = np.std(border_pixels, axis=0)

            # Solid if low variance
            if np.all(std_color < 15):
                median_color = np.median(border_pixels, axis=0).astype(np.uint8)
                fill = mask_roi > 0
                result_roi = roi.copy()
                result_roi[fill] = median_color
                image[y:y + h, x:x + w] = result_roi
                solid[y:y + h, x:x + w] = mask_roi
                logger.debug(f"Solid fill at ({x},{y}) std={std_color.astype(int)}")

        return solid

    def _fill_solid(self, image: np.ndarray, mask: np.ndarray, solid_mask: np.ndarray) -> np.ndarray:
        """Fill solid-masked regions with border color."""
        result = image.copy()
        contours, _ = cv2.findContours(solid_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            roi = image[y:y + h, x:x + w]
            solid_roi = solid_mask[y:y + h, x:x + w]

            border_px = 5
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (border_px * 2, border_px * 2))
            dilated = cv2.dilate(solid_roi, kernel)
            border = cv2.subtract(dilated, solid_roi)

            if np.sum(border > 0) > 0:
                border_pixels = roi[border > 0]
                color = np.median(border_pixels, axis=0).astype(np.uint8)
            else:
                color = np.array([255, 255, 255], dtype=np.uint8)

            fill = solid_roi > 0
            result[y:y + h, x:x + w][fill] = color

        return result

    def _lama_inpaint(self, image: np.ndarray, mask: np.ndarray) -> np.ndarray:
        """Run LaMa ONNX model on the masked regions."""
        h, w = image.shape[:2]

        # Pad to 8px multiple
        pad_h = (8 - h % 8) % 8
        pad_w = (8 - w % 8) % 8
        if pad_h > 0 or pad_w > 0:
            image = cv2.copyMakeBorder(image, 0, pad_h, 0, pad_w, cv2.BORDER_REFLECT)
            mask = cv2.copyMakeBorder(mask, 0, pad_h, 0, pad_w, cv2.BORDER_CONSTANT, value=0)

        # Normalize
        img_float = image.astype(np.float32) / 255.0
        img_float = np.transpose(img_float, (2, 0, 1))  # HWC -> CHW
        img_float = np.expand_dims(img_float, 0)  # Add batch

        mask_float = mask.astype(np.float32) / 255.0
        mask_float = np.expand_dims(np.expand_dims(mask_float, 0), 0)

        # Free memory before inference
        gc.collect()

        # Run inference
        try:
            result = self.session.run(
                None,
                {self.input_name: img_float, self.mask_name: mask_float},
            )[0]
        finally:
            del img_float, mask_float
            gc.collect()

        # Post-process
        result = np.transpose(result[0], (1, 2, 0))  # CHW -> HWC
        result = np.clip(result * 255, 0, 255).astype(np.uint8)

        # Unpad
        result = result[:h, :w]

        # Blend: only replace masked areas
        blend_mask = mask[:h, :w] > 0
        output = image[:h, :w].copy()
        output[blend_mask] = result[blend_mask]

        return output


class Inpainter:
    """Legacy wrapper."""

    def __init__(self, method: str = "ns", radius: int = 5):
        self.method = method
        self.radius = radius

    def inpaint(self, image: np.ndarray, mask: np.ndarray) -> np.ndarray:
        flag = cv2.INPAINT_NS if self.method == "ns" else cv2.INPAINT_TELEA
        return cv2.inpaint(image, mask, self.radius, flag)
