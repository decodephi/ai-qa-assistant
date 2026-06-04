# backend/pipeline.py
# Main RAG orchestrator. Called by the FastAPI API layer.
#
# Full flow per query:
#   1.  Validate input
#   2.  Retrieve chat history         (memory)
#   3.  Enhance query for follow-ups  (memory)
#   4.  Web search                    (search)
#   5.  Scrape content                (scraper)
#   6.  Chunk content                 (chunker)
#   7.  Build FAISS vector index      (vector_store)
#   8.  Retrieve top-k chunks         (vector_store)
#   9.  Build structured prompt       (prompt_builder)
#  10.  Generate answer               (llm)
#  11.  Parse answer + key points
#  12.  Save turn to memory           (memory)
#  13.  Return answer + key_points + sources

import logging

from backend.modules.search        import get_top_urls
from backend.modules.scraper       import scrape_multiple
from backend.modules.chunker       import chunk_multiple
from backend.modules.vector_store  import vector_store
from backend.modules.memory        import chat_memory
from backend.modules.prompt_builder import build_prompt, extract_sources
from backend.modules.llm           import generate_answer
from backend.modules.helpers       import format_sources, is_valid_query

logger = logging.getLogger(__name__)


# ── Output parser ──────────────────────────────────────────────────────────────
def parse_llm_output(raw: str) -> tuple[str, list[str]]:
    """
    Parse the LLM's structured output into answer text and key points.

    Expected format:
        Answer:
        <answer text>

        Key Points:
        - point 1
        - point 2

    Falls back gracefully if format is missing.
    """
    answer     = raw.strip()
    key_points: list[str] = []

    if "Key Points:" in raw:
        parts      = raw.split("Key Points:", 1)
        answer     = parts[0].replace("Answer:", "").strip()
        kp_section = parts[1].strip()
        for line in kp_section.splitlines():
            line = line.strip()
            if line.startswith("-") and len(line) > 2:
                key_points.append(line[1:].strip())
    elif "Answer:" in raw:
        answer = raw.split("Answer:", 1)[1].strip()

    # Clean up any stray section headers
    answer = answer.replace("Key Points:", "").replace("Simple Explanation:", "").strip()

    return answer, key_points


# ── Main entry point ───────────────────────────────────────────────────────────
def get_answer(query: str) -> dict:
    """
    Run the full RAG pipeline for a user query.

    Args:
        query: Current user question.

    Returns:
        {
            "answer":     str,
            "key_points": list[str],
            "sources":    list[{"title": str, "url": str}],
            "error":      str | None,
            "backend":    str,          # which LLM was used
        }
    """
    from backend.modules.llm import get_active_backend

    # ── Step 1: Validate ───────────────────────────────────────────────────────
    if not is_valid_query(query):
        return {"answer": "", "key_points": [], "sources": [], "error": "Please enter a valid question.", "backend": ""}

    # ── Step 2: Chat history ───────────────────────────────────────────────────
    history_text = chat_memory.format_for_prompt()

    # ── Step 3: Enhance query (follow-up detection) ────────────────────────────
    enhanced_query = chat_memory.enhance_query(query)
    logger.info("[pipeline] Query: %r  Enhanced: %r", query, enhanced_query)

    # ── Step 4: Web search ─────────────────────────────────────────────────────
    search_results = get_top_urls(enhanced_query, max_results=5)

    if not search_results:
        logger.warning("[pipeline] No search results found.")
        return {
            "answer":     "I couldn't find any information about that. Please try rephrasing your question.",
            "key_points": [],
            "sources":    [],
            "error":      None,
            "backend":    get_active_backend(),
        }

    # ── Step 5: Scrape URLs ────────────────────────────────────────────────────
    urls     = [r["url"] for r in search_results]
    contents = scrape_multiple(urls)

    # Fallback to snippets if scraping returned nothing useful
    if not any(contents):
        logger.warning("[pipeline] Scraping failed — using search snippets.")
        contents = [r.get("snippet", "") for r in search_results]

    # For price / real-time queries also mix in snippets for freshness
    if any(kw in query.lower() for kw in ("price", "stock", "today", "now", "latest", "current")):
        logger.info("[pipeline] Real-time query — mixing in snippets.")
        snippets = [r.get("snippet", "") for r in search_results]
        contents = [
            (c + "\n\n" + s).strip() if c else s
            for c, s in zip(contents, snippets)
        ]

    # ── Step 6: Chunk content ──────────────────────────────────────────────────
    chunks = chunk_multiple(contents, urls)

    if not chunks:
        return {
            "answer":     "Could not extract usable content from the search results.",
            "key_points": [],
            "sources":    [],
            "error":      None,
            "backend":    get_active_backend(),
        }

    # ── Step 7: Build vector index ─────────────────────────────────────────────
    vector_store.build(chunks)

    # ── Step 8: Retrieve relevant chunks ──────────────────────────────────────
    retrieved = vector_store.retrieve(enhanced_query, top_k=6)
    if not retrieved:
        retrieved = chunks[:6]
        logger.warning("[pipeline] Vector retrieval empty — using first chunks.")

    # ── Step 9: Build prompt ───────────────────────────────────────────────────
    prompt = build_prompt(
        query             = query,
        retrieved_chunks  = retrieved,
        chat_history_text = history_text,
    )

    # ── Step 10: Generate answer ───────────────────────────────────────────────
    logger.info("[pipeline] Sending prompt to LLM…")
    raw_output = generate_answer(prompt)

    # ── Step 11: Parse output ──────────────────────────────────────────────────
    answer, key_points = parse_llm_output(raw_output)

    # ── Step 12: Save turn ────────────────────────────────────────────────────
    chat_memory.add_turn(user_msg=query, assistant_msg=answer)

    # ── Step 13: Build source list ────────────────────────────────────────────
    chunk_urls    = extract_sources(retrieved, max_sources=5)
    url_to_title  = {r["url"]: r.get("title", "Source") for r in search_results}
    sources       = [{"title": url_to_title.get(u, "Source"), "url": u} for u in chunk_urls]
    if not sources:
        sources = format_sources(search_results)

    logger.info(
        "[pipeline] Done. Answer: %d chars, Key points: %d, Sources: %d",
        len(answer), len(key_points), len(sources),
    )

    return {
        "answer":     answer,
        "key_points": key_points,
        "sources":    sources,
        "error":      None,
        "backend":    get_active_backend(),
    }
