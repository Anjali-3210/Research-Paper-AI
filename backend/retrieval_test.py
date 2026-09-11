import time
from dotenv import load_dotenv

from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings


# Load environment variables
load_dotenv()

PERSIST_DIRECTORY = "chroma_db"
COLLECTION_NAME = "research_papers"


# -----------------------------
# Load embedding model
# -----------------------------

embeddings = GoogleGenerativeAIEmbeddings(
    model="gemini-embedding-001"
)


# -----------------------------
# Load existing ChromaDB
# -----------------------------

vector_store = Chroma(
    collection_name=COLLECTION_NAME,
    persist_directory=PERSIST_DIRECTORY,
    embedding_function=embeddings,
)


# -----------------------------
# Test question
# -----------------------------

question = "What is the capital of France?"


# -----------------------------
# Measure retrieval latency
# -----------------------------

start_time = time.perf_counter()

results = vector_store.similarity_search_with_score(
    question,
    k=4
)

end_time = time.perf_counter()

retrieval_time = (end_time - start_time) * 1000


# -----------------------------
# Display results
# -----------------------------

print("\n" + "=" * 60)
print("RETRIEVAL TEST")
print("=" * 60)

print(f"\nQuestion: {question}")
print(f"Retrieved chunks: {len(results)}")
print(f"Retrieval time: {retrieval_time:.2f} ms")

print("\n" + "-" * 60)
print("Retrieved Sources")
print("-" * 60)

for i, (result, score) in enumerate(results, start=1):
    print(f"\nChunk {i}")
    print(f"Score: {score:.4f}")
    print(f"Page: {result.metadata.get('page', 'Unknown')}")
    print(f"Content: {result.page_content[:300]}...")

print("\n" + "=" * 60)

