# backend/modules/llm.py
# LLM module: Groq cloud (llama-3.3-70b) primary, flan-t5-large local fallback.

import os
import logging
import requests
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

GROQ_API_KEY  = os.getenv("GROQ_API_KEY", "")
GROQ_ENDPOINT = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL    = "llama-3.3-70b-versatile"   # free tier, very capable

# ── Lazy-load local model only if no Groq key ─────────────────────────────────
_local_generator = None


def _load_local_model():
    global _local_generator
    if _local_generator is None:
        from transformers import pipeline
        logger.info("[llm] Loading local flan-t5-large (fallback)…")
        _local_generator = pipeline(
            "text2text-generation",
            model="google/flan-t5-large",
        )
        logger.info("[llm] Local model loaded.")
    return _local_generator


# ── Groq generation ────────────────────────────────────────────────────────────
def _generate_via_groq(prompt: str) -> str:
    """Call Groq API (OpenAI-compatible) and return generated text."""
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": GROQ_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 1024,
        "temperature": 0.4,
        "top_p": 0.9,
    }
    resp = requests.post(GROQ_ENDPOINT, json=payload, headers=headers, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    return data["choices"][0]["message"]["content"].strip()


# ── Local flan-t5-large generation ────────────────────────────────────────────
def _generate_via_local(prompt: str) -> str:
    """Generate using local flan-t5-large model."""
    gen = _load_local_model()
    # flan-t5-large handles ~1024 tokens ≈ 4000 chars
    prompt = prompt[:3500]
    result = gen(
        prompt,
        max_new_tokens=512,
        do_sample=True,
        temperature=0.6,
        top_p=0.9,
        repetition_penalty=1.3,
    )
    return result[0].get("generated_text", "").strip()


# ── Public API ─────────────────────────────────────────────────────────────────
def generate_answer(prompt: str) -> str:
    """
    Generate an answer from a fully pre-built prompt string.

    Uses Groq llama-3.3-70b if GROQ_API_KEY is set, otherwise falls back
    to local flan-t5-large.

    Args:
        prompt: Complete prompt string from prompt_builder.build_prompt()

    Returns:
        Raw generated text string.
    """
    if not prompt or not prompt.strip():
        return "I could not find enough information to answer that question."

    # ── Try Groq first ─────────────────────────────────────────────────────────
    if GROQ_API_KEY:
        try:
            logger.info("[llm] Generating via Groq (%s)…", GROQ_MODEL)
            answer = _generate_via_groq(prompt)
            logger.info("[llm] Groq response: %d chars", len(answer))
            return answer
        except Exception as exc:
            logger.warning("[llm] Groq failed (%s) — falling back to local model.", exc)

    # ── Local fallback ──────────────────────────────────────────────────────────
    try:
        logger.info("[llm] Generating via local flan-t5-large…")
        answer = _generate_via_local(prompt)
        logger.info("[llm] Local response: %d chars", len(answer))
        return answer if answer else "The model could not generate a response."
    except Exception as exc:
        logger.error("[llm] Local model error: %s", exc)
        return "An error occurred while generating the answer."


def get_active_backend() -> str:
    """Return a human-readable label for the currently active LLM backend."""
    return f"Groq · {GROQ_MODEL}" if GROQ_API_KEY else "Local · flan-t5-large"
