import time

from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings


load_dotenv()


PERSIST_DIRECTORY = "chroma_db"
COLLECTION_NAME = "research_papers"


embeddings = GoogleGenerativeAIEmbeddings(
    model="gemini-embedding-001"
)


vector_store = Chroma(
    collection_name=COLLECTION_NAME,
    persist_directory=PERSIST_DIRECTORY,
    embedding_function=embeddings,
)


question = "Why is it useful?"


print("\n" + "=" * 60)
print("RETRIEVAL TEST")
print("=" * 60)

print(f"\nQuestion: {question}")


# Measure retrieval time
start_time = time.perf_counter()

results_with_scores = vector_store.similarity_search_with_score(
    question,
    k=4
)

end_time = time.perf_counter()

retrieval_time = (end_time - start_time) * 1000


print(f"Retrieved chunks: {len(results_with_scores)}")
print(f"Retrieval time: {retrieval_time:.2f} ms")


print("\n" + "-" * 60)
print("Retrieved Sources")
print("-" * 60)


for i, (result, distance) in enumerate(
    results_with_scores,
    start=1
):

    print(f"\nChunk {i}")
    print(f"Distance: {distance:.4f}")
    print(
        f"Page: {result.metadata.get('page', 'Unknown')}"
    )
    print(
        f"Content: {result.page_content[:300]}..."
    )

