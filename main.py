# main.py - Core pipeline: query → search → scrape → LLM → answer + sources

from modules.search import get_top_urls
from modules.scraper import scrape_multiple
from modules.llm import generate_answer
from modules.helpers import combine_contents, format_sources, is_valid_query


def get_answer(query: str) -> dict:
    """
    End-to-end pipeline: take a user query, search the web,
    extract content, generate an LLM answer, and return results.

    Args:
        query: The user's question string

    Returns:
        dict with keys:
            - 'answer' (str): LLM-generated answer
            - 'sources' (list[dict]): List of {'title', 'url'} dicts
            - 'error' (str | None): Error message if something went wrong
    """

    # --- Validate input ---
    if not is_valid_query(query):
        return {
            "answer": "",
            "sources": [],
            "error": "Please enter a valid question."
        }

    # --- Step 1: Get top 3 URLs from DuckDuckGo ---
    print(f"[pipeline] Searching for: {query}")
    search_results = get_top_urls(query, max_results=3)

    if not search_results:
        return {
            "answer": "No search results found for your query.",
            "sources": [],
            "error": None
        }

    # --- Step 2: Scrape content from each URL ---
    urls = [r["url"] for r in search_results]
    print(f"[pipeline] Scraping {len(urls)} URLs...")
    contents = scrape_multiple(urls)

    # --- Step 3: Combine content into a single context block ---
    context = combine_contents(contents)

    if not context:
        # Fall back to using DuckDuckGo snippets if scraping fails
        print("[pipeline] Scraping yielded no content, falling back to snippets.")
        snippets = [r.get("snippet", "") for r in search_results]
        context = combine_contents(snippets)

    # --- Step 4: Generate answer using LLM ---
    print("[pipeline] Generating answer...")
    answer = generate_answer(query, context)

    # --- Step 5: Format and return answer + sources ---
    sources = format_sources(search_results)

    return {
        "answer": answer,
        "sources": sources,
        "error": None
    }


# ── Quick CLI test ──────────────────────────────────────────────────────────
if __name__ == "__main__":
    test_query = "What is quantum computing?"
    result = get_answer(test_query)
    print("\n=== ANSWER ===")
    print(result["answer"])
    print("\n=== SOURCES ===")
    for s in result["sources"]:
        print(f"  - {s['title']}: {s['url']}")