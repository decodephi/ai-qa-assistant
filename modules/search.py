# search.py - Fetch top URLs using DuckDuckGo Search

from duckduckgo_search import DDGS


def get_top_urls(query: str, max_results: int = 3) -> list[dict]:
    """
    Search DuckDuckGo and return top N results.

    Args:
        query: User's search query
        max_results: Number of results to fetch (default: 3)

    Returns:
        List of dicts with 'title', 'url', 'snippet'
    """
    results = []

    try:
        with DDGS(headers={"User-Agent": "Mozilla/5.0"}) as ddgs:
            search_results = ddgs.text(query, max_results=max_results)
            for r in search_results:
                results.append({
                    "title": r.get("title", "No title"),
                    "url": r.get("href", ""),
                    "snippet": r.get("body", "")
                })
    except Exception as e:
        print(f"[search] Error fetching search results: {e}")

    return results

#To cheak the result , we are geeting or not 


'''
if __name__ == "__main__":
    query = input("Enter your search query: ")
    
    results = get_top_urls(query)

    print("\nTop Results:\n")
    for i, r in enumerate(results, 1):
        print(f"{i}. {r['title']}")
        print(f"   URL: {r['url']}")
        print(f"   Snippet: {r['snippet']}\n")
'''  