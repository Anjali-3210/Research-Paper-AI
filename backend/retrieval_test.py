from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma

load_dotenv()

embeddings = GoogleGenerativeAIEmbeddings(
    model="gemini-embedding-001"
)

vector_store = Chroma(
    persist_directory="chroma_db",
    collection_name="research_papers",
    embedding_function=embeddings
)

print("Vector store loaded successfully!")

query = "Why is self-attention useful?"

results = vector_store.similarity_search(
    query,
    k=3
)

print("\nRetrieved chunks:\n")

for i, result in enumerate(results, start=1):
    print(f"\n--- Result {i} ---")
    print("Page:", result.metadata.get("page"))
    print("Content:")
    print(result.page_content)