import os
import json
import pickle
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings

RAW_DIR = "data/raw"
INDEX_DIR = "data/faiss_index"

TOPICS = [
    "pocso_act",
    "consumer_protection_act",
    "cyber_crime_laws",
    "rti_act",
    "gst_registration",
]


def load_raw_text(topic_key: str) -> str:
    """Load raw scraped text for a topic."""
    path = os.path.join(RAW_DIR, f"{topic_key}.txt")
    if not os.path.exists(path):
        print(f"  [WARN] Raw file not found: {path} — run scraper.py first")
        return ""
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def build_index_for_topic(topic_key: str, embeddings):
    """Chunk text and build a FAISS vector index for one topic."""
    print(f"\n{'='*50}")
    print(f"Processing: {topic_key}")

    text = load_raw_text(topic_key)
    if not text:
        return False

    # Split into overlapping chunks so context is preserved across boundaries
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,  # ~00 chars per chunk
        chunk_overlap=100,  # 100 char overlap so nothing is cut off abruptly
        separators=["\n\n", "\n", ". ", " "],
    )
    chunks = splitter.split_text(text)
    print(f"  Split into {len(chunks)} chunks")

    # Add topic metadata to each chunk so we can trace it later
    metadatas = [{"topic": topic_key, "chunk_index": i} for i in range(len(chunks))]

    # Build FAISS index from chunks + embeddings
    vectorstore = FAISS.from_texts(chunks, embeddings, metadatas=metadatas)

    # Save index to disk
    topic_index_dir = os.path.join(INDEX_DIR, topic_key)
    os.makedirs(topic_index_dir, exist_ok=True)
    vectorstore.save_local(topic_index_dir)

    print(f"  [OK] FAISS index saved -> {topic_index_dir}")
    return True


def build_all_indexes():
    os.makedirs(INDEX_DIR, exist_ok=True)

    print("Loading embedding model (this takes ~30s the first time)...")
    # Free, runs locally, no API key needed
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={"device": "cpu"},
    )
    print("Embedding model loaded.")

    results = {}
    for topic_key in TOPICS:
        success = build_index_for_topic(topic_key, embeddings)
        results[topic_key] = "success" if success else "failed"

    print(f"\n{'='*50}")
    print("PROCESSING COMPLETE")
    print(json.dumps(results, indent=2))


def load_index(topic_key: str):
    """
    Load a saved FAISS index for a topic.
    Call this from other modules (generator.py, app.py) to do retrieval.
    """
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={"device": "cpu"},
    )
    topic_index_dir = os.path.join(INDEX_DIR, topic_key)
    if not os.path.exists(topic_index_dir):
        raise FileNotFoundError(
            f"No FAISS index found for '{topic_key}'. Run processor.py first."
        )
    vectorstore = FAISS.load_local(
        topic_index_dir,
        embeddings,
        allow_dangerous_deserialization=True,  # safe since we built the index ourselves
    )
    return vectorstore


def retrieve_context(topic_key: str, query: str, k: int = 4) -> str:
    """
    Retrieve the top-k most relevant chunks for a query.
    Returns a single string to pass as context to the LLM.
    """
    vectorstore = load_index(topic_key)
    docs = vectorstore.similarity_search(query, k=k)
    context = "\n\n---\n\n".join([doc.page_content for doc in docs])
    return context


if __name__ == "__main__":
    build_all_indexes()
