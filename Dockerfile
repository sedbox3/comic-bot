FROM python:3.11-slim

# System dependencies (minimal for cloud free tier)
RUN apt-get update && apt-get install -y --no-install-recommends \
    unrar \
    tesseract-ocr \
    tesseract-ocr-eng \
    libgl1-mesa-glx \
    libglib2.0-0 \
    locales \
    && locale-gen en_US.UTF-8 \
    && update-locale LANG=en_US.UTF-8 \
    && rm -rf /var/lib/apt/lists/*

ENV LANG=en_US.UTF-8
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install Python dependencies first (layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir --no-compile -r requirements.txt

# Copy application code
COPY . .

# Create temp workspace
RUN mkdir -p /tmp/comic_work

# Health check for PaaS providers
HEALTHCHECK --interval=60s --timeout=10s --retries=3 \
    CMD python -c "from telegram import Bot; print('ok')" || exit 1

# Run the Telegram bot
CMD ["python", "-m", "bot.main"]
