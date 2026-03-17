# scraper.py - Extract article content from URLs using newspaper4k
# newspaper4k is the actively maintained fork of newspaper3k — same API, Python 3.12 compatible

from newspaper import Article   # newspaper4k uses the same import as newspaper3k
import re


MAX_CHARS = 1500  # Limit content per article to avoid huge LLM inputs


def extract_content(url: str) -> str:
    """
    Download and parse article content from a URL.

    Args:
        url: Web page URL to scrape

    Returns:
        Cleaned article text (truncated), or empty string on failure
    """
    if not url or not url.startswith("http"):
        print(f"[scraper] Invalid URL skipped: {url}")
        return ""

    try:
        article = Article(url)
        article.download()
        article.parse()

        text = article.text.strip()

        # Remove excessive whitespace/newlines
        text = re.sub(r'\n{3,}', '\n\n', text)
        text = re.sub(r' {2,}', ' ', text)

        if not text:
            print(f"[scraper] Empty content from: {url}")
            return ""

        # Truncate to limit input size
        return text[:MAX_CHARS]

    except Exception as e:
        print(f"[scraper] Failed to extract from {url}: {e}")
        return ""


def scrape_multiple(urls: list[str]) -> list[str]:
    """
    Scrape content from multiple URLs.

    Args:
        urls: List of URLs to scrape

    Returns:
        List of non-empty content strings
    """
    contents = []
    for url in urls:
        content = extract_content(url)
        if content:
            contents.append(content)
    return contents


'''   

if __name__ == "__main__":
    test_urls = [
        "https://en.wikipedia.org/wiki/Artificial_intelligence",
        "https://www.ibm.com/topics/artificial-intelligence"
    ]

    print("Scraping content...\n")

    results = scrape_multiple(test_urls)

    for i, content in enumerate(results, 1):
        print(f"\n--- Article {i} ---\n")
        print(content[:500])  # show preview only
        
''' 