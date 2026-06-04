# backend/modules/helpers.py
# Utility functions shared across the pipeline.


def combine_contents(contents: list[str], separator: str = "\n\n---\n\n") -> str:
    """Join multiple scraped content strings into one context block."""
    valid = [c.strip() for c in contents if c and c.strip()]
    return separator.join(valid)


def format_sources(search_results: list[dict]) -> list[dict]:
    """
    Filter and format source info for display.

    Returns:
        List of {"title": str, "url": str} dicts from valid search results.
    """
    sources = []
    for r in search_results:
        url   = r.get("url", "").strip()
        title = r.get("title", "Untitled").strip()
        if url.startswith("http"):
            sources.append({"title": title, "url": url})
    return sources


def is_valid_query(query: str) -> bool:
    """Return True if the query is non-empty and at least 3 characters long."""
    return bool(query and query.strip() and len(query.strip()) > 2)
