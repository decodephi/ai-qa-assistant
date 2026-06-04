# backend/modules/chunker.py
# Split scraped text into overlapping chunks for vector indexing.

import logging

logger = logging.getLogger(__name__)

CHUNK_SIZE    = 500   # chars per chunk (increased for better context)
CHUNK_OVERLAP = 100   # overlap between consecutive chunks


def split_into_chunks(text: str, source_url: str = "") -> list[dict]:
    """
    Split a single text into overlapping chunks with attached metadata.

    Args:
        text:       The scraped article text to chunk
        source_url: The URL this text came from (stored as metadata)

    Returns:
        List of dicts: [{"text": str, "source": str, "index": int}, ...]
    """
    text = text.strip()
    if not text:
        return []

    chunks = []
    start  = 0
    index  = 0
    step   = CHUNK_SIZE - CHUNK_OVERLAP

    while start < len(text):
        chunk_text = text[start : start + CHUNK_SIZE].strip()
        if chunk_text:
            chunks.append({
                "text":   chunk_text,
                "source": source_url,
                "index":  index,
            })
            index += 1
        start += step

    return chunks


def chunk_multiple(contents: list[str], urls: list[str]) -> list[dict]:
    """
    Chunk content from multiple scraped pages into one unified list.

    Args:
        contents: List of scraped text strings (one per URL)
        urls:     Matching list of source URLs (same length as contents)

    Returns:
        Flat list of all chunk dicts across all pages.
    """
    all_chunks: list[dict] = []

    for content, url in zip(contents, urls):
        if not content or not content.strip():
            logger.debug("[chunker] Skipping empty content for: %s", url)
            continue
        page_chunks = split_into_chunks(content, source_url=url)
        all_chunks.extend(page_chunks)
        logger.debug("[chunker] %s → %d chunks", url, len(page_chunks))

    logger.info("[chunker] Total chunks created: %d", len(all_chunks))
    return all_chunks
