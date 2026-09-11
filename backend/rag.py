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
    results_with_scores = vector_store.similarity_search_with_score(
    query,
    k=3
    )

    threshold = 0.70

    results = [
        result
        for result, score in results_with_scores
        if score <= threshold
    ]
    
    if not results:
        return {
            "answer": "I could not find relevant information in the provided paper.",
            "sources": []
        }

    sources = [
        {
            "page": result.metadata.get("page", "Unknown"),
            "content": result.page_content
        }
        for result in results
    ]

    context = "\n\n".join(
        f"[Page {source['page']}]\n{source['content']}"
        for source in sources
    )

    model = ChatGoogleGenerativeAI(
        model="gemini-flash-latest",
        temperature=0
    )

    prompt = f"""
    You are a research paper assistant.

    Answer the question using ONLY the information provided in the context.

    Rules:
    1. Do not use outside knowledge.
    2. Do not make up or assume information that is not present in the context.
    3. When using information from the context, cite the page number using [Page X].
    4. If the answer cannot be determined from the context, say:
    "I could not find the answer in the provided paper."
    5. Give a clear and concise answer.

    Context:
    {context}

    Question:
    {query}
    """

    try:
        response = model.invoke(prompt)

    except Exception as error:
        print("\nAI service error:")
        print(type(error).__name__)
        print(error)

        error_message = str(error)

        if "RESOURCE_EXHAUSTED" in error_message or "429" in error_message:
            user_message = (
                "The AI generation quota has been reached. "
                "Please try again later."
            )
        else:
            user_message = (
                "The AI service is temporarily unavailable. "
                "Please try again later."
            )

        return {
            "answer": user_message,
            "sources": sources
        }

    print("\nFinal Answer:\n")

    return {
        "answer": response.text,
        "sources": sources
    }