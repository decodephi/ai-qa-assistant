# modules/chunker.py
# Splits long scraped text into small overlapping chunks.
# Smaller chunks = more precise similarity search in the vector DB.
# Overlap ensures context is not lost at chunk boundaries.

# ── Constants ─────────────────────────────────────────────────────────────────
CHUNK_SIZE    = 400   # characters per chunk (fits well within flan-t5 limits)
CHUNK_OVERLAP = 80    # characters shared between consecutive chunks


def split_into_chunks(text: str, source_url: str = "") -> list[dict]:
    """
    Split a single text into overlapping chunks with attached metadata.

    Args:
        text:       The scraped article text to be chunked
        source_url: The URL this text came from (stored as metadata)

    Returns:
        List of dicts, each with:
            {
                "text":   str,   # the chunk content
                "source": str,   # origin URL
                "index":  int    # chunk position within this document
            }

    Example:
        text = "ABCDE..." (1000 chars)
        CHUNK_SIZE=400, OVERLAP=80
        → chunk 0: chars   0–400
        → chunk 1: chars 320–720   (starts 80 chars before chunk 0 ends)
        → chunk 2: chars 640–1000
    """
    text = text.strip()
    if not text:
        return []

    chunks = []
    start  = 0
    index  = 0
    step   = CHUNK_SIZE - CHUNK_OVERLAP  # advance by this much each iteration

    while start < len(text):
        end        = start + CHUNK_SIZE
        chunk_text = text[start:end].strip()

        if chunk_text:
            chunks.append({
                "text":   chunk_text,
                "source": source_url,
                "index":  index
            })
            index += 1

        start += step   # slide the window forward

    return chunks


def chunk_multiple(contents: list[str], urls: list[str]) -> list[dict]:
    """
    Chunk content from multiple scraped pages into one unified list.

    Args:
        contents: List of scraped text strings (one per URL)
        urls:     Matching list of source URLs

    Returns:
        Flat list of all chunk dicts across all pages

    Note:
        len(contents) must equal len(urls).
        If a content string is empty, it is skipped silently.
    """
    all_chunks = []

    for content, url in zip(contents, urls):
        if not content or not content.strip():
            print(f"[chunker] Skipping empty content for: {url}")
            continue

        page_chunks = split_into_chunks(content, source_url=url)
        all_chunks.extend(page_chunks)
        print(f"[chunker] {url} → {len(page_chunks)} chunks")

    print(f"[chunker] Total chunks created: {len(all_chunks)}")
    return all_chunks

'''    
if __name__ == "__main__":
    sample_text = "Artificial Intelligence is transforming industries. " * 20

    contents = [sample_text]
    urls = ["https://example.com/ai"]

    chunks = chunk_multiple(contents, urls)

    print("\nSample Output (first 2 chunks):\n")
    for c in chunks[:2]:
        print(c)
        
'''