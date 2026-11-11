"""Arabic Streamlit interface for the CrewAI four-agent project team."""

from __future__ import annotations

import os

import streamlit as st
from dotenv import load_dotenv

from crew import build_crew

load_dotenv()
st.set_page_config(page_title="فريق CrewAI الذكي", page_icon="🤖", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;500;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Cairo', sans-serif; }
.hero { padding: 2rem 2.2rem; border-radius: 22px; background: linear-gradient(125deg,#101b3d,#2357a5 65%,#36a6b5); color:white; margin-bottom:1.2rem; }
.hero h1 { font-size:2.4rem; margin:0; color:white; }
.hero p { font-size:1.05rem; opacity:.9; margin:.6rem 0 0; }
.agent-card { background:#f3f6fb; border:1px solid #e2e8f0; border-radius:16px; padding:1rem 1.1rem; min-height:145px; direction:rtl; }
.agent-card h3 { margin:0 0 .35rem; font-size:1.05rem; color:#172b4d; }
.agent-card p { margin:0; color:#52627a; font-size:.9rem; }
.step { color:#607089; font-size:.85rem; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="hero" dir="rtl"><h1>🤖 فريق مشروعك الذكي</h1><p>أربعة وكلاء متخصصين يتعاونون لتحويل فكرتك إلى خطة، تصميم، وحل قابل للتنفيذ.</p></div>', unsafe_allow_html=True)

with st.sidebar:
    st.header("⚙️ إعدادات النموذج")
    provider = os.getenv("LLM_PROVIDER", "openai").strip().lower()
    model = os.getenv("LLM_MODEL", "").strip()
    st.caption(f"المزوّد من ملف .env: **{provider}**")
    st.caption(f"النموذج: **{model or 'الافتراضي للمزوّد'}**")
    st.info("لتغيير المزوّد، عدّل `LLM_PROVIDER` و`LLM_MODEL` و`LLM_API_KEY` في ملف `.env` ثم أعد تشغيل التطبيق.")
    st.caption("المزوّدون المدعومون: OpenAI · Gemini · Anthropic · Ollama · OpenRouter")
    st.divider()
    st.caption("تسلسل العمل: التخطيط ← Backend ← تصميم الواجهة ← ضمان الجودة")

st.markdown("### 👥 فريق العمل")
cols = st.columns(4)
cards = [
    ("🧭", "مدير المشروع", "يفهم المتطلبات ويقسم العمل ويتابع معايير القبول."),
    ("⚙️", "مطور Backend", "يصمم منطق الأعمال والبيانات والواجهات البرمجية."),
    ("🎨", "مصمم UI/UX", "يبني تصور الشاشات والتفاعلات وتجربة استخدام واضحة."),
    ("🧪", "مختبر الجودة", "يراجع المخرجات ويحدد الاختبارات والفجوات والمخاطر."),
]
for col, (icon, title, desc) in zip(cols, cards):
    with col:
        st.markdown(f'<div class="agent-card"><h3>{icon} {title}</h3><p>{desc}</p></div>', unsafe_allow_html=True)

st.markdown("### 🚀 صف مشروعك")
with st.form("project_form"):
    brief = st.text_area(
        "ما التطبيق الذي تريد بناءه؟",
        placeholder="مثال: أريد تطبيقاً لإدارة مهام فريق صغير، مع تسجيل دخول، قوائم مهام، تحديد مسؤول وموعد نهائي، ولوحة تعرض التقدم...",
        height=145,
        help="اكتب الفكرة والوظائف المطلوبة وأي تفضيلات تقنية تعرفها.",
    )
    submitted = st.form_submit_button("✨ ابدأ تعاون الفريق", type="primary", use_container_width=True)

if submitted:
    if not brief.strip():
        st.warning("اكتب وصف المشروع قبل بدء الفريق.")
    else:
        try:
            crew, agents, tasks = build_crew(brief)
            st.markdown("### 🔄 سير العمل")
            progress = st.progress(0, text="يبدأ مدير المشروع بتحليل طلبك...")
            status = st.status("الفريق يعمل على مشروعك…", expanded=True)
            status.write("🧭 مدير المشروع يحدد المتطلبات وخطة العمل.")
            status.write("⚙️ مطور Backend يبني التصور التقني.")
            status.write("🎨 مصمم UI/UX يجهز تجربة الاستخدام.")
            status.write("🧪 مختبر الجودة يراجع الحل ومعايير القبول.")
            with st.spinner("الوكلاء يتعاونون الآن، قد يستغرق ذلك بعض الوقت…"):
                result = crew.kickoff(inputs={"project_brief": brief.strip()})
            progress.progress(100, text="اكتمل تعاون الوكلاء الأربعة.")
            status.update(label="اكتمل عمل الفريق", state="complete", expanded=False)
            st.markdown("### 📋 نتيجة الفريق")
            st.markdown(result.raw if hasattr(result, "raw") else str(result))
            with st.expander("تفاصيل المهام والوكلاء"):
                for agent, task in zip(agents, tasks):
                    st.markdown(f"**{agent.role}** — {task.expected_output}")
                    output = getattr(task, "output", None)
                    if output:
                        st.write(str(output))
        except Exception as exc:
            st.error(f"تعذر تشغيل الفريق: {exc}")
            st.info("تحقق من تثبيت المتطلبات وإعداد مزود النموذج ومفتاح API في `.env`.")

st.divider()
st.markdown('<div dir="rtl" style="text-align:center;color:#8391a7">مبني باستخدام CrewAI · أربعة أدوار، سير عمل واضح، ومزوّد قابل للتبديل</div>', unsafe_allow_html=True)
