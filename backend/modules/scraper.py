# backend/modules/scraper.py
# Scrape article content from URLs using newspaper4k with requests fallback.

import re
import logging
import requests
from bs4 import BeautifulSoup
from newspaper import Article

logger = logging.getLogger(__name__)

MAX_CHARS    = 2500   # chars per page (increased for better context)
REQUEST_TIMEOUT = 10  # seconds

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}


def _clean_text(text: str) -> str:
    """Normalize whitespace in extracted text."""
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r" {2,}", " ", text)
    return text.strip()


def _scrape_with_newspaper(url: str) -> str:
    """Primary: use newspaper4k to extract article text."""
    article = Article(url)
    article.download()
    article.parse()
    return _clean_text(article.text)


def _scrape_with_requests(url: str) -> str:
    """Fallback: raw requests + BeautifulSoup paragraph extraction."""
    resp = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    # Remove noisy tags
    for tag in soup(["script", "style", "nav", "footer", "header", "aside", "form"]):
        tag.decompose()

    # Collect paragraphs
    paragraphs = [p.get_text(separator=" ", strip=True) for p in soup.find_all("p")]
    text = "\n\n".join(p for p in paragraphs if len(p) > 40)
    return _clean_text(text)


def extract_content(url: str) -> str:
    """
    Download and parse article content from a URL.

    Tries newspaper4k first; falls back to requests+BS4.

    Returns:
        Cleaned article text (truncated to MAX_CHARS), or empty string on failure.
    """
    if not url or not url.startswith("http"):
        logger.debug("[scraper] Invalid URL skipped: %s", url)
        return ""

    # ── Attempt 1: newspaper4k ─────────────────────────────────────────────────
    try:
        text = _scrape_with_newspaper(url)
        if text and len(text) > 100:
            logger.debug("[scraper] newspaper4k OK: %s (%d chars)", url, len(text))
            return text[:MAX_CHARS]
    except Exception as exc:
        logger.debug("[scraper] newspaper4k failed for %s: %s", url, exc)

    # ── Attempt 2: requests + BeautifulSoup ───────────────────────────────────
    try:
        text = _scrape_with_requests(url)
        if text and len(text) > 100:
            logger.debug("[scraper] BS4 fallback OK: %s (%d chars)", url, len(text))
            return text[:MAX_CHARS]
    except Exception as exc:
        logger.debug("[scraper] BS4 fallback failed for %s: %s", url, exc)

    logger.warning("[scraper] Could not extract content from: %s", url)
    return ""


def scrape_multiple(urls: list[str]) -> list[str]:
    """
    Scrape content from multiple URLs concurrently (sequential for simplicity).

    Returns:
        List of non-empty content strings (same order as input URLs).
    """
    contents = []
    for url in urls:
        content = extract_content(url)
        contents.append(content)  # keep empty strings to preserve URL index alignment
    return contents
