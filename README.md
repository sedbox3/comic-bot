# Comic Translator Bot — ترجمة الكوميكس عربي

بوت Telegram مجاني يترجم كوميكس الإنجليزية إلى العربية بجودة احترافية.

## المميزات

- ترجمة `.cbz` و`.cbr` تلقائياً
- كشف فقاعات الكلام وإزالة النصوص (Inpainting)
- OCR لاستخراج النصوص
- ترجمة عبر نماذج LLM مجانية (OrcaRouter, Gemini, Groq)
- عرض عربي احترافي مع RTL reshaping
- تحديثات تقدم مباشرة في التليجرام

---

## الخطوة 1: إنشاء بوت Telegram

1. افتح Telegram وابحث عن **@BotFather**
2. أرسل `/newbot`
3. اختر اسم للبوت (مثال: `Comic Translator Bot`)
4. اختر username فريد (مثال: `my_comic_translator_bot`)
5. ستحصل على **token** — احفظه!

## الخطوة 2: الحصول على مفتاح API مجاني

### OrcaRouter (موصى به)
1. اذهب إلى [orcarouter.ai](https://orcarouter.ai)
2. سجّل حساب مجاني
3. اذهب إلى **Keys** → **Create Key**
4. انسخ المفتاح

### Google Gemini (بديل)
1. اذهب إلى [aistudio.google.com](https://aistudio.google.com/apikey)
2. أنشئ مفتاح مجاني

## الخطوة 3: إعداد المشروع

```bash
# استنساخ المشروع
git clone <your-repo-url>
cd comic-translator

# إعداد ملف .env
cp .env.example .env
```

عدّل ملف `.env`:
```env
TELEGRAM_BOT_TOKEN=توكن-البوت-من-BotFather
LLM_API_KEY=مفتاح-OrcaRouter
LLM_BASE_URL=https://api.orcarouter.ai/v1
LLM_MODEL=z-ai/glm-5.3-flash-free
```

## الخطوة 4: النشر المجاني 24/7

### الخيار أ: Koyeb (مجاني 100%)

1. أنشئ حساب على [koyeb.com](https://www.koyeb.com)
2. اضغط **Create App** → **Docker**
3. اربط مستودع GitHub الخاص بك
4. اضبط الإعدادات:
   - **Port**: `8080` (أو أي порт)
   - **Environment Variables**: أضف متغيرات `.env`
5. اضغط **Deploy**

**ملاحظة**: Koyeb يحتاج web server للـ health check. أضف هذا الكود في `bot/main.py`:

```python
from aiohttp import web

async def health_check(request):
    return web.Response(text="ok")

# أضف في main() بعد إنشاء app:
web_app = web.Application()
web_app.router.add_get("/", health_check)
web_app.router.add_get("/health", health_check)
runner = web.AppRunner(web_app)
await runner.setup()
site = web.TCPSite(runner, "0.0.0.0", 8080)
await site.start()
```

### الخيار ب: Render (مجاني)

1. أنشئ حساب على [render.com](https://render.com)
2. اضغط **New** → **Background Worker**
3. اربط مستودع GitHub
4. اضبط:
   - **Runtime**: Docker
   - **Environment Variables**: أضف `.env` variables
5. اضغط **Create Background Worker**

### الخيار ج: Railway (مجاني للبداية)

1. أنشئ حساب على [railway.app](https://railway.app)
2. اضغط **New Project** → **Deploy from GitHub**
3. اربط المستودع
4. أضف Environment Variables
5. النشر تلقائي

### الخيار د: Hugging Face Spaces

1. أنشئ حساب على [huggingface.co](https://huggingface.co)
2. أنشئ Space جديد مع **Docker** SDK
3. ارفع الكود
4. أضف Secrets في الإعدادات:
   - `TELEGRAM_BOT_TOKEN`
   - `LLM_API_KEY`

## الخطوة 5: اختبار البوت

1. افتح البوت في Telegram
2. أرسل `/start`
3. أرسل ملف `.cbz` أو `.cbr`
4. انتظر المعالجة
5. ستصلك النسخة المترجمة!

---

## أوامر البوت

| الأمر | الوظيفة |
|-------|---------|
| `/start` | بدء الاستخدام |
| `/help` | المساعدة |
| `/settings` | عرض الإعدادات |
| `/setmodel <model>` | تغيير نموذج الترجمة |
| `/setprompt <text>` | تغيير برومبت الترجمة |
| `/setfont <name>` | تغيير الخط |
| `/reset` | إعادة تعيين |

## نماذج مجانية متاحة

| النموذج | المزود |
|---------|--------|
| `google/gemini-2.0-flash-exp:free` | OpenRouter |
| `meta-llama/llama-3.1-8b-instruct:free` | OpenRouter |
| `mistralai/mistral-7b-instruct:free` | OpenRouter |
| `gemini-2.0-flash` | Google Gemini |
| `llama-3.1-8b-instant` | Groq |

---

## التشغيل المحلي

```bash
pip install -r requirements.txt
python -m bot.main
```

## Docker

```bash
docker build -t comic-bot .
docker run --env-file .env comic-bot
```

## هيكل المشروع

```
├── bot/
│   ├── __init__.py
│   ├── main.py           # مدخل بوت Telegram
│   └── handlers.py       # معالجات الأوامر والملفات
├── pipeline/
│   ├── __init__.py
│   ├── archive_handler.py
│   ├── text_detector.py
│   ├── inpainter.py
│   ├── ocr_engine.py
│   ├── translator.py
│   ├── typesetter.py
│   └── pipeline.py
├── fonts/
│   └── NotoSansArabic-Regular.ttf
├── main.py               # CLI entry point
├── config.py
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env.example
└── README.md
```

## MIT License
