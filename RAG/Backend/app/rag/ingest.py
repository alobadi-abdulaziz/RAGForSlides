import os
import json
from langchain.schema import Document
#from langchain_community.vectorstores import FAISS
#from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from dotenv import load_dotenv

# Paths
load_dotenv()
E5_MODEL = os.getenv("E5_MODEL")
CACHE_DIR = os.getenv("CACHE_DIR")
json_dir = os.getenv("json_dir")
DB_DIR = os.getenv("DB_DIR")



def load_documents(json_dir: str):
    """
    Load all .json files from a directory and convert them into LangChain Document objects.
    """
    documents = []

    # 1. Loop over all .json files in the folder
    for filename in os.listdir(json_dir):
        if not filename.endswith(".json"):
            continue  # skip non-JSON files

        filepath = os.path.join(json_dir, filename)

        # 2. Load JSON
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        # 3. Convert slides → Documents
        for slide in data["slides"]:
            documents.append(
                Document(
                    page_content=slide["text"],
                    metadata={
                        "course": data["course_name"],
                        "chapter": data["chapter_name"],
                        "page": slide["page_number"],
                        "title": slide["title"],
                        "file": filename,
                    },
                )
            )

    print(f"✅ Loaded {len(documents)} slides across {len(os.listdir(json_dir))} files")
    return documents

# 4. Embed + store in Chroma

#embeddings 

embeddings = HuggingFaceEmbeddings(
    model_name=E5_MODEL,  # which embedding model to load
    model_kwargs={"device": "cpu"},                       # run on CPU (or "cuda" for GPU)
    encode_kwargs={"normalize_embeddings": True, "prompt": "passage:"},  # E5 model expects prefixes ("passage:" for docs, "query:" for user questions)
    cache_folder= CACHE_DIR                             # local cache so it won’t re-download
)


if __name__ == "__main__":
    # Load documents
    documents = load_documents(json_dir)

    #  5 Create vector store (Chroma)
    vectorstore = Chroma.from_documents(
        documents,
        embedding=embeddings,
        persist_directory=DB_DIR#here to store the DB
    )
    vectorstore.persist()  # save to disk
    print("✅ Created and persisted vectorstore")

