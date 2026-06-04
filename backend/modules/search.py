# backend/modules/search.py
# Robust web search using ddgs (successor to duckduckgo-search) with Bing fallback.

import time
import random
import logging
import requests
from bs4 import BeautifulSoup
from ddgs import DDGS

logger = logging.getLogger(__name__)

# ── Constants ─────────────────────────────────────────────────────────────────
MAX_RETRIES   = 3
BASE_DELAY    = 2.0
MAX_DELAY     = 10.0
BING_ENDPOINT = "https://www.bing.com/search"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}


def _make_result(title: str, url: str, snippet: str) -> dict:
    return {"title": title or "No title", "url": url or "", "snippet": snippet or ""}


# ── Backend 1: ddgs ────────────────────────────────────────────────────────────
def _ddgs_search(query: str, max_results: int) -> list[dict]:
    """Search using the ddgs library (successor to duckduckgo-search)."""
    results = []
    with DDGS() as ddgs:
        for r in ddgs.text(query, max_results=max_results):
            results.append(_make_result(
                title   = r.get("title", ""),
                url     = r.get("href", ""),
                snippet = r.get("body", ""),
            ))
    return results


# ── Backend 2: Bing scrape ─────────────────────────────────────────────────────
def _bing_search(query: str, max_results: int) -> list[dict]:
    """Scrape Bing as last-resort fallback (no API key needed)."""
    results = []
    try:
        resp = requests.get(
            BING_ENDPOINT,
            params={"q": query, "count": max_results},
            headers=HEADERS,
            timeout=12,
        )
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        for li in soup.select("li.b_algo")[:max_results]:
            title_el   = li.select_one("h2 a")
            snippet_el = li.select_one(".b_caption p")
            if title_el:
                results.append(_make_result(
                    title   = title_el.get_text(strip=True),
                    url     = title_el.get("href", ""),
                    snippet = snippet_el.get_text(strip=True) if snippet_el else "",
                ))
    except Exception as exc:
        logger.warning("[search] Bing fallback error: %s", exc)
    return results


# ── Public API ─────────────────────────────────────────────────────────────────
def get_top_urls(query: str, max_results: int = 5) -> list[dict]:
    """
    Search the web and return top N results.

    Strategy:
      1. ddgs (DuckDuckGo successor library) — primary
      2. Bing scrape                          — fallback

    Returns:
        List of dicts: [{"title": str, "url": str, "snippet": str}, ...]
    """
    # ── Primary: ddgs with retry ───────────────────────────────────────────────
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            logger.info("[search] ddgs attempt=%d query=%r", attempt, query)
            results = _ddgs_search(query, max_results)
            if results:
                logger.info("[search] Got %d results via ddgs", len(results))
                return results
            logger.warning("[search] ddgs returned empty results (attempt %d)", attempt)
        except Exception as exc:
            err = str(exc).lower()
            is_rate_limit = any(k in err for k in ("ratelimit", "202", "429", "rate limit", "blocked"))

            if is_rate_limit and attempt < MAX_RETRIES:
                delay = min(BASE_DELAY * (2 ** (attempt - 1)) + random.uniform(0, 1.5), MAX_DELAY)
                logger.warning("[search] Rate-limited (attempt %d/%d). Retrying in %.1fs...", attempt, MAX_RETRIES, delay)
                time.sleep(delay)
            else:
                logger.warning("[search] ddgs attempt %d failed: %s", attempt, exc)
                break

    # ── Fallback: Bing ─────────────────────────────────────────────────────────
    logger.warning("[search] ddgs exhausted — trying Bing fallback.")
    results = _bing_search(query, max_results)
    if results:
        logger.info("[search] Got %d results via Bing", len(results))
        return results

    logger.error("[search] All search backends failed for query: %r", query)
    return []
