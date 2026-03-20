#

def combine_contents(contents: list[str], separator: str = "\n\n---\n\n") -> str:
    """
    Join multiple scraped content strings into one context block.

    Args:
        contents: List of text strings from scraped pages
        separator: String used to separate each content block

    Returns:
        Single combined context string
    """
    valid = [c.strip() for c in contents if c and c.strip()]
    return separator.join(valid)
#

def format_sources(search_results: list[dict]) -> list[dict]:
    """
    Filter and format source info for display.

    Args:
        search_results: Raw results from DuckDuckGo (list of dicts)

    Returns:
        Cleaned list with 'title' and 'url' keys only
    """
    sources = []
    for r in search_results:
        url = r.get("url", "").strip()
        title = r.get("title", "Untitled").strip()
        if url.startswith("http"):
            sources.append({"title": title, "url": url})
    return sources

#
def is_valid_query(query: str) -> bool:
    """
    Check if the user's query is non-empty and meaningful.

    Args:
        query: Input text from user

    Returns:
        True if valid, False otherwise
    """
    return bool(query and query.strip() and len(query.strip()) > 2)


