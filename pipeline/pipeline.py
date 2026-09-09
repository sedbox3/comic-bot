"""Unified comic translation pipeline - with proper scaling and RapidOCR."""

import os
import sys

# Prevent OpenMP and ONNX thread contention deadlock on shared cloud vCPUs
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["VECLIB_MAXIMUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"
os.environ["ORT_DISABLE_TELEMETRY"] = "1"

import re
import cv2
import json
import numpy as np
import logging
import gc
import tempfile
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Tuple, Optional, Dict

BT_PATH = Path(r"E:\apppcomic\BallonsTranslator")
if str(BT_PATH) not in sys.path:
    sys.path.insert(0, str(BT_PATH))

logger = logging.getLogger(__name__)

# Use temp directory for debug crops to avoid triggering auto-reloader
DEBUG_CROPS = Path(tempfile.gettempdir()) / "comic_translator" / "debug_crops"


def extract_text_style(crop_bgr: np.ndarray, text_mask: np.ndarray) -> Tuple[Tuple[int, int, int], bool]:
    """
    Analyze the original un-inpainted text crop to determine:
    1. RGB font color
    2. Boldness flag
    """
    if text_mask is None or np.count_nonzero(text_mask) == 0:
        return (0, 0, 0), False

    # 1. Stroke pixels extraction
    stroke_bgr = crop_bgr[text_mask > 0]
    if len(stroke_bgr) < 15:
        return (0, 0, 0), False

    # 2. Filter out background bleeding (near-white or flat bubble background)
    bg_color = np.median(crop_bgr[text_mask == 0], axis=0) if np.count_nonzero(text_mask == 0) > 0 else np.array([255, 255, 255])

    # Calculate color distance to background
    diff = np.linalg.norm(stroke_bgr.astype(float) - bg_color.astype(float), axis=1)
    contrast_strokes = stroke_bgr[diff > 35]

    if len(contrast_strokes) > 10:
        stroke_bgr = contrast_strokes

    # 3. Median RGB calculation
    median_bgr = np.median(stroke_bgr, axis=0).astype(int)
    r, g, b = int(median_bgr[2]), int(median_bgr[1]), int(median_bgr[0])

    # Clamp near-black / dark neutral strokes to pure black
    brightness = 0.299 * r + 0.587 * g + 0.114 * b
    max_channel_diff = max(r, g, b) - min(r, g, b)
    if brightness < 65 and max_channel_diff < 25:
        final_color = (0, 0, 0)
    else:
        final_color = (r, g, b)

    # 4. Boldness detection based on stroke density ratio
    stroke_area = np.count_nonzero(text_mask)
    total_area = text_mask.shape[0] * text_mask.shape[1]
    density = stroke_area / total_area if total_area > 0 else 0
    is_bold = density > 0.18

    logger.debug(f"Text style: color={final_color}, bold={is_bold}, density={density:.3f}")

    return final_color, is_bold


@dataclass
class BubbleGroup:
    """A merged speech bubble containing one or more text lines."""
    x: int
    y: int
    w: int
    h: int
    texts: List[str] = field(default_factory=list)
    translation: str = ""
    confidence: float = 0.0
    text_color: Tuple[int, int, int] = (0, 0, 0)  # Extracted RGB color
    is_bold: bool = False  # Extracted font weight

    @property
    def full_text(self) -> str:
        return " ".join(self.texts).strip()

    @property
    def bbox(self) -> Tuple[int, int, int, int]:
        return (self.x, self.y, self.w, self.h)

    @property
    def center(self) -> Tuple[int, int]:
        return (self.x + self.w // 2, self.y + self.h // 2)


class ComicPipeline:

    def __init__(
        self,
        llm_api_key: Optional[str] = None,
        llm_base_url: Optional[str] = None,
        llm_model: Optional[str] = None,
        system_prompt: Optional[str] = None,
        font_path: Optional[str] = None,
    ):
        self.font_path = font_path or self._find_font()
        self.llm_api_key = llm_api_key
        self.llm_base_url = llm_base_url
        self.llm_model = llm_model
        self.system_prompt = system_prompt

        self._detector = None
        self._ocr_engine = None
        self._bt_cwd = str(BT_PATH)

        # Verify font
        if not os.path.exists(self.font_path):
            logger.error(f"Arabic font NOT FOUND: {self.font_path}")
        else:
            logger.info(f"Arabic font: {self.font_path}")

        logger.info("Pipeline initialized")

    def _find_font(self) -> str:
        """Find Arabic font - prefer Hayah comic font."""
        base_dir = os.path.dirname(os.path.abspath(__file__))
        fonts_dir = os.path.join(base_dir, "..", "fonts")

        # Primary: Hayah comic font
        hayah_path = os.path.join(fonts_dir, "Hayah.ttf")
        if os.path.exists(hayah_path):
            return hayah_path

        # Case-insensitive fallback
        hayah_lower = os.path.join(fonts_dir, "hayah.ttf")
        if os.path.exists(hayah_lower):
            return hayah_lower

        # Fallback to NotoSans
        noto_path = os.path.join(fonts_dir, "NotoSansArabic-Regular.ttf")
        if os.path.exists(noto_path):
            return noto_path

        return ""

    def _get_detector(self):
        if self._detector is None:
            # Try to load CTD detector from BallonsTranslator
            if os.path.exists(self._bt_cwd):
                old_cwd = os.getcwd()
                os.chdir(self._bt_cwd)
                try:
                    from ballontranslator.modules.textdetector import TEXTDETECTORS
                    DetectorClass = TEXTDETECTORS.resolve_module('ctd')
                    self._detector = DetectorClass(device='cpu')
                    self._detector.load_model()
                    if hasattr(self._detector, 'set_param'):
                        self._detector.set_param('detect_size', 1024)
                        self._detector.set_param('mask dilate size', 5)
                    logger.info("CTD detector loaded")
                except Exception as e:
                    logger.warning(f"Failed to load CTD detector: {e}")
                    self._detector = "rapidocr"
                finally:
                    os.chdir(old_cwd)
            else:
                logger.info("BallonsTranslator not found, using RapidOCR DBNet detection")
                self._detector = "rapidocr"
        return self._detector

    def _get_ocr(self):
        """Get ComicOCR engine with preprocessing."""
        if self._ocr_engine is None:
            from pipeline.ocr_engine import ComicOCR
            self._ocr_engine = ComicOCR()
            logger.info("ComicOCR loaded")
        return self._ocr_engine

    def _detect_and_group(self, image: np.ndarray, page_label: str) -> Tuple[List[BubbleGroup], np.ndarray]:
        """Step 1: Detect text and group into bubbles."""
        orig_h, orig_w = image.shape[:2]
        logger.info(f"[{page_label}] Original image: {orig_w}x{orig_h}")

        # Scale for detection - reduced from 2048 to 1024 to prevent OOM
        scale = 1.0
        max_dim = 1024
        if max(orig_h, orig_w) > max_dim:
            scale = max_dim / max(orig_h, orig_w)
            new_w = int(orig_w * scale)
            new_h = int(orig_h * scale)
            image_scaled = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_AREA)
            logger.info(f"[{page_label}] Scaled to {new_w}x{new_h} for detection (scale={scale:.4f})")
        else:
            new_w, new_h = orig_w, orig_h
            image_scaled = image

        logger.info(f"[{page_label}] Total detected candidate boxes: detecting...")

        detector = self._get_detector()

        # Free memory before detection to prevent OOM
        gc.collect()
        try:
            import torch
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
        except ImportError:
            pass

        # Use RapidOCR DBNet detection if CTD not available
        if detector == "rapidocr":
            logger.info(f"[{page_label}] Using RapidOCR DBNet detection engine...")
            mask_scaled, blk_list = self._rapidocr_detect(image_scaled)
        else:
            try:
                import torch
                with torch.no_grad():
                    mask_scaled, blk_list = detector.detect(image_scaled)
            except ImportError:
                mask_scaled, blk_list = detector.detect(image_scaled)

        logger.info(f"[{page_label}] Total detected candidate boxes: {len(blk_list)}")

        # Scale mask back to original size
        mask = cv2.resize(mask_scaled, (orig_w, orig_h), interpolation=cv2.INTER_NEAREST) if scale != 1.0 else mask_scaled

        # CRITICAL: Scale bounding boxes back to original coordinates
        if scale != 1.0:
            for blk in blk_list:
                if hasattr(blk, 'xyxy'):
                    # xyxy format: [x1, y1, x2, y2]
                    coords = blk.xyxy
                    if isinstance(coords, np.ndarray):
                        coords = coords.tolist()
                    # Scale each coordinate
                    blk.xyxy = [
                        int(round(coords[0] / scale)),  # x1
                        int(round(coords[1] / scale)),  # y1
                        int(round(coords[2] / scale)),  # x2
                        int(round(coords[3] / scale)),  # y2
                    ]
                    logger.debug(f"[{page_label}] Scaled box: {coords} -> {blk.xyxy}")

        # Now run ComicOCR on the ORIGINAL image
        logger.info(f"[{page_label}] Running ComicOCR on original image...")
        ocr = self._get_ocr()

        if ocr is not None:
            blk_list = self._run_ocr(image, blk_list, page_label)
        else:
            logger.warning(f"[{page_label}] No OCR engine available")

        # Build BubbleGroups from OCR results
        # Extract text style BEFORE inpainting
        bubbles = []
        for i, blk in enumerate(blk_list):
            text = blk.get_text() if hasattr(blk, 'get_text') else ''
            coords = getattr(blk, 'xyxy', None)

            if not coords:
                continue

            if isinstance(coords, (list, tuple)):
                x1, y1, x2, y2 = coords
            else:
                x1, y1, x2, y2 = coords[0], coords[1], coords[2], coords[3]

            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
            w, h = x2 - x1, y2 - y1

            if w < 10 or h < 10:
                continue

            # Extract text style from original image BEFORE inpainting
            text_color = (0, 0, 0)
            is_bold = False

            # Clamp to image bounds
            cx1 = max(0, x1)
            cy1 = max(0, y1)
            cx2 = min(image.shape[1], x2)
            cy2 = min(image.shape[0], y2)

            if cx2 > cx1 and cy2 > cy1:
                crop = image[cy1:cy2, cx1:cx2]
                # Get text mask for this region
                text_mask = mask[cy1:cy2, cx1:cx2] if mask is not None else None

                if text_mask is not None and np.count_nonzero(text_mask) > 0:
                    text_color, is_bold = extract_text_style(crop, text_mask)
                    logger.info(f"[{page_label}] Block {i} style: color={text_color}, bold={is_bold}")

            # Create bubble with extracted style
            bubbles.append(BubbleGroup(
                x=x1, y=y1, w=w, h=h,
                texts=[text] if text.strip() else [""],
                text_color=text_color,
                is_bold=is_bold,
            ))

            if text.strip():
                logger.info(f"[{page_label}] Block {i}: '{text}' at ({x1},{y1}) {w}x{h}")
            else:
                logger.info(f"[{page_label}] Block {i}: (empty) at ({x1},{y1}) {w}x{h}")

        # Group nearby lines
        grouped = self._group_bubbles(bubbles)
        logger.info(f"[{page_label}] Merged into bubbles: {len(grouped)}")

        return grouped, mask

    def _run_ocr(self, image: np.ndarray, blk_list, page_label: str) -> list:
        """Run ComicOCR on each detected text block."""
        ocr = self._get_ocr()
        if ocr is None:
            return blk_list

        # Create debug directory
        debug_dir = DEBUG_CROPS
        debug_dir.mkdir(exist_ok=True)

        for i, blk in enumerate(blk_list):
            coords = getattr(blk, 'xyxy', None)
            if not coords:
                continue

            if isinstance(coords, (list, tuple)):
                x1, y1, x2, y2 = coords
            else:
                x1, y1, x2, y2 = coords[0], coords[1], coords[2], coords[3]

            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)

            # Clamp to image bounds
            x1 = max(0, x1)
            y1 = max(0, y1)
            x2 = min(image.shape[1], x2)
            y2 = min(image.shape[0], y2)

            if x2 <= x1 or y2 <= y1:
                continue

            w, h = x2 - x1, y2 - y1

            # Save debug crops (first 5)
            if i < 5:
                crop = image[y1:y2, x1:x2]
                crop_path = debug_dir / f"crop_{i}_{x1}_{y1}.png"
                cv2.imwrite(str(crop_path), crop)
                logger.info(f"[{page_label}] Saved debug crop: {crop_path}")

            # Run ComicOCR with preprocessing
            text = ocr.ocr_bubble(image, x1, y1, w, h, block_id=i)

            if hasattr(blk, 'text'):
                blk.text = [text] if text else []
            else:
                blk._text = text

        return blk_list

    def _group_bubbles(self, bubbles: List[BubbleGroup]) -> List[BubbleGroup]:
        """
        Merge ONLY text lines that are clearly inside the same bubble.
        Do NOT merge separate chained bubbles - keep them independent.
        """
        if not bubbles:
            return []

        # Sort by Y then X for natural reading order
        bubbles.sort(key=lambda b: (b.y, b.x))

        # DISABLE aggressive merging - return bubbles as-is
        # Each detected text block is its own independent bubble
        logger.info(f"Bubbles kept separate: {len(bubbles)} (no merging)")
        return bubbles

    def _rapidocr_detect(self, image: np.ndarray):
        """Use RapidOCR's built-in DBNet text detection with downscaling for cloud performance."""
        import cv2
        import numpy as np
        import time
        
        try:
            from rapidocr_onnxruntime import RapidOCR
            
            # Configure RapidOCR for lightweight detection
            ocr = RapidOCR(
                det_limit_side_len=1024,    # Ultra-light for cloud containers
                det_limit_type='max',
                det_db_thresh=0.2,          # Low threshold to capture stylized comic fonts
                det_db_box_thresh=0.3,      # Retain smaller shouts and whispers
                det_db_unclip_ratio=1.6     # Expand box contour to cover full dialogue words
            )
            
            orig_h, orig_w = image.shape[:2]
            max_det_side = 1024
            
            # Downscale for detection to save memory
            if max(orig_h, orig_w) > max_det_side:
                scale = max_det_side / max(orig_h, orig_w)
                det_w = int(orig_w * scale)
                det_h = int(orig_h * scale)
                det_image = cv2.resize(image, (det_w, det_h), interpolation=cv2.INTER_AREA)
                logger.info(f"[RapidOCR] Downscaled to {det_w}x{det_h} for ultra-light detection (scale={scale:.4f})")
            else:
                scale = 1.0
                det_image = image
                logger.info(f"[RapidOCR] Running DBNet on {orig_w}x{orig_h}...")
            
            t0 = time.time()
            result, _ = ocr(det_image)
            elapsed = time.time() - t0
            logger.info(f"[RapidOCR] Detection finished in {elapsed:.2f}s")
            
            if not result:
                logger.warning("[RapidOCR] No text detected on page.")
                return np.zeros(image.shape[:2], dtype=np.uint8), []
            
            mask = np.zeros((orig_h, orig_w), dtype=np.uint8)
            blk_list = []
            
            class Block:
                def __init__(self, x1, y1, x2, y2, text=""):
                    self.xyxy = [x1, y1, x2, y2]
                    self._text = text
                def get_text(self):
                    return self._text
            
            inv_scale = 1.0 / scale if scale != 1.0 else 1.0
            
            for item in result:
                pts = np.array(item[0], dtype=np.int32)
                text = item[1].strip()
                score = float(item[2])
                
                # Get bounding box on downscaled image
                x, y, bw, bh = cv2.boundingRect(pts)
                
                # Discard tiny artifacts (<12px) and empty strings
                if bw < 12 or bh < 12 or len(text) == 0:
                    continue
                
                # Add 6% padding to ensure letters aren't clipped
                pad_x = int(bw * 0.06)
                pad_y = int(bh * 0.06)
                bx = max(0, x - pad_x)
                by = max(0, y - pad_y)
                bw_pad = bw + (2 * pad_x)
                bh_pad = bh + (2 * pad_y)
                
                # Scale coordinates back to original full-res image
                real_x = int(bx * inv_scale)
                real_y = int(by * inv_scale)
                real_w = int(bw_pad * inv_scale)
                real_h = int(bh_pad * inv_scale)
                
                # Ensure boxes stay within original canvas bounds
                real_x = max(0, min(orig_w - 1, real_x))
                real_y = max(0, min(orig_h - 1, real_y))
                real_w = min(orig_w - real_x, real_w)
                real_h = min(orig_h - real_y, real_h)
                
                if real_w < 12 or real_h < 12:
                    continue
                
                blk = Block(real_x, real_y, real_x + real_w, real_y + real_h, text)
                blk_list.append(blk)
                
                # Fill mask at original resolution
                mask[real_y:real_y+real_h, real_x:real_x+real_w] = 255
            
            # Dilate mask slightly
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
            mask = cv2.dilate(mask, kernel, iterations=1)
            
            logger.info(f"[RapidOCR] Successfully found {len(blk_list)} dialogue regions.")
            return mask, blk_list
            
        except Exception as e:
            logger.error(f"[RapidOCR] Detection failed: {e}")
            return np.zeros(image.shape[:2], dtype=np.uint8), []

    def _smart_inpaint(self, image: np.ndarray, mask: np.ndarray, bubbles: List[BubbleGroup], page_label: str) -> np.ndarray:
        """Step 2: Ultra-high precision inpainting with adaptive dilation and background sampling."""
        from pipeline.inpainter import SmartInpainter
        
        result = image.copy()
        smart_inpainter = SmartInpainter()

        for i, bubble in enumerate(bubbles):
            x, y, w, h = bubble.bbox

            # Clamp
            x1 = max(0, x)
            y1 = max(0, y)
            x2 = min(image.shape[1], x + w)
            y2 = min(image.shape[0], y + h)

            if x2 <= x1 or y2 <= y1:
                continue

            block_mask = mask[y1:y2, x1:x2]

            if np.sum(block_mask) == 0:
                continue

            # Use smart inpainter with adaptive dilation and background sampling
            result = smart_inpainter.inpaint(result, mask, bbox=(x1, y1, x2 - x1, y2 - y1))
            logger.debug(f"[{page_label}] Bubble {i}: Smart inpainted at ({x1},{y1}) {x2-x1}x{y2-y1}")

        logger.info(f"[{page_label}] Inpainting complete on canvas.")
        return result

    def _is_white_bubble(self, roi: np.ndarray) -> bool:
        if roi.size == 0:
            return False
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        white_ratio = np.sum(gray > 220) / gray.size
        return white_ratio > 0.7

    def _translate(self, bubbles: List[BubbleGroup], page_label: str) -> List[BubbleGroup]:
        """Step 3: Bulletproof LLM translation."""
        import httpx

        # Only translate bubbles with actual text
        to_translate = [(i, b) for i, b in enumerate(bubbles) if b.full_text.strip()]
        if not to_translate:
            logger.info(f"[{page_label}] No text to translate")
            return bubbles

        texts = [{"id": idx, "text": b.full_text} for idx, (i, b) in enumerate(to_translate)]
        prompt = json.dumps(texts, ensure_ascii=False)

        system_msg = self.system_prompt or """You are a comic translation specialist. Translate English comic text to Arabic.
Return JSON array: [{"id": 0, "translation": "Arabic text"}]
Rules: Be dramatic, concise, use comic-style Arabic. JSON only, no markdown."""

        logger.info(f"[{page_label}] Translating {len(texts)} bubbles via {self.llm_model}")

        try:
            client = httpx.Client(
                base_url=self.llm_base_url.rstrip("/") if self.llm_base_url else "https://api.orcarouter.ai/v1",
                headers={
                    "Authorization": f"Bearer {self.llm_api_key}",
                    "Content-Type": "application/json",
                },
                timeout=60.0,
            )

            response = client.post(
                "/chat/completions",
                json={
                    "model": self.llm_model or "z-ai/glm-5.3-flash-free",
                    "messages": [
                        {"role": "system", "content": system_msg},
                        {"role": "user", "content": prompt},
                    ],
                    "temperature": 0.3,
                },
            )
            response.raise_for_status()

            raw = response.json()["choices"][0]["message"]["content"]
            logger.debug(f"[{page_label}] Raw LLM response: {raw[:200]}")

            # Parse JSON
            translations = self._parse_translation_response(raw, len(texts))

            # Map back to bubbles
            for idx, (i, bubble) in enumerate(to_translate):
                if idx < len(translations):
                    bubble.translation = translations[idx]
                else:
                    bubble.translation = bubble.full_text
                    logger.warning(f"[{page_label}] Bubble {i}: Fallback to source text")

                logger.info(f"[{page_label}] Bubble {i} Source: '{bubble.full_text}' -> Arabic: '{bubble.translation}'")

        except Exception as e:
            logger.error(f"[{page_label}] Translation failed: {e}")
            for i, bubble in to_translate:
                bubble.translation = bubble.full_text
                logger.info(f"[{page_label}] Bubble {i} Fallback: '{bubble.full_text}'")

        return bubbles

    def _parse_translation_response(self, raw: str, expected_count: int) -> List[str]:
        """Parse LLM JSON response with fallback regex extraction."""
        # Try JSON parse
        try:
            cleaned = re.sub(r'```json\s*', '', raw)
            cleaned = re.sub(r'```\s*$', '', cleaned)
            cleaned = cleaned.strip()

            data = json.loads(cleaned)
            if isinstance(data, list):
                return [item.get("translation", "") for item in data]
        except json.JSONDecodeError:
            logger.warning("JSON parse failed, trying regex extraction")

        # Regex fallback
        pattern = r'"translation"\s*:\s*"([^"]*)"'
        matches = re.findall(pattern, raw)

        if matches:
            return matches

        # Last resort: return raw text split by newlines
        lines = [line.strip() for line in raw.split("\n") if line.strip()]
        return lines[:expected_count] if lines else [""] * expected_count

    def _render(self, canvas: np.ndarray, bubbles: List[BubbleGroup], page_label: str) -> np.ndarray:
        """Step 4: Studio-grade elliptical Arabic typesetting with extracted colors."""
        from PIL import Image, ImageDraw, ImageFont
        from pipeline.typesetter import ArabicTypesetter

        if not os.path.exists(self.font_path):
            logger.error(f"Font not found: {self.font_path}")
            return canvas

        typesetter = ArabicTypesetter(font_path=self.font_path)
        pil_img = Image.fromarray(cv2.cvtColor(canvas, cv2.COLOR_BGR2RGB))
        draw = ImageDraw.Draw(pil_img)

        rendered_count = 0

        for i, bubble in enumerate(bubbles):
            text = bubble.translation if bubble.translation.strip() else bubble.full_text
            if not text.strip():
                logger.info(f"[{page_label}] Bubble {i}: Empty text, skipping render")
                continue

            x, y, w, h = bubble.bbox
            if w < 15 or h < 10:
                continue

            # Use extracted text color (matches original comic style)
            text_color = bubble.text_color if bubble.text_color else (0, 0, 0)

            logger.info(f"[{page_label}] Rendering '{text[:30]}' at ({x},{y},{w},{h}) with color={text_color}")

            # Use elliptical typesetter for proper comic bubble rendering
            typesetter.render_comic_dialogue(
                draw, text, (x, y, w, h), self.font_path,
                text_color=text_color,
            )

            rendered_count += 1

        logger.info(f"[{page_label}] Rendered {rendered_count} text blocks")
        return cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)

    def _process_single_page(self, image: np.ndarray, page_label: str) -> np.ndarray:
        logger.info(f"[{page_label}] Image: {image.shape[1]}x{image.shape[0]}")

        # Step 1: Detect and group
        bubbles, mask = self._detect_and_group(image, page_label)

        if not bubbles:
            logger.info(f"[{page_label}] No bubbles detected, returning original")
            return image.copy()

        # Step 2: Smart inpaint
        cleaned = self._smart_inpaint(image, mask, bubbles, page_label)

        # Step 3: Translate
        bubbles = self._translate(bubbles, page_label)

        # Step 4: Render
        result = self._render(cleaned, bubbles, page_label)

        return result

    def process_image(self, image_path: str, output_path: Optional[str] = None, callback=None) -> str:
        img_path = Path(image_path)
        if output_path is None:
            output_path = str(img_path.parent / f"{img_path.stem}_ar{img_path.suffix}")

        image = cv2.imread(str(img_path))
        if image is None:
            raise ValueError(f"Cannot read: {image_path}")

        result = self._process_single_page(image, "Image")

        ok = cv2.imwrite(output_path, result)
        if not ok:
            raise ValueError(f"Failed to save: {output_path}")

        return output_path

    def process(self, input_path: str, output_path: str, callback=None) -> str:
        from pipeline.archive_handler import ArchiveHandler
        handler = ArchiveHandler()

        extract_dir, images = handler.extract(input_path)
        total = len(images)

        try:
            processed = []
            for i, img_path in enumerate(images):
                page = f"Page {i+1}/{total}"
                if callback:
                    callback("Processing", i + 1, total)

                image = cv2.imread(str(img_path))
                if image is None:
                    processed.append(img_path)
                    continue

                try:
                    result = self._process_single_page(image, page)
                except Exception as e:
                    logger.error(f"[{page}] Failed: {e}", exc_info=True)
                    result = image.copy()

                out = img_path.parent / f"processed_{i:04d}{img_path.suffix}"
                if cv2.imwrite(str(out), result):
                    processed.append(out)
                else:
                    processed.append(img_path)

            return handler.repackage(processed, output_path)
        finally:
            handler.cleanup(extract_dir)

    def set_model(self, model: str):
        self.llm_model = model

    def set_provider(self, base_url: str, api_key: str, model: str):
        self.llm_base_url = base_url
        self.llm_api_key = api_key
        self.llm_model = model

    def set_system_prompt(self, prompt: str):
        self.system_prompt = prompt
