import time
import os
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings

from evaluation_dataset import evaluation_questions


load_dotenv()

PERSIST_DIRECTORY = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "chroma_db"
)
COLLECTION_NAME = "research_papers"


embeddings = GoogleGenerativeAIEmbeddings(
    model="gemini-embedding-001"
)


vector_store = Chroma(
    collection_name=COLLECTION_NAME,
    persist_directory=PERSIST_DIRECTORY,
    embedding_function=embeddings,
)


thresholds = [0.60, 0.65, 0.70]


print("\nRAG UNIQUE-PAGE EVALUATION")
print("=" * 70)


for threshold in thresholds:

    total_questions = len(evaluation_questions)
    passed_questions = 0

    total_precision = 0
    total_retrieval_time = 0
    total_retrieved_pages = 0

    print(f"\n{'=' * 70}")
    print(f"THRESHOLD: {threshold}")
    print(f"{'=' * 70}")

    for item in evaluation_questions:

        question = item["question"]
        expected_pages = item["expected_pages"]

        start_time = time.perf_counter()

        results_with_scores = (
            vector_store.similarity_search_with_score(
                question,
                k=4
            )
        )

        end_time = time.perf_counter()

        retrieval_time = (
            end_time - start_time
        ) * 1000

        total_retrieval_time += retrieval_time

        retrieved_pages = []

        for result, score in results_with_scores:

            if score <= threshold:

                page = result.metadata.get(
                    "page",
                    "Unknown"
                )

                if page not in retrieved_pages:
                    retrieved_pages.append(page)

        total_retrieved_pages += len(
            retrieved_pages
        )

        # --------------------------------------------------
        # Hit Rate
        # --------------------------------------------------

        if not expected_pages:

            passed = len(retrieved_pages) == 0

        else:

            passed = any(
                page in expected_pages
                for page in retrieved_pages
            )

        if passed:
            passed_questions += 1

        # --------------------------------------------------
        # Unique-page Precision
        # --------------------------------------------------

        if expected_pages:

            relevant_pages = [
                page
                for page in retrieved_pages
                if page in expected_pages
            ]

            if retrieved_pages:

                precision = (
                    len(relevant_pages)
                    / len(retrieved_pages)
                )

            else:

                precision = 0.0

        else:

            precision = (
                1.0
                if len(retrieved_pages) == 0
                else 0.0
            )

        total_precision += precision

        print(f"\nQuestion: {question}")
        print(f"Expected pages: {expected_pages}")
        print(f"Retrieved unique pages: {retrieved_pages}")

        print(
            f"Unique-page Precision: "
            f"{precision * 100:.2f}%"
        )

        print(
            f"Retrieval time: "
            f"{retrieval_time:.2f} ms"
        )

        print(
            f"Result: {'PASS' if passed else 'FAIL'}"
        )

    # --------------------------------------------------
    # Final metrics
    # --------------------------------------------------

    hit_rate = (
        passed_questions
        / total_questions
    ) * 100

    average_precision = (
        total_precision
        / total_questions
    ) * 100

    average_retrieval_time = (
        total_retrieval_time
        / total_questions
    )

    average_retrieved_pages = (
        total_retrieved_pages
        / total_questions
    )

    print("\n" + "-" * 70)
    print(f"SUMMARY FOR THRESHOLD {threshold}")
    print("-" * 70)

    print(
        f"Passed: "
        f"{passed_questions}/{total_questions}"
    )

    print(
        f"Hit Rate: "
        f"{hit_rate:.2f}%"
    )

    print(
        f"Average Unique-page Precision: "
        f"{average_precision:.2f}%"
    )

    print(
        f"Average Retrieved Unique Pages: "
        f"{average_retrieved_pages:.2f}"
    )

    print(
        f"Average Retrieval Time: "
        f"{average_retrieval_time:.2f} ms"
    )


print("\n" + "=" * 70)
print("UNIQUE-PAGE EVALUATION COMPLETE")
print("=" * 70)