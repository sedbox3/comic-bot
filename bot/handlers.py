"""Telegram bot handlers for comic translation."""

import os
import shutil
import tempfile
import asyncio
from pathlib import Path
from typing import Dict

from telegram import Update, BotCommand, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)
from telegram.constants import ParseMode, ChatAction, ChatMemberStatus

from config import load_config
from pipeline.pipeline import ComicPipeline
from pipeline.translator import LLMTranslator

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"}
COMIC_EXTENSIONS = {".cbz", ".cbr"}

CHANNEL_USERNAME = "sedbox3"
CHANNEL_URL = f"https://t.me/{CHANNEL_USERNAME}"

user_settings: Dict[int, dict] = {}


def get_user_settings(user_id: int) -> dict:
    if user_id not in user_settings:
        config = load_config()
        user_settings[user_id] = {
            "model": config.llm_model,
            "base_url": config.llm_base_url,
            "api_key": config.llm_api_key,
            "system_prompt": "",
            "font_path": config.font_path,
        }
    return user_settings[user_id]


def build_pipeline(user_id: int) -> ComicPipeline:
    settings = get_user_settings(user_id)
    return ComicPipeline(
        font_path=settings["font_path"] or None,
        llm_api_key=settings["api_key"],
        llm_base_url=settings["base_url"],
        llm_model=settings["model"],
        system_prompt=settings["system_prompt"] or None,
    )


async def check_subscription(user_id: int, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Check if user is subscribed to the channel."""
    try:
        member = await context.bot.get_chat_member(chat_id=f"@{CHANNEL_USERNAME}", user_id=user_id)
        return member.status in [ChatMemberStatus.MEMBER, ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR]
    except Exception:
        return False


def get_phase_ar(phase: str) -> str:
    return {
        "Extracting": "جاري الاستخراج",
        "Processing": "جاري المعالجة",
        "Repackaging": "جاري إعادة التعبئة",
        "Loading image": "جاري تحميل الصورة",
        "Detecting text": "جاري كشف النصوص",
        "Removing text": "جاري إزالة النصوص",
        "Extracting text": "جاري استخراج النص",
        "Translating": "جاري الترجمة",
        "Rendering Arabic": "جاري كتابة النص العربي",
        "Saving": "جاري الحفظ",
    }.get(phase, phase)


def make_progress_bar(current: int, total: int) -> str:
    """Create a visual progress bar."""
    if total <= 0:
        return ""
    
    bar_length = 10
    filled = int(bar_length * current / total)
    empty = bar_length - filled
    
    bar = "█" * filled + "░" * empty
    percent = int(100 * current / total)
    
    return f"\n{bar} {percent}% ({current}/{total})"


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    is_subscribed = await check_subscription(update.effective_user.id, context)
    
    if not is_subscribed:
        keyboard = [
            [InlineKeyboardButton("اشترك في القناة", url=CHANNEL_URL)],
            [InlineKeyboardButton("تحقق", callback_data="check_subscription")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "مرحباً! لل использования، يجب أن تكون مشتركاً في قناتنا\n\n"
            "1. اشترك في القناة أولاً\n"
            "2. اضغط 'تحقق' للتأكيد",
            reply_markup=reply_markup
        )
        return
    
    await show_main_menu(update, context)


async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "مرحباً! أنا بوت ترجمة الكوميكس والصور\n\n"
        "أرسل لي:\n"
        "- ملف `.cbz` أو `.cbr` (كوميكس كامل)\n"
        "- صورة `.jpg` أو `.png` (صفحة مفردة)\n"
        "- صورة مباشرة من الكاميرا\n\n"
        "وسأترجم النصوص للعربية تلقائياً!\n\n"
        "**الأوامر:**\n"
        "/setmodel <model> — تغيير النموذج\n"
        "/setprompt <prompt> — تغيير برومبت الترجمة\n"
        "/settings — عرض الإعدادات\n"
        "/reset — إعادة تعيين",
        parse_mode=ParseMode.MARKDOWN,
    )


async def check_subscription_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the check subscription button."""
    query = update.callback_query
    await query.answer()
    
    is_subscribed = await check_subscription(query.from_user.id, context)
    
    if is_subscribed:
        await query.edit_message_text("تم التحقق بنجاح! أرسل صورة أو ملف كوميكس للبدء")
    else:
        await query.edit_message_text(
            "لم يتم الاشتراك بعد. اشترك في القناة ثم اضغط 'تحقق' مرة أخرى",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("اشترك في القناة", url=CHANNEL_URL)],
                [InlineKeyboardButton("تحقق", callback_data="check_subscription")]
            ])
        )


async def settings_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    settings = get_user_settings(update.effective_user.id)
    await update.message.reply_text(
        f"**الإعدادات الحالية:**\n\n"
        f"النموذج: `{settings['model']}`\n"
        f"المزود: `{settings['base_url']}`\n"
        f"البرومبت: {'مخصص' if settings['system_prompt'] else 'افتراضي'}",
        parse_mode=ParseMode.MARKDOWN,
    )


async def setmodel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text(
            "الاستخدام: `/setmodel <model>`\n"
            "مثال: `/setmodel google/gemini-2.0-flash-exp:free`",
            parse_mode=ParseMode.MARKDOWN,
        )
        return
    model = " ".join(context.args)
    settings = get_user_settings(update.effective_user.id)
    settings["model"] = model
    await update.message.reply_text(f"تم تغيير النموذج إلى: `{model}`", parse_mode=ParseMode.MARKDOWN)


async def setprompt_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text(
            "الاستخدام: `/setprompt <text>`\n"
            "مثال: `/setprompt Translate to Egyptian Arabic`",
            parse_mode=ParseMode.MARKDOWN,
        )
        return
    prompt = " ".join(context.args)
    settings = get_user_settings(update.effective_user.id)
    settings["system_prompt"] = prompt
    await update.message.reply_text("تم تحديث برومبت الترجمة")


async def reset_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_settings.pop(update.effective_user.id, None)
    await update.message.reply_text("تم إعادة تعيين جميع الإعدادات")


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle photos sent directly (camera/gallery) with translation."""
    if not update.message.photo:
        return
    
    # Check subscription
    is_subscribed = await check_subscription(update.effective_user.id, context)
    if not is_subscribed:
        keyboard = [
            [InlineKeyboardButton("اشترك في القناة", url=CHANNEL_URL)],
            [InlineKeyboardButton("تحقق", callback_data="check_subscription")]
        ]
        await update.message.reply_text(
            "يجب أن تكون مشتركاً في القناة لاستخدام البوت",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    status_msg = await update.message.reply_text("جاري تحميل الصورة...")
    work_dir = tempfile.mkdtemp(prefix="tg_img_")
    input_path = os.path.join(work_dir, "input.jpg")
    output_path = os.path.join(work_dir, "output.jpg")

    try:
        await update.message.chat.send_action(ChatAction.UPLOAD_PHOTO)
        photo = update.message.photo[-1]
        file = await photo.get_file()
        await file.download_to_drive(input_path)

        await status_msg.edit_text("تم التحميل - جاري كشف النصوص...")

        pipeline = build_pipeline(update.effective_user.id)
        settings = get_user_settings(update.effective_user.id)

        def sync_cb(phase, current, total):
            try:
                loop = asyncio.get_event_loop()
                text = get_phase_ar(phase)
                if total > 0:
                    text += make_progress_bar(current, total)
                loop.call_soon_threadsafe(asyncio.ensure_future, status_msg.edit_text(text))
            except Exception:
                pass

        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, lambda: pipeline.process_image(input_path, output_path, callback=sync_cb))

        if not os.path.exists(result):
            await status_msg.edit_text("لم يتم العثور على نص في الصورة")
            return

        await status_msg.edit_text("تم الترجمة! جاري الإرسال...")
        with open(result, "rb") as f:
            await update.message.reply_photo(photo=f, caption=f"النموذج: {settings['model']}")
        await status_msg.delete()

    except Exception as e:
        import traceback
        traceback.print_exc()
        try:
            await status_msg.edit_text(f"خطأ في المعالجة:\n{str(e)[:300]}")
        except Exception:
            pass
    finally:
        shutil.rmtree(work_dir, ignore_errors=True)


async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle all documents: .cbz/.cbr comics AND .jpg/.png images."""
    document = update.message.document
    if not document:
        return
    
    # Check subscription
    is_subscribed = await check_subscription(update.effective_user.id, context)
    if not is_subscribed:
        keyboard = [
            [InlineKeyboardButton("اشترك في القناة", url=CHANNEL_URL)],
            [InlineKeyboardButton("تحقق", callback_data="check_subscription")]
        ]
        await update.message.reply_text(
            "يجب أن تكون مشتركاً في القناة لاستخدام البوت",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    file_name = document.file_name or ""
    suffix = Path(file_name).suffix.lower()

    if suffix in COMIC_EXTENSIONS:
        await _process_comic(update, context, document, file_name, suffix)
    elif suffix in IMAGE_EXTENSIONS:
        await _process_image_doc(update, context, document, file_name, suffix)
    else:
        await update.message.reply_text(
            f"صيغة غير مدعومة: `{suffix}`\nأرسل صورة أو ملف `.cbz`/`.cbr`",
            parse_mode=ParseMode.MARKDOWN,
        )


async def _process_comic(update, context, document, file_name, suffix):
    """Process .cbz/.cbr comic archives."""
    max_size = 50 * 1024 * 1024
    if document.file_size and document.file_size > max_size:
        await update.message.reply_text(f"الملف كبير جداً ({document.file_size // 1024 // 1024}MB). الحد 50MB")
        return

    status_msg = await update.message.reply_text("جاري تحميل الملف...")
    work_dir = tempfile.mkdtemp(prefix="tg_comic_")
    input_path = os.path.join(work_dir, file_name)
    output_name = Path(file_name).stem + "_ar.cbz"
    output_path = os.path.join(work_dir, output_name)

    try:
        await update.message.chat.send_action(ChatAction.UPLOAD_DOCUMENT)
        file = await document.get_file()
        await file.download_to_drive(input_path)
        await status_msg.edit_text("تم التحميل - جاري المعالجة...")

        pipeline = build_pipeline(update.effective_user.id)
        settings = get_user_settings(update.effective_user.id)

        def sync_cb(phase, current, total):
            try:
                loop = asyncio.get_event_loop()
                text = get_phase_ar(phase)
                if total > 0:
                    text += make_progress_bar(current, total)
                loop.call_soon_threadsafe(asyncio.ensure_future, status_msg.edit_text(text))
            except Exception:
                pass

        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, lambda: pipeline.process(input_path, output_path, callback=sync_cb))

        if not os.path.exists(result):
            await status_msg.edit_text("حدث خطأ أثناء المعالجة")
            return

        await status_msg.edit_text("تم الترجمة! جاري الإرسال...")
        output_size = os.path.getsize(result)
        with open(result, "rb") as f:
            await update.message.reply_document(
                document=f,
                filename=output_name,
                caption=f"ترجمة مكتملة\nالنموذج: {settings['model']}\nالحجم: {output_size // 1024}KB",
                write_timeout=600.0,
                read_timeout=600.0,
                connect_timeout=120.0
            )
        await status_msg.delete()

    except Exception as e:
        import traceback
        traceback.print_exc()
        try:
            await status_msg.edit_text(f"خطأ في المعالجة:\n{str(e)[:300]}")
        except Exception:
            pass
    finally:
        shutil.rmtree(work_dir, ignore_errors=True)


async def _process_image_doc(update, context, document, file_name, suffix):
    """Process image files sent as documents with translation."""
    max_size = 20 * 1024 * 1024
    if document.file_size and document.file_size > max_size:
        await update.message.reply_text("الصورة كبيرة جداً. الحد 20MB")
        return

    status_msg = await update.message.reply_text("جاري تحميل الصورة...")
    work_dir = tempfile.mkdtemp(prefix="tg_img_")
    input_path = os.path.join(work_dir, file_name)
    output_name = Path(file_name).stem + "_ar.jpg"
    output_path = os.path.join(work_dir, output_name)

    try:
        await update.message.chat.send_action(ChatAction.UPLOAD_PHOTO)
        file = await document.get_file()
        await file.download_to_drive(input_path)
        await status_msg.edit_text("تم التحميل - جاري المعالجة...")

        pipeline = build_pipeline(update.effective_user.id)
        settings = get_user_settings(update.effective_user.id)

        def sync_cb(phase, current, total):
            try:
                loop = asyncio.get_event_loop()
                loop.call_soon_threadsafe(asyncio.ensure_future, status_msg.edit_text(get_phase_ar(phase)))
            except Exception:
                pass

        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, lambda: pipeline.process_image(input_path, output_path, callback=sync_cb))

        if not os.path.exists(result):
            await status_msg.edit_text("لم يتم العثور على نص في الصورة")
            return

        await status_msg.edit_text("تم الترجمة! جاري الإرسال...")
        with open(result, "rb") as f:
            await update.message.reply_photo(photo=f, caption=f"النموذج: {settings['model']}")
        await status_msg.delete()

    except Exception as e:
        import traceback
        traceback.print_exc()
        try:
            await status_msg.edit_text(f"خطأ في المعالجة:\n{str(e)[:300]}")
        except Exception:
            pass
    finally:
        shutil.rmtree(work_dir, ignore_errors=True)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "**كيفية الاستخدام:**\n\n"
        "أرسل أي من:\n"
        "- صورة مباشرة (Camera/Photo)\n"
        "- ملف صورة `.jpg` `.png`\n"
        "- ملف كوميكس `.cbz` `.cbr`\n\n"
        "وسأترجم النصوص للعربية تلقائياً!\n\n"
        "**الأوامر:**\n"
        "/start — البدء\n"
        "/settings — الإعدادات\n"
        "/setmodel <model> — تغيير النموذج\n"
        "/setprompt <text> — تغيير البرومبت\n"
        "/reset — إعادة تعيين\n"
        "/help — المساعدة",
        parse_mode=ParseMode.MARKDOWN,
    )
