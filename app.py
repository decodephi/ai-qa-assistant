# app.py — Conversational RAG Chatbot UI (v2)
# Chat-style interface with memory display, key points, and sources.

import streamlit as st
from main import get_answer
from modules.memory import chat_memory

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="RAG Chatbot",
    page_icon="🤖",
    layout="centered"
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .block-container { padding-top: 1.5rem; max-width: 800px; }

    /* Chat bubbles */
    .user-bubble {
        background: #e8f0fe;
        border-radius: 12px 12px 2px 12px;
        padding: 0.8rem 1.1rem;
        margin: 0.4rem 0 0.4rem 15%;
        font-size: 0.97rem;
        color: #1a1a2e;
    }
    .bot-bubble {
        background: #f8f9fa;
        border: 1px solid #e2e8f0;
        border-radius: 12px 12px 12px 2px;
        padding: 0.9rem 1.2rem;
        margin: 0.4rem 15% 0.4rem 0;
        font-size: 0.97rem;
        color: #1a1a2e;
        line-height: 1.7;
    }

    /* Section labels */
    .label {
        font-size: 0.72rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #94a3b8;
        margin-bottom: 0.3rem;
    }

    /* Key points box */
    .kp-box {
        background: #fffbeb;
        border-left: 3px solid #f59e0b;
        border-radius: 6px;
        padding: 0.6rem 1rem;
        margin-top: 0.6rem;
        font-size: 0.9rem;
    }

    /* Source cards */
    .src-card {
        background: #fff;
        border: 1px solid #e2e8f0;
        border-radius: 6px;
        padding: 0.45rem 0.9rem;
        margin-top: 0.3rem;
        font-size: 0.85rem;
    }
    .src-card a { color: #4a6cf7; text-decoration: none; font-weight: 500; }
    .src-card a:hover { text-decoration: underline; }

    /* Memory sidebar badge */
    .mem-badge {
        background: #f1f5f9;
        border-radius: 6px;
        padding: 0.4rem 0.7rem;
        font-size: 0.82rem;
        color: #475569;
        margin-bottom: 0.4rem;
    }
</style>
""", unsafe_allow_html=True)


# ── Session state setup ───────────────────────────────────────────────────────
# Store the display conversation (different from the memory module's store).
# 'messages' drives what's rendered on screen.
if "messages" not in st.session_state:
    st.session_state.messages = []   # list of {"role", "content", "key_points", "sources"}


# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("## 🤖 RAG Chatbot")
st.markdown("Ask anything — I search the web, retrieve relevant context, and remember our conversation.")
st.divider()


# ── Sidebar: memory viewer ────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🧠 Chat Memory")
    st.caption("Last 5 turns stored in memory")

    history = chat_memory.get_history()
    if history:
        for entry in history:
            role_label = "🙋 You" if entry["role"] == "user" else "🤖 Bot"
            st.markdown(
                f'<div class="mem-badge"><b>{role_label}:</b> {entry["content"][:80]}{"..." if len(entry["content"]) > 80 else ""}</div>',
                unsafe_allow_html=True
            )
    else:
        st.info("No memory yet. Start chatting!")

    st.divider()
    if st.button("🗑️ Clear Memory & Chat", use_container_width=True):
        chat_memory.clear()
        st.session_state.messages = []
        st.rerun()


# ── Render existing chat messages ─────────────────────────────────────────────
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f'<div class="user-bubble">🙋 {msg["content"]}</div>', unsafe_allow_html=True)
    else:
        # Bot answer
        st.markdown(f'<div class="bot-bubble">🤖 {msg["content"]}</div>', unsafe_allow_html=True)

        # Key points
        if msg.get("key_points"):
            kp_html = "".join(f"<li>{kp}</li>" for kp in msg["key_points"])
            st.markdown(
                f'<div class="kp-box"><div class="label">📌 Key Points</div><ul style="margin:0;padding-left:1.2rem">{kp_html}</ul></div>',
                unsafe_allow_html=True
            )

        # Sources
        if msg.get("sources"):
            st.markdown('<div class="label" style="margin-top:0.8rem">🔗 Sources</div>', unsafe_allow_html=True)
            for src in msg["sources"]:
                st.markdown(
                    f'<div class="src-card"><a href="{src["url"]}" target="_blank">↗ {src["title"]}</a></div>',
                    unsafe_allow_html=True
                )


# ── Input area ────────────────────────────────────────────────────────────────
st.divider()
col1, col2 = st.columns([5, 1])

with col1:
    query = st.text_input(
        label="Your message",
        placeholder="Ask a question or follow up on the previous one...",
        label_visibility="collapsed",
        key="chat_input"
    )
with col2:
    send = st.button("Send", use_container_width=True, type="primary")


# ── Process query ─────────────────────────────────────────────────────────────
if send:
    if not query or not query.strip():
        st.warning("⚠️ Please type a question first.")
    else:
        # Add user bubble immediately
        st.session_state.messages.append({"role": "user", "content": query})

        with st.spinner("🔍 Searching → 📄 Extracting → 🧠 Thinking..."):
            result = get_answer(query)

        if result.get("error"):
            st.error(f"❌ {result['error']}")
        else:
            # Add assistant response to display history
            st.session_state.messages.append({
                "role":       "assistant",
                "content":    result["answer"],
                "key_points": result.get("key_points", []),
                "sources":    result.get("sources", [])
            })

        st.rerun()   # Refresh to render new messages and updated sidebar


# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown(
    '<p style="text-align:center;color:#94a3b8;font-size:0.78rem;margin-top:1rem">'
    'DuckDuckGo · newspaper4k · FAISS · sentence-transformers · flan-t5-base · Streamlit</p>',
    unsafe_allow_html=True
)