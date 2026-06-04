# backend/modules/scraper.py
# Scrape article content — parallel execution for speed.

import re
import logging
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from bs4 import BeautifulSoup
from newspaper import Article

logger = logging.getLogger(__name__)

MAX_CHARS       = 2000
REQUEST_TIMEOUT = 8    # tighter timeout per URL
MAX_WORKERS     = 5    # parallel scrape threads

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}


def _clean(text: str) -> str:
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r" {2,}", " ", text)
    return text.strip()


def _newspaper(url: str) -> str:
    art = Article(url)
    art.download()
    art.parse()
    return _clean(art.text)


def _bs4(url: str) -> str:
    resp = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
        tag.decompose()
    paras = [p.get_text(" ", strip=True) for p in soup.find_all("p")]
    return _clean("\n\n".join(p for p in paras if len(p) > 40))


def extract_content(url: str) -> str:
    """
    Extract text from a URL.
    Tries newspaper4k first, falls back to requests + BS4.
    Returns empty string on failure.
    """
    if not url or not url.startswith("http"):
        return ""
    try:
        text = _newspaper(url)
        if text and len(text) > 100:
            return text[:MAX_CHARS]
    except Exception:
        pass
    try:
        text = _bs4(url)
        if text and len(text) > 100:
            return text[:MAX_CHARS]
    except Exception:
        pass
    logger.debug("[scraper] failed: %s", url)
    return ""


def scrape_multiple(urls: list[str]) -> list[str]:
    """
    Scrape all URLs in parallel using a thread pool.
    Returns a list aligned with the input URL order.
    Speed gain: ~3-5x faster than sequential scraping.
    """
    results: dict[int, str] = {}

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        futures = {pool.submit(extract_content, url): i for i, url in enumerate(urls)}
        for future in as_completed(futures):
            idx = futures[future]
            try:
                results[idx] = future.result()
            except Exception as exc:
                logger.debug("[scraper] thread error idx=%d: %s", idx, exc)
                results[idx] = ""

    return [results.get(i, "") for i in range(len(urls))]
