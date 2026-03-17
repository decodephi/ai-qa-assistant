# app.py - Streamlit UI for the AI Web Assistant

import streamlit as st
from main import get_answer

# ── Page config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Web Assistant",
    page_icon="🔍",
    layout="centered"
)

# ── Custom CSS for clean minimal design ─────────────────────────────────────
st.markdown("""
<style>
    /* Main container */
    .block-container { padding-top: 2rem; max-width: 780px; }

    /* Title */
    h1 { font-size: 2rem !important; font-weight: 700; }

    /* Answer box */
    .answer-box {
        background: #f0f4ff;
        border-left: 4px solid #4a6cf7;
        border-radius: 8px;
        padding: 1.2rem 1.5rem;
        margin-top: 0.5rem;
        font-size: 1rem;
        line-height: 1.7;
        color: #1a1a2e;
    }

    /* Source link cards */
    .source-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 0.6rem 1rem;
        margin-bottom: 0.5rem;
        font-size: 0.92rem;
    }
    .source-card a {
        color: #4a6cf7;
        text-decoration: none;
        font-weight: 500;
    }
    .source-card a:hover { text-decoration: underline; }

    /* Section headers */
    .section-label {
        font-size: 0.78rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #64748b;
        margin-top: 1.5rem;
        margin-bottom: 0.4rem;
    }
</style>
""", unsafe_allow_html=True)


# ── Header ───────────────────────────────────────────────────────────────────
st.markdown("## 🔍 AI Web Assistant")
st.markdown("Ask any question — I'll search the web and generate a concise answer for you.")
st.divider()


# ── Input area ───────────────────────────────────────────────────────────────
query = st.text_input(
    label="Your Question",
    placeholder="e.g. What is quantum computing?",
    label_visibility="collapsed"
)

search_btn = st.button("🔎 Search & Answer", use_container_width=True, type="primary")


# ── Pipeline trigger ─────────────────────────────────────────────────────────
if search_btn:
    if not query or not query.strip():
        st.warning("⚠️ Please enter a question before searching.")
    else:
        with st.spinner("Searching the web and generating your answer..."):
            result = get_answer(query)

        # ── Error state ──────────────────────────────────────────────────────
        if result.get("error"):
            st.error(f"❌ {result['error']}")

        else:
            # ── Answer section ───────────────────────────────────────────────
            st.markdown('<div class="section-label">📝 Answer</div>', unsafe_allow_html=True)
            st.markdown(
                f'<div class="answer-box">{result["answer"]}</div>',
                unsafe_allow_html=True
            )

            # ── Sources section ──────────────────────────────────────────────
            sources = result.get("sources", [])
            if sources:
                st.markdown('<div class="section-label">🔗 Sources</div>', unsafe_allow_html=True)
                for src in sources:
                    title = src.get("title", "Source")
                    url = src.get("url", "#")
                    st.markdown(
                        f'<div class="source-card"><a href="{url}" target="_blank">↗ {title}</a>'
                        f'<br><span style="color:#94a3b8;font-size:0.8rem">{url}</span></div>',
                        unsafe_allow_html=True
                    )
            else:
                st.info("No source links available for this query.")


# ── Footer ───────────────────────────────────────────────────────────────────
st.divider()
st.markdown(
    '<p style="text-align:center;color:#94a3b8;font-size:0.8rem">'
    'Powered by DuckDuckGo · newspaper3k · flan-t5-base · Streamlit</p>',
    unsafe_allow_html=True
)