import time
from dotenv import load_dotenv

from rag import ask_question


# Load environment variables
load_dotenv()


# Test question
question = "What is the purpose of multi-head attention?"


print("\n" + "=" * 60)
print("RAG END-TO-END BENCHMARK")
print("=" * 60)

print(f"\nQuestion: {question}")
print("\nGenerating answer...")


# Measure complete RAG pipeline
start_time = time.perf_counter()

answer = ask_question(question)

end_time = time.perf_counter()


# Calculate response time
response_time = (end_time - start_time) * 1000


# Display results
print("\n" + "-" * 60)
print("RESULT")
print("-" * 60)

print(f"\nResponse time: {response_time:.2f} ms")

print("\nAnswer:")
print(answer)

print("\n" + "=" * 60)