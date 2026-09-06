"""LLM translation engine with OpenAI-compatible API support."""

import os
import json
import logging
import httpx
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

COMIC_TRANSLATION_PROMPT = """أنت مترجم ومُعرب محترف للقصص المصورة (Comics Localization Specialist).
مهمتك: ترجمة نصوص وحوارات الكوميكس المرفقة إلى لغة عربية فصحى درامية، حيوية، وموجزة، تناسب أسلوب حوارات الكوميكس الحقيقية.

القواعد الصارمة:
1. تجنب الحرفية الركيكة تماماً؛ صِغ العبارات بأسلوب درامي متماسك يعكس نبرة المشهد (غضب، سخرية، توتر، همس).
2. الإيجاز الذكي (Conciseness): فقاعات الحوار ضيقة جداً، فاختر أقصر تعبير بلاغي يؤدي المعنى كاملاً دون حشو أو إطالة.
3. التكييف السياقي للألفاظ:
   - عبارات مثل "You're dead!" لا تُترجم "أنت ميت"، بل "سأقضي عليك!" أو "انتهى أمرك!".
   - عبارات مثل "Let's fight!" → "هيّا نقاتل!"
   - SFX مثل "BAM" → "بام!" أو ما يناسب الصوت
   - تعامل مع المصطلحات القتالية والأسماء الحركية بما هو سائد واحترافي في مجلات الكوميكس المصورة.
4. حافظ على سلامة النحو وقواعد التركيب العربي مع استخدام الأفعال النشطة.
5. الإخراج: أرجع النتائج كـ JSON array مطابق للمدخلات بحيث يحمل كل عنصر id و translation فقط.

INPUT FORMAT:
[{"id": 1, "text": "English text"}, {"id": 2, "text": "More text"}]

OUTPUT FORMAT (JSON only, no markdown):
[{"id": 1, "translation": "النص العربي"}, {"id": 2, "translation": "نص عربي آخر"}]"""


class LLMTranslator:

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        system_prompt: Optional[str] = None,
    ):
        self.api_key = api_key or os.getenv("LLM_API_KEY", "")
        self.base_url = (base_url or os.getenv("LLM_BASE_URL", "https://openrouter.ai/api/v1")).rstrip("/")
        self.model = model or os.getenv("LLM_MODEL", "minimax/minimax-m3:free")
        self.system_prompt = system_prompt or os.getenv("SYSTEM_PROMPT", COMIC_TRANSLATION_PROMPT)
        self._client = None

    @property
    def client(self):
        if self._client is None:
            self._client = httpx.Client(
                base_url=self.base_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://comic-translator.local",
                    "X-Title": "Comic Translator",
                },
                timeout=60.0,
            )
        return self._client

    def translate_batch(self, texts: List[Dict[str, str]]) -> List[Dict[str, str]]:
        if not texts:
            return []

        texts = [t for t in texts if t.get("text", "").strip()]
        if not texts:
            return []

        if not self.api_key:
            raise ValueError("LLM_API_KEY not set")

        prompt = json.dumps(texts, ensure_ascii=False, indent=2)
        logger.info(f"Translating {len(texts)} texts via {self.model}")

        response = self.client.post(
            "/chat/completions",
            json={
                "model": self.model,
                "messages": [
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": prompt},
                ],
                "temperature": 0.3,
                "max_tokens": 4096,
            },
        )

        if response.status_code == 401:
            raise ValueError(f"API key rejected (401). Check LLM_API_KEY.")
        if response.status_code == 429:
            raise ValueError(f"Rate limited (429). Model: {self.model}")
        if response.status_code >= 400:
            raise ValueError(f"API error {response.status_code}: {response.text[:300]}")

        data = response.json()
        if "choices" not in data or not data["choices"]:
            raise ValueError(f"No choices in response: {json.dumps(data)[:300]}")

        content = data["choices"][0]["message"]["content"]
        logger.info(f"LLM response ({len(content)} chars)")

        return self._parse_response(content, texts)

    def _parse_response(self, content: str, original: List[Dict]) -> List[Dict]:
        content = content.strip()

        # Remove markdown code blocks
        if "```" in content:
            lines = content.split("\n")
            json_lines = []
            in_block = False
            for line in lines:
                if line.strip().startswith("```"):
                    in_block = not in_block
                    continue
                if in_block or (line.strip().startswith("[") or line.strip().startswith("{")):
                    json_lines.append(line)
            content = "\n".join(json_lines)

        try:
            translations = json.loads(content)
            if isinstance(translations, list):
                trans_map = {}
                for t in translations:
                    if isinstance(t, dict) and "id" in t:
                        trans_map[t["id"]] = t

                result = []
                for orig in original:
                    if orig["id"] in trans_map:
                        entry = trans_map[orig["id"]]
                        result.append({
                            "id": orig["id"],
                            "text": orig["text"],
                            "translation": entry.get("translation", orig["text"]),
                        })
                    else:
                        result.append({
                            "id": orig["id"],
                            "text": orig["text"],
                            "translation": orig["text"],
                        })
                return result
        except json.JSONDecodeError as e:
            logger.warning(f"JSON parse failed: {e}")

        # Fallback: line-by-line
        lines = [l.strip() for l in content.split("\n") if l.strip()]
        result = []
        for i, orig in enumerate(original):
            trans = lines[i] if i < len(lines) else orig["text"]
            result.append({
                "id": orig["id"],
                "text": orig["text"],
                "translation": trans,
            })
        return result

    def set_model(self, model: str):
        self.model = model

    def set_system_prompt(self, prompt: str):
        self.system_prompt = prompt

    def set_provider(self, base_url: str, api_key: str, model: str):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.model = model
        if self._client:
            self._client.close()
            self._client = None
