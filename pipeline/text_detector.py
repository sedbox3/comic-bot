"""Text detection and bubble segmentation for comic pages."""

import cv2
import numpy as np
import logging
from dataclasses import dataclass, field
from typing import List, Tuple, Optional

logger = logging.getLogger(__name__)


@dataclass
class TextRegion:
    x: int
    y: int
    w: int
    h: int
    text: str = ""
    confidence: float = 0.0

    @property
    def bbox(self) -> Tuple[int, int, int, int]:
        return (self.x, self.y, self.w, self.h)

    @property
    def area(self) -> int:
        return self.w * self.h

    @property
    def bottom(self) -> int:
        return self.y + self.h

    @property
    def right(self) -> int:
        return self.x + self.w


@dataclass
class Bubble:
    """A grouped speech bubble containing multiple text lines."""
    x: int
    y: int
    w: int
    h: int
    texts: List[str] = field(default_factory=list)
    confidence: float = 0.0

    @property
    def bbox(self) -> Tuple[int, int, int, int]:
        return (self.x, self.y, self.w, self.h)

    @property
    def full_text(self) -> str:
        return " ".join(self.texts).strip()


def detect_bubbles(image: np.ndarray, min_area: int = 0, max_area_ratio: float = 0.25) -> List[TextRegion]:
    """
    Detect speech bubble regions in comic pages.
    Returns regions sorted top-to-bottom, left-to-right.
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image.copy()
    h, w = gray.shape[:2]
    page_area = h * w

    if min_area == 0:
        min_area = max(2000, int(page_area * 0.0015))

    logger.debug(f"Detection: {w}x{h}, min_area={min_area}")

    # Find bright regions (speech bubbles are white/light)
    _, bright = cv2.threshold(gray, 175, 255, cv2.THRESH_BINARY)

    k_open = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
    bright = cv2.morphologyEx(bright, cv2.MORPH_OPEN, k_open)

    k_close = cv2.getStructuringElement(cv2.MORPH_RECT, (20, 12))
    bright = cv2.morphologyEx(bright, cv2.MORPH_CLOSE, k_close)

    contours, _ = cv2.findContours(bright, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    regions = []
    for contour in contours:
        x, y, cw, ch = cv2.boundingRect(contour)
        area = cw * ch

        if area < min_area or area > page_area * max_area_ratio:
            continue

        aspect = max(cw, ch) / max(min(cw, ch), 1)
        if aspect > 8:
            continue

        if cw < 25 or ch < 15:
            continue

        roi = gray[y:y + ch, x:x + cw]
        bright_roi = bright[y:y + ch, x:x + cw]
        inside = bright_roi > 0
        total = np.sum(inside)
        if total == 0:
            continue

        dark_inside = np.sum((roi < 120) & inside)
        dark_ratio = dark_inside / total

        if dark_ratio > 0.03:
            regions.append(TextRegion(x=x, y=y, w=cw, h=ch))

    regions.sort(key=lambda r: (r.y, r.x))
    logger.info(f"Found {len(regions)} bubble regions")
    return regions


def group_text_lines(lines: List[TextRegion], max_gap_ratio: float = 1.5) -> List[Bubble]:
    """
    Group individual text lines into speech bubbles using spatial proximity.
    
    Rules:
    1. Lines must be vertically close (within 1.5x average line height)
    2. Lines must have horizontal overlap
    3. Lines in the same group are merged into one Bubble
    """
    if not lines:
        return []

    # Sort by y then x
    lines = sorted(lines, key=lambda r: (r.y, r.x))

    bubbles = []
    used = set()

    for i, line in enumerate(lines):
        if i in used:
            continue

        # Start a new bubble with this line
        group = [line]
        used.add(i)

        # Calculate average line height for gap threshold
        avg_h = line.h
        max_gap = int(avg_h * max_gap_ratio)

        # Find all lines that belong to this bubble
        changed = True
        while changed:
            changed = False
            for j, other in enumerate(lines):
                if j in used:
                    continue

                # Check if 'other' is close to any line in the group
                for member in group:
                    # Vertical gap
                    v_gap = abs(other.y - member.bottom) if other.y >= member.bottom else abs(member.y - other.bottom)
                    
                    # Horizontal overlap
                    overlap_x1 = max(member.x, other.x)
                    overlap_x2 = min(member.right, other.right)
                    overlap = max(0, overlap_x2 - overlap_x1)
                    min_width = min(member.w, other.w)

                    # Same bubble if: close vertically AND overlapping horizontally
                    if v_gap <= max_gap and overlap >= min_width * 0.3:
                        group.append(other)
                        used.add(j)
                        changed = True
                        break

        # Calculate merged bounding box
        x_min = min(r.x for r in group)
        y_min = min(r.y for r in group)
        x_max = max(r.right for r in group)
        y_max = max(r.bottom for r in group)

        # Merge texts in reading order (top-to-bottom, left-to-right)
        group.sort(key=lambda r: (r.y, r.x))
        texts = [r.text for r in group if r.text.strip()]

        bubbles.append(Bubble(
            x=x_min, y=y_min,
            w=x_max - x_min, h=y_max - y_min,
            texts=texts,
        ))

    bubbles.sort(key=lambda b: (b.y, b.x))
    logger.info(f"Grouped into {len(bubbles)} bubbles")
    return bubbles


def create_text_mask_from_lines(
    image_shape: tuple,
    lines: List[TextRegion],
    padding: int = 3,
    dilation: int = 3,
) -> np.ndarray:
    """
    Create mask covering ONLY the actual text strokes (not the whole bubble).
    Each text line gets its own tight mask, dilated slightly to cover edges.
    """
    h, w = image_shape[:2]
    mask = np.zeros((h, w), dtype=np.uint8)

    for line in lines:
        # Tight mask around the text line
        x1 = max(0, line.x - padding)
        y1 = max(0, line.y - padding)
        x2 = min(w, line.x + line.w + padding)
        y2 = min(h, line.y + line.h + padding)
        mask[y1:y2, x1:x2] = 255

    # Light dilation to cover anti-aliased edges
    if dilation > 0:
        k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (dilation * 2, dilation * 2))
        mask = cv2.dilate(mask, k, iterations=1)

    return mask


def create_bubble_mask(image_shape: tuple, bubbles: List[Bubble], padding: int = 3) -> np.ndarray:
    """Create mask covering text strokes within all bubbles."""
    h, w = image_shape[:2]
    mask = np.zeros((h, w), dtype=np.uint8)

    for b in bubbles:
        for text in b.texts:
            if not text.strip():
                continue
            # Estimate text line height from bubble height / number of lines
            n_lines = max(1, len(b.texts))
            line_h = b.h // n_lines
            for i in range(n_lines):
                ly = b.y + i * line_h
                x1 = max(0, b.x - padding)
                y1 = max(0, ly - padding)
                x2 = min(w, b.x + b.w + padding)
                y2 = min(h, ly + line_h + padding)
                mask[y1:y2, x1:x2] = 255

    # Light dilation
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    mask = cv2.dilate(mask, k, iterations=1)

    return mask


def detect_and_group(
    image: np.ndarray,
    ocr_results: List,
) -> List[Bubble]:
    """
    Given OCR results (with bboxes), group text lines into bubbles.
    """
    # Convert OCR results to TextRegion list
    lines = []
    for r in ocr_results:
        x, y, w, h = r.bbox
        if w < 10 or h < 10 or len(r.text.strip()) < 2:
            continue
        lines.append(TextRegion(x=x, y=y, w=w, h=h, text=r.text, confidence=r.confidence))

    logger.info(f"Input: {len(lines)} text lines")

    # Group into bubbles
    bubbles = group_text_lines(lines)

    for i, b in enumerate(bubbles):
        logger.info(f"  Bubble {i}: '{b.full_text}' at ({b.x},{b.y}) {b.w}x{b.h}")

    return bubbles
