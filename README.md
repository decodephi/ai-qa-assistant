# 🔎 AI Web Q&A Assistant

An end-to-end AI-powered question-answering system that retrieves real-time information from the web, processes it, and generates contextual answers along with source references.

---

## 🚀 Features

- 🔍 Web search using DuckDuckGo
- 📰 Content extraction from real web pages
- 🧠 Answer generation using HuggingFace LLM (flan-t5-base)
- 🔗 Source attribution (top 3 links displayed)
- ⚡ Fully local and free (no API keys required)
- 🧩 Modular and clean architecture

---

## 🧠 How It Works
User Query
    ↓
DuckDuckGo Search
    ↓
Extract Top 3 URLs
    ↓
Scrape Article Content
    ↓
Combine Context
    ↓
LLM (flan-t5-base)
    ↓
Answer + Source Links



---

## ⚙️ Tech Stack

- Python 3.12
- Streamlit
- DuckDuckGo Search
- Newspaper4k (or newspaper3k)
- HuggingFace Transformers
- PyTorch

---

## 📦 Installation

### 1. Clone the repository
```bash
git clone https://github.com/your-username/rag-web-assistant.git
cd rag-web-assistant


What is quantum computing?


Answer:
Quantum computing is a type of computing that uses quantum bits...

Sources:
- https://example1.com
- https://example2.com
- https://example3.com