"""comic_engine - Comic book translation pipeline."""

from pipeline.pipeline import ComicPipeline
from pipeline.archive_handler import ArchiveHandler
from pipeline.text_detector import detect_bubbles, TextRegion
from pipeline.inpainter import Inpainter, AdvancedInpainter
from pipeline.ocr_engine import OCREngine
from pipeline.translator import LLMTranslator
from pipeline.typesetter import ArabicTypesetter

__version__ = "1.0.0"
__all__ = [
    "ComicPipeline",
    "ArchiveHandler",
    "detect_bubbles",
    "TextRegion",
    "Inpainter",
    "AdvancedInpainter",
    "OCREngine",
    "LLMTranslator",
    "ArabicTypesetter",
]
