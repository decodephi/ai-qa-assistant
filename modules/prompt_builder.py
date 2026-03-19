# modules/prompt_builder.py
# Builds the final structured prompt sent to the LLM.
# Combines: chat history + retrieved context chunks + user query.
# The prompt is carefully engineered to:
#   - Prevent hallucination (context-only instruction)
#   - Request structured output (Answer + Key Points)
#   - Stay within flan-t5-base's token limit (~512 tokens / ~2000 chars)

# ── Constants ─────────────────────────────────────────────────────────────────
MAX_CONTEXT_CHARS  = 1200  # max chars from retrieved chunks
MAX_HISTORY_CHARS  = 400   # max chars from chat history block
MAX_PROMPT_CHARS   = 1900  # hard cap before sending to LLM


def build_prompt(
    query:         str,
    retrieved_chunks: list[dict],
    chat_history_text: str = ""
) -> str:
    """
    Assemble the full LLM prompt from three components:

    1. Chat History   — what was discussed before (gives follow-up context)
    2. Context        — the most relevant scraped chunks from vector DB
    3. User Query     — the current question

    Args:
        query:              Current user question
        retrieved_chunks:   List of chunk dicts from vector_store.retrieve()
                            Each has {"text": str, "source": str}
        chat_history_text:  Pre-formatted history string from memory.format_for_prompt()

    Returns:
        A single string prompt ready to be sent to the LLM.

    Output format instructed inside prompt:
        Answer:
        <concise answer>

        Key Points:
        - point 1
        - point 2
        - point 3
    """

    # ── Part 1: Context from vector DB ────────────────────────────────────────
    if retrieved_chunks:
        # Join chunks, separated by markers so LLM can follow the structure
        raw_context = "\n\n".join(
            f"[Source: {c.get('source', 'unknown')}]\n{c['text']}"
            for c in retrieved_chunks
        )
        # Trim to limit
        context_block = raw_context[:MAX_CONTEXT_CHARS]
    else:
        context_block = "No relevant content was found."

    # ── Part 2: Chat history block ────────────────────────────────────────────
    if chat_history_text and chat_history_text.strip():
        history_block = chat_history_text.strip()[:MAX_HISTORY_CHARS]
        history_section = f"Previous Conversation:\n{history_block}\n\n"
    else:
        history_section = ""  # first turn — no history yet

    # ── Part 3: Assemble final prompt ─────────────────────────────────────────
    prompt = (
        f"You are a helpful AI assistant. "
        f"Answer ONLY using the provided context. "
        f"Do NOT make up information. "
        f"Be concise and structured.\n\n"
        f"{history_section}"
        f"Context:\n{context_block}\n\n"
        f"Question: {query}\n\n"
        f"Respond in this exact format:\n"
        f"Answer:\n"
        f"<your answer here>\n\n"
        f"Key Points:\n"
        f"- point 1\n"
        f"- point 2\n"
        f"- point 3"
    )

    # Hard cap the full prompt (flan-t5-base token limit safety)
    prompt = prompt[:MAX_PROMPT_CHARS]

    return prompt


def extract_sources(retrieved_chunks: list[dict], max_sources: int = 3) -> list[str]:
    """
    Extract unique source URLs from retrieved chunks (deduplicated, top 3).

    Args:
        retrieved_chunks: Chunks returned by vector_store.retrieve()
        max_sources:      Max number of unique sources to return

    Returns:
        List of unique URL strings
    """
    seen   = set()
    result = []

    for chunk in retrieved_chunks:
        url = chunk.get("source", "").strip()
        if url and url not in seen and url.startswith("http"):
            seen.add(url)
            result.append(url)
        if len(result) >= max_sources:
            break

    return result

# if __name__ == "__main__":
#     print("Testing prompt_builder...\n")

#     query = "What is AI?"

#     sample_chunks = [
#         {"text": "AI stands for Artificial Intelligence.", "source": "https://a.com"},
#         {"text": "It enables machines to learn and make decisions.", "source": "https://b.com"}
#     ]

#     history = "User: What is AI?\nAssistant: AI is..."

#     prompt = build_prompt(query, sample_chunks, history)

#     print("Generated Prompt:\n")
#     print(prompt)

#     sources = extract_sources(sample_chunks)

#     print("\nExtracted Sources:")
#     print(sources)