
MAX_CONTEXT_CHARS  = 800  
MAX_HISTORY_CHARS  = 300   
MAX_PROMPT_CHARS   = 1600  


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
            f"[Source {i+1}: {c.get('source')}]\n{c['text']}"
            for i, c in enumerate(retrieved_chunks)
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
        
    "You are a helpful AI assistant.\n"
    "Answer ONLY using the provided context.\n"
    "Do NOT make up information.\n"
    "Do NOT repeat the same sentence.\n"
    "Keep answers natural and human-like.\n\n"
    

    "Your response MUST follow this structure:\n\n"

    "Answer:\n"
    "While answering, refer to sources like (Source 1), (Source 2).\n"
    "Write a clear and detailed explanation (3–5 sentences).\n\n"

    "Simple Explanation:\n"
    "While answering, refer to sources like (Source 1), (Source 2).\n"
    "Explain in easy words for a beginner to advance, thihk we make them understand.\n\n"
    

    "Examples:\n"
    "- Give 2 real-world examples\n\n"

    "Key Points:\n"
    "- point 1\n"
    "- point 2\n"
    "- point 3\n\n"

    f"{history_section}"
    f"Context:\n{context_block}\n\n"
    f"Question: {query}\n"
    )

    # Hard cap the full prompt (flan-t5-base token limit safety)
    prompt = prompt[:MAX_PROMPT_CHARS]

    return prompt


def extract_sources(retrieved_chunks: list[dict], max_sources: int = 5) -> list[str]:
    """
    Extract unique source URLs from retrieved chunks (deduplicated, top 5).

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


