"""Studio-grade elliptical Arabic typesetting for comic speech bubbles."""

from __future__ import annotations
import os
import math
import cv2
import numpy as np
import logging
from typing import Tuple, Optional, List, Any
from pathlib import Path

logger = logging.getLogger(__name__)

try:
    import arabic_reshaper
    from bidi.algorithm import get_display
    HAS_ARABIC = True
except ImportError:
    HAS_ARABIC = False
    logger.error("arabic-reshaper/python-bidi NOT INSTALLED!")

try:
    from PIL import Image, ImageDraw, ImageFont
    Font = ImageFont.FreeTypeFont
    HAS_PIL = True
except ImportError:
    HAS_PIL = False
    logger.error("Pillow NOT INSTALLED!")


class ArabicTypesetter:
    """Studio-grade Arabic typesetting with proportional auto-fit."""

    def __init__(
        self,
        font_path: Optional[str] = None,
        default_size: int = 36,
        min_size: int = 16,
        max_size: int = 56,
        line_spacing: float = 1.25,
        text_color: Tuple[int, int, int] = (0, 0, 0),
    ):
        self.font_path = font_path or self._find_font()
        self.default_size = default_size
        self.min_size = min_size
        self.max_size = max_size
        self.line_spacing = line_spacing
        self.text_color = text_color

        if not self.font_path or not os.path.exists(self.font_path):
            logger.error(f"Arabic font NOT FOUND: {self.font_path}")
        else:
            logger.info(f"Arabic font: {self.font_path}")

    def _find_font(self) -> str:
        """Find Arabic font - prefer Hayah comic font."""
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        # Primary: Hayah comic font
        hayah_path = os.path.join(base_dir, "fonts", "Hayah.ttf")
        if os.path.exists(hayah_path):
            return hayah_path

        # Case-insensitive fallback
        hayah_lower = os.path.join(base_dir, "fonts", "hayah.ttf")
        if os.path.exists(hayah_lower):
            return hayah_lower

        # Fallback to NotoSans
        noto_path = os.path.join(base_dir, "fonts", "NotoSansArabic-Regular.ttf")
        if os.path.exists(noto_path):
            return noto_path

        # System fonts
        candidates = [
            "C:/Windows/Fonts/arial.ttf",
            "C:/Windows/Fonts/tahoma.ttf",
        ]
        for p in candidates:
            if os.path.exists(p):
                return p
        return ""

    def fit_text_to_bubble(self, text: str, bw: int, bh: int) -> Tuple[Optional[Font], List[str]]:
        """
        Find optimal font size that fills 60-75% of bubble without spilling.
        Large bubbles get large fonts, small bubbles get smaller fonts.
        """
        words = text.strip().replace("\n", " ").split()
        if not words:
            return None, []

        # Calculate safe inner dimensions (18% padding from borders)
        safe_w = int(bw * 0.82)
        safe_h = int(bh * 0.82)

        # Dynamic search range based on bubble height - larger factor for bigger text
        max_font_size = min(self.max_size, max(self.min_size, int(bh * 0.40)))
        min_font_size = self.min_size

        best_font = None
        best_lines = []

        # Step-down search for optimal fill
        for size in range(max_font_size, min_font_size - 1, -2):
            font = ImageFont.truetype(self.font_path, size)
            sample_bbox = font.getbbox("أبجA")
            line_height = int((sample_bbox[3] - sample_bbox[1]) * self.line_spacing)

            # Simple greedy wrap within safe_w
            lines = []
            cur_line = []
            overflow = False

            for word in words:
                test_line = " ".join(cur_line + [word])
                reshaped = get_display(arabic_reshaper.reshape(test_line))
                tw = font.getbbox(reshaped)[2] - font.getbbox(reshaped)[0]

                if tw <= safe_w:
                    cur_line.append(word)
                else:
                    if cur_line:
                        lines.append(" ".join(cur_line))
                        cur_line = [word]
                    else:
                        # Single word is wider than safe width -> font is too large
                        overflow = True
                        break

            if cur_line:
                lines.append(" ".join(cur_line))

            if overflow:
                continue

            total_h = len(lines) * line_height

            # Check vertical fit
            if total_h <= safe_h:
                best_font = font
                best_lines = lines
                logger.debug(f"Font size {size} fits: {len(lines)} lines, total_h={total_h}, safe_h={safe_h}")
                break

        # Fallback to minimum if text is very long
        if not best_font:
            best_font = ImageFont.truetype(self.font_path, min_font_size)
            sample_bbox = best_font.getbbox("أبجA")
            line_height = int((sample_bbox[3] - sample_bbox[1]) * self.line_spacing)

            best_lines = []
            cur_line = []
            for word in words:
                test = " ".join(cur_line + [word])
                tw = best_font.getbbox(get_display(arabic_reshaper.reshape(test)))[2] - best_font.getbbox(get_display(arabic_reshaper.reshape(test)))[0]
                if tw <= safe_w:
                    cur_line.append(word)
                else:
                    if cur_line:
                        best_lines.append(" ".join(cur_line))
                    cur_line = [word]
            if cur_line:
                best_lines.append(" ".join(cur_line))

        return best_font, best_lines

    def render_comic_dialogue(self, draw, text: str, box: Tuple[int, int, int, int], font_path: str, text_color: Tuple[int, int, int] = (0, 0, 0)):
        """
        Render Arabic text in a speech bubble with proportional auto-fit.
        box: (x, y, w, h) bounding box of the speech bubble
        """
        bx, by, bw, bh = box
        bubble_cx = bx + bw / 2
        bubble_cy = by + bh / 2

        font, lines = self.fit_text_to_bubble(text, bw, bh)
        if not font or not lines:
            return

        sample_bbox = font.getbbox("أبجA")
        line_h = int((sample_bbox[3] - sample_bbox[1]) * self.line_spacing)
        total_h = len(lines) * line_h

        # Centered top-down rendering
        current_y = int(bubble_cy - (total_h / 2))

        # Safety: clamp to bubble bounds
        max_y = by + bh - total_h - 5
        min_y = by + 5
        if current_y > max_y:
            current_y = max_y
        if current_y < min_y:
            current_y = min_y

        for line in lines:
            reshaped = arabic_reshaper.reshape(line)
            bidi_line = get_display(reshaped)
            draw.text(
                (bubble_cx, current_y),
                bidi_line,
                font=font,
                fill=text_color,
                anchor="mt"
            )
            current_y += line_h

    def render_page(self, image: np.ndarray, texts: List[dict], bboxes: List[Tuple[int, int, int, int]]) -> np.ndarray:
        """Render multiple text blocks onto an image."""
        if not HAS_PIL:
            return image

        result = image.copy()
        pil_img = Image.fromarray(cv2.cvtColor(result, cv2.COLOR_BGR2RGB))
        draw = ImageDraw.Draw(pil_img)

        for text_data, bbox in zip(texts, bboxes):
            translated = text_data.get("translation", text_data.get("text", ""))
            if translated.strip():
                self.render_comic_dialogue(
                    draw, translated, bbox, self.font_path,
                    text_color=self.text_color,
                )

        return cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
