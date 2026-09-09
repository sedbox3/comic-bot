"""Flask web application for comic translation."""

import os
import sys
import uuid
import shutil
import tempfile
import logging
import threading
from pathlib import Path

from flask import Flask, render_template, request, jsonify, send_file, session

# Add parent directory to path for pipeline imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import load_config
from pipeline.pipeline import ComicPipeline

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Temp directory for uploads/results
TEMP_DIR = Path(tempfile.gettempdir()) / "comic_translator"
TEMP_DIR.mkdir(exist_ok=True)

# Store user settings in memory (per-session)
user_settings = {}

# Track active jobs for background processing
active_jobs = {}
job_lock = threading.Lock()


def get_settings():
    """Get current settings from session or defaults."""
    config = load_config()
    return {
        "llm_api_key": session.get("llm_api_key", config.llm_api_key),
        "llm_base_url": session.get("llm_base_url", config.llm_base_url),
        "llm_model": session.get("llm_model", config.llm_model),
    }


def build_pipeline():
    """Build pipeline with current settings."""
    settings = get_settings()
    return ComicPipeline(
        llm_api_key=settings["llm_api_key"],
        llm_base_url=settings["llm_base_url"],
        llm_model=settings["llm_model"],
    )


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/settings")
def settings():
    current = get_settings()
    return render_template("settings.html", settings=current)


@app.route("/api/settings", methods=["POST"])
def save_settings():
    data = request.json
    if "llm_api_key" in data:
        session["llm_api_key"] = data["llm_api_key"]
    if "llm_base_url" in data:
        session["llm_base_url"] = data["llm_base_url"]
    if "llm_model" in data:
        session["llm_model"] = data["llm_model"]
    return jsonify({"status": "ok"})


@app.route("/api/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    # Validate file type
    allowed = {".cbz", ".cbr", ".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"}
    ext = Path(file.filename).suffix.lower()
    if ext not in allowed:
        return jsonify({"error": f"File type {ext} not supported"}), 400

    # Create unique job directory
    job_id = str(uuid.uuid4())[:8]
    job_dir = TEMP_DIR / job_id
    job_dir.mkdir(exist_ok=True)

    # Save uploaded file
    upload_path = job_dir / file.filename
    file.save(str(upload_path))

    logger.info(f"Uploaded: {file.filename} -> {upload_path}")

    return jsonify({
        "status": "ok",
        "job_id": job_id,
        "filename": file.filename,
    })


@app.route("/api/process/<job_id>", methods=["POST"])
def process_file(job_id):
    job_dir = TEMP_DIR / job_id
    if not job_dir.exists():
        return jsonify({"error": "Job not found"}), 404

    # Find the uploaded file
    files = list(job_dir.iterdir())
    if not files:
        return jsonify({"error": "No file found"}), 404

    input_path = files[0]
    ext = input_path.suffix.lower()

    # Check if job is already running
    with job_lock:
        if job_id in active_jobs:
            return jsonify({"error": "Job already processing"}), 409
        active_jobs[job_id] = {"status": "processing"}

    def run_pipeline():
        """Run pipeline in background thread."""
        try:
            pipeline = build_pipeline()

            if ext in {".cbz", ".cbr"}:
                output_path = str(job_dir / f"translated_{input_path.stem}.cbz")
                result = pipeline.process(str(input_path), output_path)
            else:
                output_path = str(job_dir / f"translated_{input_path.name}")
                result = pipeline.process_image(str(input_path), output_path)

            with job_lock:
                active_jobs[job_id] = {
                    "status": "completed",
                    "result_file": Path(result).name,
                }
            logger.info(f"Job {job_id} completed successfully")

        except Exception as e:
            logger.error(f"Processing failed for {job_id}: {e}", exc_info=True)
            with job_lock:
                active_jobs[job_id] = {"status": "error", "error": str(e)}

    # Start background thread
    thread = threading.Thread(target=run_pipeline, daemon=True)
    thread.start()

    return jsonify({
        "status": "started",
        "job_id": job_id,
    })


@app.route("/api/status/<job_id>")
def job_status(job_id):
    """Check job processing status."""
    with job_lock:
        if job_id not in active_jobs:
            return jsonify({"status": "unknown"})
        return jsonify(active_jobs[job_id])


@app.route("/api/download/<job_id>/<filename>")
def download_file(job_id, filename):
    job_dir = TEMP_DIR / job_id
    file_path = job_dir / filename

    if not file_path.exists():
        return jsonify({"error": "File not found"}), 404

    return send_file(
        str(file_path),
        as_attachment=True,
        download_name=filename,
    )


@app.route("/api/cleanup/<job_id>", methods=["POST"])
def cleanup_job(job_id):
    job_dir = TEMP_DIR / job_id
    if job_dir.exists():
        shutil.rmtree(str(job_dir), ignore_errors=True)
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=False)
