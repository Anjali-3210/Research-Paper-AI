from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from numpy import dot
from numpy.linalg import norm

load_dotenv()

embeddings = GoogleGenerativeAIEmbeddings(
    model="gemini-embedding-001"
)

texts = [
    "The Transformer uses self-attention mechanisms.",
    "Pizza is my favorite food."
]

vectors = embeddings.embed_documents(texts)

similarity = dot(vectors[0], vectors[1]) / (
    norm(vectors[0]) * norm(vectors[1])
)

print("Cosine similarity:", similarity)

print("Number of vectors:", len(vectors))
print("Vector dimensions:", len(vectors[0]))
print("First 5 values of vector 1:", vectors[0][:5])
print("First 5 values of vector 2:", vectors[1][:5])