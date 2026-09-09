"""Pipeline modules for comic translation."""

from pipeline.archive_handler import ArchiveHandler
from pipeline.pipeline import ComicPipeline, BubbleGroup, DetectionError

__all__ = [
    "ArchiveHandler",
    "ComicPipeline",
    "BubbleGroup",
    "DetectionError",
]
