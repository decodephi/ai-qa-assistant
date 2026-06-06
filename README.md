---
title: AI Q&A Assistant
emoji: ◈
colorFrom: gray
colorTo: gray
sdk: docker
app_port: 7860
pinned: false
license: mit
short_description: RAG chatbot — searches the web, answers with sources
---

# AI Q&A Assistant

Ask a question. Get an answer from the web — with sources.

---

## The Idea

Most AI chatbots answer from training data that goes stale. This one searches the web first, pulls the actual content, and then generates an answer grounded in real, current sources.

No hallucinations. Everything is cited.

---

## How It Works

```
Your question
    ↓
Search the web (DuckDuckGo)
    ↓
Scrape top results in parallel
    ↓
Split into chunks, embed with FAISS
    ↓
Retrieve most relevant chunks
    ↓
Generate answer via Groq (llama-3.3-70b)
    ↓
Answer + Key Points + Sources
```

This pattern is called **RAG — Retrieval-Augmented Generation**.

---

## Tech Stack

| Layer | Tool |
|---|---|
| Search | ddgs (DuckDuckGo) |
| Scraping | newspaper4k, BeautifulSoup |
| Embeddings | sentence-transformers (all-MiniLM-L6-v2) |
| Vector search | FAISS |
| LLM | Groq API (llama-3.3-70b) |
| Backend | FastAPI |
| Frontend | HTML + CSS + Vanilla JS |
| Memory | In-process deque (last 6 turns) |
| Deployment | Hugging Face Spaces (Docker) |


## Project Structure

```
rag-web-assistant/
├── Dockerfile              # HF Spaces Docker config
├── run.py                  # Local dev server
├── .env                    # Your GROQ_API_KEY (never committed)
├── requirements.txt
├── backend/
│   ├── api.py              # FastAPI routes
│   ├── pipeline.py         # RAG orchestrator
│   └── modules/
│       ├── search.py       # Web search with fallback
│       ├── scraper.py      # Content extraction
│       ├── chunker.py      # Text splitting
│       ├── vector_store.py # FAISS index
│       ├── memory.py       # Conversation memory
│       ├── prompt_builder.py
│       ├── llm.py          # Groq + local fallback
│       └── helpers.py
└── frontend/
    ├── index.html
    ├── css/style.css
    └── js/
        ├── app.js
        ├── api.js
        └── ui.js
```

---

## Local Setup

**1. Clone**
```bash
git clone https://github.com/decodephi/ai-qa-assistant.git
cd ai-qa-assistant
```

**2. Create virtual environment**
```bash
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Mac/Linux
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Add your Groq API key**

Create a `.env` file in the root:
```
GROQ_API_KEY=your_key_here
```


**5. Run**
```bash
python run.py
```

Open [http://localhost:8000](http://localhost:8000)

---

## Deploy on Hugging Face Spaces

1. Create a new Space → Select **Docker** SDK
2. Set `GROQ_API_KEY` as a **Space Secret** in Settings → Variables and secrets
3. Push this repo to the Space

---

## API

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/ask` | Send a question, get an answer |
| POST | `/api/clear` | Clear conversation memory |
| GET | `/api/history` | View chat history |
| GET | `/api/status` | Check active LLM backend |
| GET | `/docs` | Swagger UI |

---

## Notes

- The `.env` file is in `.gitignore` and will never be committed.
- DuckDuckGo has a rate limit. If it hits it, Bing scraping is used as fallback.
- First run downloads the embedding model (~80 MB). Subsequent runs are fast.
- On Hugging Face Spaces, the model cache is stored in `/tmp`.