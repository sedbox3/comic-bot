"""Telegram Bot entry point for Comic Translator."""

import os
import sys
import logging
from pathlib import Path

from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)
from telegram.request import HTTPXRequest

sys.path.insert(0, str(Path(__file__).parent.parent))

from config import load_config
from bot.handlers import (
    start_command,
    help_command,
    settings_command,
    setmodel_command,
    setprompt_command,
    reset_command,
    handle_document,
    handle_photo,
    check_subscription_callback,
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)


def main():
    config = load_config()

    if not config.telegram_token:
        print("Error: TELEGRAM_BOT_TOKEN not set in .env")
        sys.exit(1)

    # Configure robust timeouts for large images
    t_request = HTTPXRequest(
        connect_timeout=60.0,
        read_timeout=600.0,
        write_timeout=600.0,
        pool_timeout=60.0,
    )

    app = (
        ApplicationBuilder()
        .token(config.telegram_token)
        .request(t_request)
        .build()
    )

    # Commands
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("settings", settings_command))
    app.add_handler(CommandHandler("setmodel", setmodel_command))
    app.add_handler(CommandHandler("setprompt", setprompt_command))
    app.add_handler(CommandHandler("reset", reset_command))
    
    # Callback queries (subscription check button)
    app.add_handler(CallbackQueryHandler(check_subscription_callback, pattern="^check_subscription$"))

    # Photos (camera/gallery)
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    # Documents (images + comics)
    app.add_handler(MessageHandler(filters.Document.ALL, handle_document))

    logger.info("Bot starting...")
    print("Bot is running! Press Ctrl+C to stop.")

    app.run_polling(
        drop_pending_updates=True,
        timeout=120,
        poll_interval=2.0,
        allowed_updates=["message", "callback_query"],
    )


if __name__ == "__main__":
    main()
