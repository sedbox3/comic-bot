"""Archive extraction and repacking for .cbr and .cbz files."""

import os
import re
import shutil
import tempfile
import zipfile
import logging
from pathlib import Path
from typing import List, Optional

logger = logging.getLogger(__name__)

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".tiff"}

# Configure unrar executable path if rarfile is used on Windows
try:
    import rarfile
    for tool_path in [
        r"C:\Program Files\WinRAR\UnRAR.exe",
        r"C:\Program Files\7-Zip\7z.exe",
        r"C:\Program Files (x86)\WinRAR\UnRAR.exe"
    ]:
        if os.path.exists(tool_path):
            rarfile.UNRAR_TOOL = tool_path
            break
except ImportError:
    rarfile = None


def natural_sort_key(path: Path) -> list:
    """Sort keys for natural numeric ordering (1, 2, 10 not 1, 10, 2)."""
    name = path.stem
    parts = re.split(r"(\d+)", name)
    return [int(p) if p.isdigit() else p.lower() for p in parts]


def extract_archive(archive_path: str, extract_dir: Optional[str] = None) -> str:
    """
    Extract a .cbr or .cbz archive to a temporary directory.
    Uses magic bytes to detect actual format, with fallback chain.
    Returns the path to the extracted directory containing sorted image files.
    """
    archive_path = Path(archive_path)
    if not archive_path.exists():
        raise FileNotFoundError(f"Archive not found: {archive_path}")

    suffix = archive_path.suffix.lower()
    if suffix not in (".cbz", ".cbr"):
        raise ValueError(f"Unsupported archive format: {suffix}. Use .cbr or .cbz")

    if extract_dir is None:
        extract_dir = tempfile.mkdtemp(prefix="comic_extract_")
    else:
        os.makedirs(extract_dir, exist_ok=True)

    # 1. Inspect file header magic bytes
    with open(archive_path, 'rb') as f:
        magic = f.read(7)

    is_zip_magic = magic.startswith(b"PK\x03\x04")
    is_rar_magic = magic.startswith(b"Rar!\x1a\x07\x00") or magic.startswith(b"Rar!\x1a\x07\x01\x00")

    # 2. Preferred extraction based on magic header
    if is_zip_magic:
        try:
            return _extract_zip(archive_path, extract_dir)
        except Exception as e:
            logger.warning(f"ZIP extraction failed despite magic header: {e}. Trying RAR fallback...")

    if is_rar_magic:
        try:
            return _extract_rar(archive_path, extract_dir)
        except Exception as e:
            logger.warning(f"RAR extraction failed despite magic header: {e}. Trying ZIP fallback...")

    # 3. Fallback Chain: Try ZipFile first (handles misnamed CBRs), then RarFile
    try:
        return _extract_zip(archive_path, extract_dir)
    except (zipfile.BadZipFile, Exception):
        pass

    try:
        return _extract_rar(archive_path, extract_dir)
    except Exception as e:
        raise ValueError(f"Could not extract '{archive_path.name}'. File is neither a valid ZIP nor RAR archive: {e}")


def _extract_zip(archive_path: Path, extract_dir: str) -> str:
    """Extract a ZIP archive."""
    with zipfile.ZipFile(archive_path, "r") as zf:
        zf.extractall(extract_dir)
    logger.info(f"[Archive] Successfully extracted ZIP container: {archive_path.name}")
    return extract_dir


def _extract_rar(archive_path: Path, extract_dir: str) -> str:
    """Extract a RAR archive."""
    if rarfile is None:
        raise ImportError("`rarfile` package is required to extract RAR archives.")
    with rarfile.RarFile(str(archive_path), 'r') as rf:
        rf.extractall(extract_dir)
    logger.info(f"[Archive] Successfully extracted RAR container: {archive_path.name}")
    return extract_dir


def get_sorted_images(extract_dir: str) -> List[Path]:
    """Return image files from extract_dir sorted in natural order."""
    extract_path = Path(extract_dir)
    images = [
        p
        for p in extract_path.rglob("*")
        if p.is_file() and p.suffix.lower() in IMAGE_EXTENSIONS
    ]
    images.sort(key=natural_sort_key)
    return images


def repack_cbz(image_files: List[Path], output_path: str, compress: bool = True) -> str:
    """
    Repack a list of image files into a .cbz archive.
    Returns the path to the created .cbz file.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    compression = zipfile.ZIP_DEFLATED if compress else zipfile.ZIP_STORED

    with zipfile.ZipFile(str(output_path), "w", compression=compression) as zf:
        for img in image_files:
            arcname = img.name
            zf.write(str(img), arcname)

    return str(output_path)


def cleanup_dir(dir_path: str) -> None:
    """Safely remove a temporary directory."""
    if os.path.isdir(dir_path):
        shutil.rmtree(dir_path, ignore_errors=True)


class ArchiveHandler:
    """High-level interface for comic archive processing."""

    def __init__(self, temp_base: Optional[str] = None):
        self.temp_base = temp_base

    def extract(self, archive_path: str) -> tuple:
        """Extract archive, return (extract_dir, sorted_image_paths)."""
        extract_dir = extract_archive(archive_path, self.temp_base)
        images = get_sorted_images(extract_dir)
        if not images:
            raise ValueError(f"No images found in archive: {archive_path}")
        return extract_dir, images

    def repackage(
        self, processed_images: List[Path], output_path: str, compress: bool = True
    ) -> str:
        """Repackage processed images into a .cbz file."""
        return repack_cbz(processed_images, output_path, compress)

    @staticmethod
    def cleanup(dir_path: str) -> None:
        cleanup_dir(dir_path)
