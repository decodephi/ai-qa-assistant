# backend/modules/prompt_builder.py
# Builds the final LLM prompt from retrieved context, history, and user query.

import logging

logger = logging.getLogger(__name__)

MAX_CONTEXT_CHARS = 3000   # ~750 tokens of context — rich enough for Groq
MAX_HISTORY_CHARS = 600    # last N chars of conversation history
MAX_PROMPT_CHARS  = 6000   # Groq can handle 8k tokens; keep headroom


def build_prompt(
    query: str,
    retrieved_chunks: list[dict],
    chat_history_text: str = "",
) -> str:
    """
    Assemble the full LLM prompt.

    Components:
      1. System instruction  — role + output format
      2. Chat history        — previous conversation context
      3. Web context         — top-k RAG chunks from vector DB
      4. User question       — current query

    Returns:
        A single prompt string ready to be sent to the LLM.
    """

    # ── Part 1: Context block ──────────────────────────────────────────────────
    if retrieved_chunks:
        raw_context = "\n\n".join(
            f"[Source {i+1}]\n{c['text']}"
            for i, c in enumerate(retrieved_chunks)
        )
        context_block = raw_context[:MAX_CONTEXT_CHARS]
    else:
        context_block = "No relevant web content was found for this query."

    # ── Part 2: History block ─────────────────────────────────────────────────
    history_section = ""
    if chat_history_text and chat_history_text.strip():
        trimmed = chat_history_text.strip()[-MAX_HISTORY_CHARS:]
        history_section = f"--- Previous Conversation ---\n{trimmed}\n\n"

    # ── Part 3: Full prompt ────────────────────────────────────────────────────
    prompt = f"""You are an expert AI research assistant. Your job is to give accurate, detailed, and helpful answers based on the provided web sources.

STRICT RULES:
- Answer ONLY from the provided context below. Do NOT hallucinate.
- Be comprehensive but concise. Use clear, natural language.
- Cite sources inline like (Source 1), (Source 2) where relevant.
- Always end with 3-5 bullet Key Points summarizing the answer.
- If the context does not contain enough info, say "I couldn't find reliable information about this."

{history_section}--- Web Context ---
{context_block}

--- Question ---
{query}

--- Your Answer ---
Provide a thorough answer (3-6 sentences), then list Key Points:

Answer:
[Write your detailed answer here, citing sources]

Key Points:
- [key point 1]
- [key point 2]
- [key point 3]
"""

    # Safety cap (for local model fallback)
    return prompt[:MAX_PROMPT_CHARS]


def extract_sources(retrieved_chunks: list[dict], max_sources: int = 5) -> list[str]:
    """
    Extract unique source URLs from retrieved chunks.

    Returns:
        List of unique URL strings (up to max_sources).
    """
    seen: set[str] = set()
    result: list[str] = []

    for chunk in retrieved_chunks:
        url = chunk.get("source", "").strip()
        if url and url.startswith("http") and url not in seen:
            seen.add(url)
            result.append(url)
        if len(result) >= max_sources:
            break

    return result
