from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import RetrievalQA
from FlagEmbedding import FlagReranker
import torch, os
from dotenv import load_dotenv
from .ingest import embeddings
from langchain_chroma import Chroma
from dotenv import load_dotenv

# Paths
load_dotenv()
DB_DIR = os.getenv("DB_DIR")
SEARCH_TYPE=os.getenv("SEARCH_TYPE")
# ================================
# 1) Setup Vectorstore + Retriever
# ================================
vectorstore = Chroma(
    persist_directory=DB_DIR,
    embedding_function=embeddings
)

# Base retriever (fast cosine similarity)
retriever = vectorstore.as_retriever(
    search_type=SEARCH_TYPE,
    search_kwargs={"k": 10}
)

# ================================
# 2) Setup Reranker
# ================================
reranker = FlagReranker("BAAI/bge-reranker-base", use_fp16=True)

# ================================
# Helpers: BEFORE/AFTER rerank views
# ================================
def retrieve_candidates(query: str, k: int = 10):
    """
    Use Chroma retriever to get k candidates.
    Returns a list of dicts with rank, content, metadata, and the original doc.
    """
    docs = retriever.get_relevant_documents(query)
    candidates = []
    for i, doc in enumerate(docs, start=1):
        candidates.append({
            "initial_rank": i,
            "content": doc.page_content,
            "metadata": dict(doc.metadata) if doc.metadata else {},
            "doc": doc
        })
    return candidates

def rerank_candidates(query: str, candidates, top_k: int = 5):
    """
    Rerank candidates using FlagReranker and return top_k best.
    Adds:
      - rerank_score_raw   : raw model score (logit)
      - rerank_score_norm  : sigmoid-normalized score in [0, 1]
      - rerank_score       : alias to normalized score (for backward compatibility)
    """
    if not candidates:
        return []

    # Build [query, content] pairs for the reranker
    pairs = [[query, c["content"]] for c in candidates]
    raw_scores = reranker.compute_score(pairs)  # list[float]

    reranked = []
    for cand, score in zip(candidates, raw_scores):
        norm = float(torch.sigmoid(torch.tensor(score)).item())
        item = {**cand}
        item["rerank_score_raw"] = float(score)
        item["rerank_score_norm"] = norm
        item["rerank_score"] = norm  # keep old key name for compatibility
        reranked.append(item)

    # Sort by normalized score (desc) and keep top_k
    reranked.sort(key=lambda x: x["rerank_score_norm"], reverse=True)
    return reranked[:top_k]




# ================================
# 4) Main
# ================================
if __name__ == "__main__":
    # Keep retrieval query short and focused
    question_text = "What is NLP ?"

    # BEFORE reranking
    candidates = retrieve_candidates(question_text, k=10)
    print("\n📌 BEFORE RERANKING\n")
    for c in candidates:
        print(f"Rank {c['initial_rank']}")
        print(f"📄 {c['content']}...")
        print(f"📌 {c['metadata']}")
        print("---")

    # AFTER reranking
    reranked = rerank_candidates(question_text, candidates, top_k=5)
    print("\n📌 AFTER RERANKING\n")
    for rank, c in enumerate(reranked, start=1):
        print(f"Rank {rank} | Score={c['rerank_score']:.4f} (was {c['initial_rank']})")
        print(f"📄 {c['content']}...")
        print(f"📌 {c['metadata']}")
        print("---")

