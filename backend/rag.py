from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

embeddings = GoogleGenerativeAIEmbeddings(
    model="gemini-embedding-001"
)

vector_store = Chroma(
    persist_directory="chroma_db",
    collection_name="research_papers",
    embedding_function=embeddings
)

def ask_question(query):
    results = vector_store.similarity_search(
        query,
        k=3
    )

    context = "\n\n".join(
        f"[Page {result.metadata.get('page', 'Unknown')}]\n{result.page_content}"
        for result in results
    )

    model = ChatGoogleGenerativeAI(
        model="gemini-flash-latest",
        temperature=0
    )

    prompt = f"""
You are a research paper assistant.

CITATION RULE:
When you use information from the context, cite the page number
using the format [Page X].

If the answer is not present in the context, say:
"I could not find the answer in the provided paper."

Context:
{context}

Question:
{query}
"""

    try:
        response = model.invoke(prompt)

    except Exception as error:
        print("\nAI service error:")
        print(error)
        return "The AI service is temporarily unavailable. Please try again later."

    print("\nFinal Answer:\n")
    return response.text