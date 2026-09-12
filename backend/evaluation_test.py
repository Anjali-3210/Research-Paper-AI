import time

from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings

from evaluation_dataset import evaluation_questions

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

threshold = 0.70

total_questions = len(evaluation_questions)
passed_questions = 0

print("\nRAG RETRIEVAL EVALUATION")
print("=" * 50)

for item in evaluation_questions:
    question = item["question"]
    expected_pages = item["expected_pages"]

    start_time = time.perf_counter()

    results = vector_store.similarity_search_with_score(
        question,
        k=3
    )

    end_time = time.perf_counter()

    retrieval_time = (end_time - start_time) * 1000

    relevant_pages = []
    relevant_scores = []

    for result, score in results:
        if score <= threshold:
            relevant_pages.append(
                result.metadata.get("page", "Unknown")
            )
            relevant_scores.append(score)

    if not expected_pages:
        passed = len(relevant_pages) == 0
    else:
        passed = any(
            page in expected_pages
            for page in relevant_pages
        )
    if passed:
        passed_questions += 1

    print(f"\nQuestion: {question}")
    print(f"Expected pages: {expected_pages}")
    print(f"Retrieved pages: {relevant_pages}")

    if relevant_scores:
        print(
            "Retrieval scores: "
            + ", ".join(f"{score:.4f}" for score in relevant_scores)
        )

    print(f"Retrieval time: {retrieval_time:.2f} ms")
    print(f"Result: {'PASS' if passed else 'FAIL'}")

accuracy = (passed_questions / total_questions) * 100

print("\n" + "=" * 50)
print(f"Passed: {passed_questions}/{total_questions}")
print(f"Retrieval Accuracy: {accuracy:.2f}%")