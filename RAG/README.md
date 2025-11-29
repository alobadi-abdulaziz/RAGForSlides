# RAG over Slides — README

A Dockerized Retrieval-Augmented Generation (RAG) system that indexes your course slides (PDF/PPTX) and lets you query them via a FastAPI service.

---

## 📂 Project Structure

```
rag-slides/
├─ .env.sample          # Environment variables (copy to .env)
├─ docker-compose.yml   # Compose stack (API + Qdrant)
├─ Dockerfile           # API service container
├─ Makefile             # Dev commands (up/ingest/query)
├─ requirements.txt     # Python dependencies
├─ data/
│  ├─ slides/           # Put your PDFs/PPTX here (organized by course)
│  └─ cache/            # OCR/temp artifacts (gitignored)
└─ app/
   ├─ main.py           # FastAPI app with /ingest & /query endpoints
   ├─ ingest.py         # Slide parsing + vector indexing
   ├─ rag.py            # Retrieval + answer generation
   ├─ models.py         # Pydantic schemas
   ├─ parsing/          # Extract text from PDF & PPTX
   └─ utils.py          # Helper functions
```

---

## ⚙️ Setup

1. **Clone repo & enter folder**

```bash
git clone YOUR_REPO_URL rag-slides
cd rag-slides
```

2. **Environment**

```bash
cp .env.sample .env
# edit .env (embedding model, OpenAI key if desired)
```

3. **Start stack**

```bash
make up
```

4. **Ingest slides**

```bash
# index everything under data/slides/
make ingest
```

5. **Query**

```bash
make query
# or use curl:
curl -X POST http://localhost:8000/query \
 -H 'Content-Type: application/json' \
 -d '{"question":"What is a support vector?","top_k":5}' | jq .
```

6. **Docs UI**
   Open Swagger UI at: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 🔗 Endpoints

### `POST /ingest`

**Body**:

```json
{
  "root_dir": "/app/data/slides",
  "glob": "**/*"
}
```

**Response**: `{ "ingested": N }`

### `POST /query`

**Body**:

```json
{
  "question": "Explain the kernel trick.",
  "top_k": 6,
  "with_answer": true
}
```

**Response**:

```json
{
  "answer": "...",
  "citations": [
    {"slide_no": 7, "course": "CS364", "lecture": "CH7", "path": "/app/data/slides/CS364/CH7-SVM.pptx"}
  ]
}
```

---

## 📚 Pipeline

### 1. Ingestion

* Parse PDFs/PPTX per slide
* Add metadata: `course`, `lecture`, `slide_no`
* Chunk long slides (\~900 tokens, 120 overlap)
* Embed with SentenceTransformers (default: `all-MiniLM-L6-v2`)
* Upsert to Qdrant vector DB

### 2. Retrieval

* Encode user question → search Qdrant (cosine similarity)
* Return top-k relevant chunks
* (Optional) rerank with cross-encoder for precision

### 3. Answering

* If `OPENAI_API_KEY` provided: generate abstractive answers using context, citing slide numbers.
* Otherwise: return top passages (extractive mode).

### 4. Output

* JSON response: `answer` + `citations` (with slide\_no, course, lecture, file path).

---

## 🛠 Makefile Commands

```bash
make up       # Start Qdrant + API
make down     # Stop stack
make ingest   # Ingest all slides
make query    # Run test query
make rebuild  # Rebuild containers clean
```

---

## 🚀 Deployment

* Works locally with Docker Compose.
* Push to GitHub, then deploy with services like **Railway**, **Render**, or **AWS ECS**.
* Ensure Qdrant storage is persisted (see `volumes:` in docker-compose).

---

## 📈 Extensions

* Hybrid search (BM25 + embeddings)
* Slide thumbnails in frontend
* Reranker for better results
* Logging queries/answers for evaluation
* GitHub Actions to auto-ingest new slides

---

## 📝 License

MIT — free to adapt and extend for your coursework or team.
