# main.py — Conversational RAG Pipeline (v2)
#
# Full flow per query:
#   1. Validate input
#   2. Retrieve chat history  (memory.py)
#   3. Enhance query for follow-ups  (memory.py)
#   4. Web search  (search.py)
#   5. Scrape content  (scraper.py)
#   6. Chunk content  (chunker.py)
#   7. Store chunks in vector DB  (vector_store.py)
#   8. Retrieve top-k relevant chunks  (vector_store.py)
#   9. Build structured prompt  (prompt_builder.py)
#  10. Generate answer  (llm.py)
#  11. Parse answer + key points
#  12. Save turn to memory  (memory.py)
#  13. Return answer + key points + sources

from modules.search        import get_top_urls
from modules.scraper       import scrape_multiple
from modules.chunker       import chunk_multiple
from modules.vector_store  import vector_store
from modules.memory        import chat_memory
from modules.prompt_builder import build_prompt, extract_sources
from modules.llm           import generate_answer
from modules.helpers       import format_sources, is_valid_query


def parse_llm_output(raw: str) -> tuple[str, list[str]]:
    """
    Parse the LLM's structured output into answer text and key points list.

    Expected LLM output format:
        Answer:
        <answer text>

        Key Points:
        - point 1
        - point 2
        - point 3

    Args:
        raw: Raw string returned by generate_answer()

    Returns:
        (answer_text, key_points_list)
        Falls back gracefully if format is not followed by the model.
    """
    answer     = raw.strip()
    key_points = []

    # Try to split on "Key Points:" marker
    if "Key Points:" in raw:
        parts      = raw.split("Key Points:", 1)
        answer     = parts[0].replace("Answer:", "").strip()
        kp_section = parts[1].strip()

        # Extract bullet lines
        for line in kp_section.splitlines():
            line = line.strip()
            if line.startswith("-"):
                key_points.append(line[1:].strip())

    elif "Answer:" in raw:
        # At least extract the answer part cleanly
        answer = raw.split("Answer:", 1)[1].strip()

    # Remove stray format remnants
    answer = answer.replace("Key Points:", "").strip()

    return answer, key_points


def get_answer(query: str) -> dict:
    """
    Conversational RAG pipeline — main entry point called by app.py.

    Args:
        query: Current user question string

    Returns:
        {
            "answer":     str,          # LLM generated answer
            "key_points": list[str],    # Bullet points extracted from answer
            "sources":    list[dict],   # [{"title": ..., "url": ...}, ...]
            "error":      str | None    # Error message or None
        }
    """

    # ── Step 1: Validate input ────────────────────────────────────────────────
    if not is_valid_query(query):
        return {"answer": "", "key_points": [], "sources": [], "error": "Please enter a valid question."}

    # ── Step 2: Retrieve chat history ─────────────────────────────────────────
    history_text = chat_memory.format_for_prompt()

    # ── Step 3: Enhance query using history (handles follow-up questions) ─────
    enhanced_query = chat_memory.enhance_query(query)

    # ── Step 4: Web search using enhanced query ───────────────────────────────
    print(f"\n[pipeline] Query     : {query}")
    print(f"[pipeline] Enhanced  : {enhanced_query}")
    search_results = get_top_urls(enhanced_query, max_results=3)

    if not search_results:
        return {"answer": "No search results found.", "key_points": [], "sources": [], "error": None}

    # ── Step 5: Scrape content from top URLs ──────────────────────────────────
    urls     = [r["url"] for r in search_results]
    contents = scrape_multiple(urls)
    
    #-----------------------------falshback
    if "price" in query.lower():
        
        print("[pipeline] Price query detected — using snippets")

        contents = [r.get("snippet", "") for r in search_results]
    

    # Fallback to snippets if scraping failed entirely
    if not any(contents):
        print("[pipeline] Scraping failed — using DuckDuckGo snippets as fallback.")
        contents = [r.get("snippet", "") for r in search_results]

    # ── Step 6: Chunk content into small overlapping pieces ───────────────────
    chunks = chunk_multiple(contents, urls)

    if not chunks:
        return {"answer": "Could not extract usable content.", "key_points": [], "sources": [], "error": None}

    # ── Step 7: Build vector index from chunks ────────────────────────────────
    vector_store.build(chunks)

    # ── Step 8: Retrieve top-k most relevant chunks via semantic search ───────
    retrieved = vector_store.retrieve(enhanced_query, top_k=4)

    if not retrieved:
        retrieved = chunks[:4]   # fallback: take first 4 chunks directly
        print("[pipeline] Vector retrieval empty — using first chunks as fallback.")

    # ── Step 9: Build structured prompt ──────────────────────────────────────
    prompt = build_prompt(
        query              = query,
        retrieved_chunks   = retrieved,
        chat_history_text  = history_text
    )

    # ── Step 10: Generate answer ──────────────────────────────────────────────
    print("[pipeline] Generating answer...")
    raw_output = generate_answer(prompt)

    # ── Step 11: Parse structured output ─────────────────────────────────────
    answer, key_points = parse_llm_output(raw_output)

    # ── Step 12: Save this turn to memory ────────────────────────────────────
    chat_memory.add_turn(
        user_msg      = query,
        assistant_msg = answer
    )

    # ── Step 13: Format sources and return ───────────────────────────────────
    chunk_source_urls = extract_sources(retrieved, max_sources=3)

    # Match URLs back to titles from search results
    url_to_title = {r["url"]: r.get("title", "Source") for r in search_results}
    sources = [
        {"title": url_to_title.get(url, "Source"), "url": url}
        for url in chunk_source_urls
    ]

    # Fill in any missing titles using format_sources helper
    if not sources:
        sources = format_sources(search_results)

    print(f"[pipeline] Done. Answer length: {len(answer)} chars, Key points: {len(key_points)}")

    return {
        "answer":     answer,
        "key_points": key_points,
        "sources":    sources,
        "error":      None
    }





if __name__ == "__main__":
    # Test multi-turn conversation
    questions = [
        "What is machine learning?",
        "What are its main types?",         # follow-up — tests memory
        "Which one is used for images?",    # another follow-up
    ]

    for q in questions:
        print(f"\n{'='*60}")
        print(f"Q: {q}")
        result = get_answer(q)
        print(f"\nAnswer:\n{result['answer']}")
        if result["key_points"]:
            print("\nKey Points:")
            for kp in result["key_points"]:
                print(f"  - {kp}")
        print("\nSources:")
        for s in result["sources"]:
            print(f"  → {s['title']}: {s['url']}")