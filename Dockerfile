# ── Hugging Face Spaces — FastAPI + RAG Web Assistant ─────────────────────────
# SDK: Docker   Port: 7860   User: non-root (UID 1000, required by HF)

FROM python:3.11-slim

# ── System deps ───────────────────────────────────────────────────────────────
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        libxml2-dev \
        libxslt1-dev \
        libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# ── Non-root user (Hugging Face requirement) ──────────────────────────────────
RUN useradd -m -u 1000 user
USER user

ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

# ── Redirect ML model caches to /tmp (writable in HF Spaces) ─────────────────
ENV HF_HOME=/tmp/hf_home \
    TRANSFORMERS_CACHE=/tmp/transformers_cache \
    SENTENCE_TRANSFORMERS_HOME=/tmp/sentence_transformers \
    XDG_CACHE_HOME=/tmp/.cache

WORKDIR $HOME/app

# ── Install Python dependencies ───────────────────────────────────────────────
COPY --chown=user requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ── Copy application source ───────────────────────────────────────────────────
COPY --chown=user . .

# ── Expose the port HF Spaces expects ────────────────────────────────────────
EXPOSE 7860

# ── Launch FastAPI via uvicorn on port 7860 ───────────────────────────────────
CMD ["python", "-m", "uvicorn", "backend.api:app", "--host", "0.0.0.0", "--port", "7860", "--log-level", "info"]
