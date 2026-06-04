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



---

## Setup

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
pip install ddgs
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

I built this application through `Vibe Coding`. If you feel there is a need for light to make it perfect, you can do it 🤗. @decodephi

---

## Notes

- The `.env` file is in `.gitignore` and will never be committed.
- DuckDuckGo has a rate limit. If it hits it, Bing scraping is used as fallback.
- First run downloads the embedding model (~80 MB). Subsequent runs are fast.
