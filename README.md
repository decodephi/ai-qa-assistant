# AI Q&A Assistant

An intelligent Retrieval-Augmented Generation (RAG) chatbot that searches the web in real time, retrieves relevant information, and generates grounded answers with source citations.

Unlike traditional AI chatbots that rely solely on pre-trained knowledge, this application performs live web retrieval before generating responses, enabling more accurate and up-to-date answers.

<img width="1880" height="896" alt="image" src="https://github.com/user-attachments/assets/1f4ab024-0081-4e7d-8b2b-efcf27ac7b54" />

## Live Demo

**Application:** https://decodephi-home-chat.hf.space/

---

# Features

* Real-time web search using DuckDuckGo
* Parallel article extraction from multiple sources
* Retrieval-Augmented Generation (RAG) pipeline
* Semantic search using vector embeddings
* Context-aware answer generation
* Source attribution and citations
* Conversation memory for multi-turn interactions
* Fast response generation powered by Groq
* Clean and responsive web interface

---

# System Architecture

```text
User Question
      │
      ▼
DuckDuckGo Search
      │
      ▼
Fetch Top Search Results
      │
      ▼
Article Extraction
(Newspaper4k + BeautifulSoup)
      │
      ▼
Text Chunking
      │
      ▼
Sentence Embeddings
(all-MiniLM-L6-v2)
      │
      ▼
FAISS Vector Index
      │
      ▼
Similarity Retrieval
      │
      ▼
Context Construction
      │
      ▼
Groq LLM
(llama-3.3-70b)
      │
      ▼
Generated Answer
+ Key Insights
+ Source Citations
```

---

# Why RAG?

Large Language Models are limited by the data available during training and may produce outdated or hallucinated responses.

Retrieval-Augmented Generation (RAG) solves this problem by:

1. Retrieving relevant information from external sources.
2. Selecting the most useful context.
3. Providing the retrieved context to the language model.
4. Generating answers grounded in actual source material.

This approach significantly improves factual accuracy and transparency.

---

# ⚙️ Tech Stack

| Category        | Technology                     |
| --------------- | ------------------------------ |
| Search Engine   | DuckDuckGo (ddgs)              |
| Web Scraping    | newspaper4k, BeautifulSoup     |
| Embeddings      | sentence-transformers          |
| Embedding Model | all-MiniLM-L6-v2               |
| Vector Database | FAISS                          |
| LLM Provider    | Groq                           |
| Language Model  | llama-3.3-70b                  |
| Backend         | FastAPI                        |
| Frontend        | HTML, CSS, JavaScript          |
| Memory          | In-memory conversation history |
| Deployment      | Hugging Face Spaces (Docker)   |



---

# 🔄 Workflow

### Step 1: User Query

The user submits a question through the web interface.

### Step 2: Web Search

DuckDuckGo retrieves relevant search results.

### Step 3: Content Extraction

Articles are downloaded and parsed using:

* newspaper4k
* BeautifulSoup

### Step 4: Text Processing

Retrieved content is:

* Cleaned
* Split into chunks
* Prepared for embedding generation

### Step 5: Semantic Retrieval

Each chunk is embedded using:

```text
all-MiniLM-L6-v2
```

Embeddings are indexed in FAISS for similarity search.

### Step 6: Context Retrieval

The most relevant chunks are selected based on semantic similarity to the user's question.

### Step 7: Answer Generation

The retrieved context is sent to:

```text
Groq API
↓
llama-3.3-70b
```

to generate a grounded response.

### Step 8: Source Attribution

The final response includes source references used during retrieval.

---

# Local Development

## Clone Repository

```bash
git clone https://github.com/decodephi/ai-qa-assistant.git

cd ai-qa-assistant
```

## Create Virtual Environment

### Windows

```bash
python -m venv venv

venv\Scripts\activate
```

## Install Dependencies

```bash
pip install -r requirements.txt
```

## Configure Environment Variables

Create a `.env` file:

```env
GROQ_API_KEY=your_groq_api_key
```


---

# 🐳 Docker Deployment

Build Image

```bash
docker build -t ai-qa-assistant
```

Run Container

```bash
docker run -p 7860:7860 ai-qa-assistant
```

---

# 🤗 Deploy to Hugging Face Spaces

### 1. Create a New Space

* Open Hugging Face Spaces
* Select **Docker** SDK

### 2. Configure Secrets

Add:

```text
GROQ_API_KEY
```

under:

```text
Settings
→ Variables and Secrets
```

### 3. Push Repository

```bash
git add.
git commit -m "Initial deployment."
git push
```

The application will be automatically built and deployed.

---

# Future Improvements

* Persistent chat history
* User authentication
* Streaming responses
* Hybrid search (Keyword + Semantic)
* Multi-source ranking
* Redis caching
* PostgreSQL integration
* Vector database migration (Qdrant/Pinecone)
* PDF and document ingestion
* Agentic search workflows

---

# Learning Outcomes

This project demonstrates practical experience with:

* Retrieval-Augmented Generation (RAG)
* Information Retrieval
* Semantic Search
* Vector Databases
* LLM Integration
* Web Scraping
* FastAPI Development
* Docker Deployment
* AI System Design

---

# 👨‍💻 Author

**Pranab Samanta**

* GitHub: https://github.com/decodephi
* LinkedIn: https://www.linkedin.com/in/pranab-samanta-a606922b0/
* X (Twitter): https://x.com/decodephi

---

# 📄 License

This project is licensed under the MIT License.



