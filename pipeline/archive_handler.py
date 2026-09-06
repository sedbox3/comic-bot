"""Archive extraction and repacking for .cbr and .cbz files."""

import os
import re
import shutil
import tempfile
import zipfile
from pathlib import Path
from typing import List, Optional

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".tiff"}


def natural_sort_key(path: Path) -> list:
    """Sort keys for natural numeric ordering (1, 2, 10 not 1, 10, 2)."""
    name = path.stem
    parts = re.split(r"(\d+)", name)
    return [int(p) if p.isdigit() else p.lower() for p in parts]


def extract_archive(archive_path: str, extract_dir: Optional[str] = None) -> str:
    """
    Extract a .cbr or .cbz archive to a temporary directory.
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

    if suffix == ".cbz":
        _extract_cbz(archive_path, extract_dir)
    elif suffix == ".cbr":
        _extract_cbr(archive_path, extract_dir)

    return extract_dir


def _extract_cbz(archive_path: Path, extract_dir: str) -> None:
    """Extract a .cbz (ZIP) archive."""
    with zipfile.ZipFile(archive_path, "r") as zf:
        zf.extractall(extract_dir)


def _extract_cbr(archive_path: Path, extract_dir: str) -> None:
    """Extract a .cbr (RAR) archive using unrar CLI or rarfile library."""
    try:
        import rarfile
        with rarfile.RarFile(str(archive_path)) as rf:
            rf.extractall(extract_dir)
    except ImportError:
        import subprocess
        result = subprocess.run(
            ["unrar", "x", "-o+", "-inul", str(archive_path), extract_dir],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            raise RuntimeError(f"unrar failed: {result.stderr}")
    except rarfile.BadRarFile:
        raise RuntimeError(f"Invalid or corrupted RAR file: {archive_path}")


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
