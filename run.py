# run.py — Single entry point to start the RAG Web Assistant server.
#
# Usage (local):
#   python run.py
#
# The server automatically adapts the port:
#   - Local:              http://localhost:8000
#   - Hugging Face Spaces / Docker: port 7860 (set via PORT env var)

import os
import sys
import uvicorn
from dotenv import load_dotenv

# Force UTF-8 output on Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Load .env BEFORE importing backend (so GROQ_API_KEY is available)
load_dotenv()

# ── Port selection ─────────────────────────────────────────────────────────────
# Hugging Face Spaces uses port 7860 by default.
# Override with PORT env var if needed; fallback to 8000 locally.
PORT = int(os.getenv("PORT", 7860 if os.getenv("SPACE_ID") else 8000))

if __name__ == "__main__":
    print("=" * 60)
    print("  RAG Web Assistant  v2.0")
    print("=" * 60)

    groq_key = os.getenv("GROQ_API_KEY", "")
    if groq_key:
        print("  [OK] Groq API key loaded -- using llama-3.3-70b-versatile")
    else:
        print("  [WARN] No GROQ_API_KEY -- falling back to local flan-t5-large")

    print(f"  Server starting at http://localhost:{PORT}")
    print(f"  API docs at        http://localhost:{PORT}/docs")
    print("=" * 60)

    uvicorn.run(
        "backend.api:app",
        host      = "0.0.0.0",
        port      = PORT,
        reload    = False,
        log_level = "info",
    )
