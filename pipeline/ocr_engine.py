"""High-precision comic OCR with preprocessing for English text."""

import cv2
import numpy as np
import logging
from typing import List, Tuple, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class ComicOCR:
    """OCR engine optimized for comic lettering with preprocessing."""

    def __init__(self):
        self._engine = None

    def _get_engine(self):
        if self._engine is None:
            try:
                from rapidocr_onnxruntime import RapidOCR
                self._engine = RapidOCR()
                logger.info("RapidOCR initialized")
            except ImportError:
                logger.error("RapidOCR not installed")
                return None
        return self._engine

    def preprocess_bubble(self, crop: np.ndarray) -> np.ndarray:
        """
        Preprocess bubble crop for better OCR:
        1. Convert to grayscale
        2. Apply CLAHE for contrast enhancement
        3. Bilateral filter to remove halftones
        4. Normalize
        """
        if crop.size == 0:
            return crop

        # Convert to grayscale
        if len(crop.shape) == 3:
            gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
        else:
            gray = crop.copy()

        # Apply CLAHE (Contrast Limited Adaptive Histogram Equalization)
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(gray)

        # Bilateral filter to remove halftones/paper grain while preserving edges
        filtered = cv2.bilateralFilter(enhanced, 9, 75, 75)

        # Normalize contrast
        normalized = cv2.normalize(filtered, None, 0, 255, cv2.NORM_MINMAX)

        # Convert back to 3-channel for RapidOCR
        return cv2.cvtColor(normalized, cv2.COLOR_GRAY2BGR)

    def expand_bbox(self, x: int, y: int, w: int, h: int, img_w: int, img_h: int, padding_pct: float = 0.06) -> Tuple[int, int, int, int]:
        """Expand bounding box by padding percentage."""
        pad_x = int(w * padding_pct)
        pad_y = int(h * padding_pct)

        x1 = max(0, x - pad_x)
        y1 = max(0, y - pad_y)
        x2 = min(img_w, x + w + pad_x)
        y2 = min(img_h, y + h + pad_y)

        return x1, y1, x2, y2

    def is_valid_text(self, text: str) -> bool:
        """
        Check if text is valid (not garbage noise).
        Preserve short comic interjections: NO!, WHEW!, HA!, etc.
        Discard pure punctuation or single non-alphabetic strokes.
        """
        text = text.strip()
        if not text:
            return False

        # If very short (1-2 chars), must contain at least one letter
        if len(text) <= 2:
            return any(c.isalpha() for c in text)

        # If longer, just needs some alpha content
        alpha_count = sum(1 for c in text if c.isalpha())
        return alpha_count >= 1

    def ocr_bubble(self, image: np.ndarray, x: int, y: int, w: int, h: int, block_id: int = 0) -> str:
        """
        Run OCR on a single bubble region with preprocessing.
        Returns merged text from all lines in reading order.
        """
        engine = self._get_engine()
        if engine is None:
            return ""

        img_h, img_w = image.shape[:2]

        # Expand bbox by 6% padding
        x1, y1, x2, y2 = self.expand_bbox(x, y, w, h, img_w, img_h, padding_pct=0.06)

        # Crop the region
        crop = image[y1:y2, x1:x2]

        if crop.size == 0:
            return ""

        # Preprocess for better OCR
        preprocessed = self.preprocess_bubble(crop)

        # Run RapidOCR
        try:
            result, _ = engine(preprocessed)
            if not result:
                return ""

            # RapidOCR returns list of (bbox, text, confidence)
            # Sort by Y-coordinate (top-to-bottom), then X-coordinate
            lines_with_pos = []
            for item in result:
                bbox_points, text, confidence = item
                if not text.strip():
                    continue

                # Get Y position from bbox (average of top points)
                if isinstance(bbox_points, (list, np.ndarray)) and len(bbox_points) >= 4:
                    # bbox_points is [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
                    y_pos = (bbox_points[0][1] + bbox_points[2][1]) / 2
                    x_pos = (bbox_points[0][0] + bbox_points[2][0]) / 2
                else:
                    y_pos = 0
                    x_pos = 0

                lines_with_pos.append((y_pos, x_pos, text.strip()))

            # Sort by Y then X (natural reading order)
            lines_with_pos.sort(key=lambda t: (t[0], t[1]))

            # Merge valid lines
            valid_lines = [text for _, _, text in lines_with_pos if self.is_valid_text(text)]

            merged = " ".join(valid_lines)
            logger.debug(f"Block {block_id}: OCR result = '{merged}'")

            return merged

        except Exception as e:
            logger.warning(f"OCR failed on block {block_id}: {e}")
            return ""

    def ocr_full_page(self, image: np.ndarray) -> List[dict]:
        """
        Run OCR on full page and return all detected text blocks.
        Returns list of dicts with 'text', 'bbox', 'confidence'.
        """
        engine = self._get_engine()
        if engine is None:
            return []

        # Preprocess full page
        preprocessed = self.preprocess_bubble(image)

        try:
            result, _ = engine(preprocessed)
            if not result:
                return []

            blocks = []
            for item in result:
                bbox_points, text, confidence = item
                if not text.strip():
                    continue

                # Extract bounding box
                if isinstance(bbox_points, (list, np.ndarray)) and len(bbox_points) >= 4:
                    xs = [p[0] for p in bbox_points]
                    ys = [p[1] for p in bbox_points]
                    x1, y1 = int(min(xs)), int(min(ys))
                    x2, y2 = int(max(xs)), int(max(ys))
                else:
                    continue

                if self.is_valid_text(text):
                    blocks.append({
                        "text": text.strip(),
                        "bbox": (x1, y1, x2 - x1, y2 - y1),
                        "confidence": confidence,
                    })

            return blocks

        except Exception as e:
            logger.warning(f"Full page OCR failed: {e}")
            return []
