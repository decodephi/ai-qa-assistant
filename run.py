# run.py — Single entry point to start the RAG Web Assistant server.
#
# Usage:
#   python run.py
#
# Then open: http://localhost:8000

import os
import sys
import uvicorn
from dotenv import load_dotenv

# Force UTF-8 output on Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Load .env BEFORE importing backend (so GROQ_API_KEY is available)
load_dotenv()

if __name__ == "__main__":
    print("=" * 60)
    print("  RAG Web Assistant  v2.0")
    print("=" * 60)

    groq_key = os.getenv("GROQ_API_KEY", "")
    if groq_key:
        print("  [OK] Groq API key loaded -- using llama-3.3-70b-versatile")
    else:
        print("  [WARN] No GROQ_API_KEY -- falling back to local flan-t5-large")

    print("  Server starting at http://localhost:8000")
    print("  API docs at        http://localhost:8000/docs")
    print("=" * 60)

    uvicorn.run(
        "backend.api:app",
        host      = "0.0.0.0",
        port      = 8000,
        reload    = False,
        log_level = "info",
    )
