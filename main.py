"""Comic Translator CLI — Translate comics from English to Arabic."""

import sys
import argparse
import cv2
from pathlib import Path

try:
    from rich.console import Console
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
    from rich.panel import Panel
    from rich import print as rprint
    HAS_RICH = True
except ImportError:
    HAS_RICH = False

from config import load_config
from pipeline.pipeline import ComicPipeline


def progress_callback_factory(console=None):
    """Create a progress callback for the pipeline."""
    if HAS_RICH and console:
        progress = Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=console,
        )
        task_id = None

        def callback(phase: str, current: int, total: int):
            nonlocal task_id
            if task_id is None and total > 0:
                task_id = progress.add_task(phase, total=total)
            if task_id is not None:
                progress.update(task_id, description=phase, completed=current)
                if current == total and total > 0:
                    progress.stop()
        return callback, progress
    else:
        def callback(phase: str, current: int, total: int):
            if total > 0:
                print(f"  [{phase}] {current}/{total}")
            else:
                print(f"  [{phase}]...")
        return callback, None


def main():
    parser = argparse.ArgumentParser(
        description="Comic Translator — Translate English comics to Arabic",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py translate comic.cbz
  python main.py translate comic.cbz -o translated.cbz
  python main.py translate comic.cbr --model google/gemini-2.0-flash-exp:free
  python main.py info comic.cbz
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Translate command
    translate_parser = subparsers.add_parser("translate", help="Translate a comic archive")
    translate_parser.add_argument("input", help="Path to .cbr or .cbz file")
    translate_parser.add_argument("-o", "--output", help="Output .cbz path (default: input_translated.cbz)")
    translate_parser.add_argument("--model", help="LLM model name (overrides .env)")
    translate_parser.add_argument("--api-key", help="LLM API key (overrides .env)")
    translate_parser.add_argument("--base-url", help="LLM API base URL (overrides .env)")
    translate_parser.add_argument("--ocr", choices=["tesseract", "easyocr"], help="OCR backend")
    translate_parser.add_argument("--inpaint", choices=["ns", "telea"], help="Inpainting method")
    translate_parser.add_argument("--font", help="Path to Arabic TTF font")
    translate_parser.add_argument("--prompt", help="Custom translation system prompt")

    # Info command
    info_parser = subparsers.add_parser("info", help="Show info about a comic archive")
    info_parser.add_argument("input", help="Path to .cbr or .cbz file")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    config = load_config()

    if HAS_RICH:
        console = Console()
        console.print(Panel.fit(
            "[bold cyan]Comic Translator[/bold cyan]\n"
            "[dim]English to Arabic comic localization pipeline[/dim]",
            border_style="blue",
        ))
    else:
        console = None
        print("=== Comic Translator ===")

    if args.command == "translate":
        _handle_translate(args, config, console)
    elif args.command == "info":
        _handle_info(args, console)


def _handle_translate(args, config, console):
    """Handle the translate command."""
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: File not found: {input_path}")
        sys.exit(1)

    if input_path.suffix.lower() not in (".cbz", ".cbr"):
        print(f"Error: Unsupported format: {input_path.suffix}. Use .cbr or .cbz")
        sys.exit(1)

    output_path = args.output or str(input_path.with_name(input_path.stem + "_translated.cbz"))

    # Build pipeline with overrides
    pipeline = ComicPipeline(
        ocr_backend=args.ocr or config.ocr_backend,
        inpaint_method=args.inpaint or config.inpaint_method,
        font_path=args.font or config.font_path or None,
        llm_api_key=args.api_key or config.llm_api_key,
        llm_base_url=args.base_url or config.llm_base_url,
        llm_model=args.model or config.llm_model,
        system_prompt=args.prompt or config.system_prompt or None,
    )

    if not config.llm_api_key and not args.api_key:
        print("Error: No API key configured. Set LLM_API_KEY in .env or use --api-key")
        sys.exit(1)

    if HAS_RICH and console:
        console.print(f"\n[green]Input:[/green]  {input_path}")
        console.print(f"[green]Output:[/green] {output_path}")
        console.print(f"[green]Model:[/green]  {args.model or config.llm_model}")
        console.print()

    callback, progress = progress_callback_factory(console)

    try:
        if progress:
            with progress:
                result = pipeline.process(str(input_path), output_path, callback=callback)
        else:
            result = pipeline.process(str(input_path), output_path, callback=callback)

        if HAS_RICH and console:
            console.print(f"\n[bold green]Done![/bold green] Output saved to: {result}")
        else:
            print(f"\nDone! Output saved to: {result}")

    except Exception as e:
        if HAS_RICH and console:
            console.print(f"\n[bold red]Error:[/bold red] {e}")
        else:
            print(f"\nError: {e}")
        sys.exit(1)


def _handle_info(args, console):
    """Handle the info command."""
    from pipeline.archive_handler import ArchiveHandler

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: File not found: {input_path}")
        sys.exit(1)

    handler = ArchiveHandler()
    try:
        extract_dir, images = handler.extract(str(input_path))
        if HAS_RICH and console:
            console.print(f"\n[bold]Archive Info:[/bold]")
            console.print(f"  File: {input_path.name}")
            console.print(f"  Format: {input_path.suffix}")
            console.print(f"  Pages: {len(images)}")
            if images:
                sample = cv2.imread(str(images[0]))
                if sample is not None:
                    console.print(f"  Page size: {sample.shape[1]}x{sample.shape[0]}")
        else:
            print(f"Archive: {input_path.name}")
            print(f"Format: {input_path.suffix}")
            print(f"Pages: {len(images)}")
    finally:
        handler.cleanup(extract_dir)


if __name__ == "__main__":
    main()
