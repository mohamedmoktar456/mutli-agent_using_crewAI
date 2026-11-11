# فريق مشروعك الذكي — CrewAI

تطبيق عربي ينسق العمل بين أربعة وكلاء CrewAI لبناء تصور متكامل لأي فكرة مشروع:

1. **مدير المشروع:** يحلل الطلب ويكتب الخطة والمهام ومعايير القبول.
2. **مطور Backend:** يصمم منطق الأعمال والبيانات ومكونات النظام.
3. **مصمم UI/UX:** يقترح الشاشات والتفاعلات والحالات وتجربة الاستخدام.
4. **مختبر الجودة:** يراجع المخرجات ويحدد الاختبارات والفجوات والمخاطر.

## التشغيل

يتطلب Python 3.10 إلى 3.13.

```bash
python -m venv .venv
# Windows PowerShell
.venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
```

انسخ `.env.example` إلى `.env` وضع مفتاح API المناسب:

```env
LLM_PROVIDER=openai
LLM_MODEL=gpt-4o-mini
LLM_API_KEY=your-api-key-here
```

ثم شغّل الواجهة:

```bash
streamlit run app.py
```

## تبديل مزود النموذج

التكامل يستخدم واجهة LiteLLM في CrewAI. غيّر الإعدادات في `.env`:

| المزوّد | `LLM_PROVIDER` | نموذج افتراضي مقترح |
|---|---|---|
| OpenAI | `openai` | `gpt-4o-mini` |
| Google Gemini | `gemini` | `gemini/gemini-2.0-flash` |
| Anthropic | `anthropic` | `claude-3-5-haiku-latest` |
| Ollama محلي | `ollama` | `ollama/llama3.1` |
| OpenRouter | `openrouter` | `openrouter/openai/gpt-4o-mini` |

```env
LLM_PROVIDER=gemini
LLM_MODEL=gemini/gemini-2.0-flash
LLM_API_KEY=your-gemini-key
```

`LLM_API_KEY` اسم موحد لسهولة التبديل. ويمكن عند الحاجة استخدام اسم المتغير الخاص بالمزوّد مثل `GEMINI_API_KEY` أو `OPENAI_API_KEY`. المتغير `LLM_BASE_URL` اختياري لنقاط الاتصال المتوافقة أو Ollama.

## كيف يتعاون الفريق؟

يستخدم التطبيق `Process.sequential` حتى تكون المخرجات قابلة للشرح والعرض: ينجز المدير الخطة، ثم يطلع المطور عليها، ثم يعمل المصمم بالاستناد إلى الخطة والتصميم الخلفي، ثم يراجع المختبر كل ما سبق. المهام تستقبل وصف المشروع نفسه وتستخدم سياق المهام السابقة.

## هيكل الملفات

- `app.py` — واجهة Streamlit العربية وعرض سير العمل والنتائج.
- `crew.py` — تعريف الوكلاء والمهام وسير التعاون واختيار النموذج.
- `.env.example` — قالب إعداد المزود والمفتاح.
