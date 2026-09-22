from dotenv import load_dotenv
import os
from langchain_chroma import Chroma
from langchain_google_genai import (
    ChatGoogleGenerativeAI,
    GoogleGenerativeAIEmbeddings
)

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


def ask_question(query, history=None):

    if history is None:
        history = []
        
    retrieval_query = query

    if history:
        last_question = history[-1].get("question", "")

        if last_question:
            retrieval_query = f"{last_question} {query}"

    # Retrieve relevant chunks from the research paper
    results_with_scores = vector_store.similarity_search_with_score(
        retrieval_query,
        k=4
    )

    # Filter results using similarity threshold
    threshold = 0.60

    results = [
        result
        for result, score in results_with_scores
        if score <= threshold
    ][:3]

    # No relevant information found
    if not results:
        return {
            "answer": "I could not find relevant information in the provided paper.",
            "sources": []
        }

    # Prepare source information
    sources = []
    seen_pages = set()

    for result in results:
        page = result.metadata.get("page", "Unknown")

        if page not in seen_pages:
            sources.append({
                "page": page,
                "content": result.page_content
            })
            seen_pages.add(page)

    # Combine retrieved chunks into context
    context = "\n\n".join(
        f"[Page {source['page']}]\n{source['content']}"
        for source in sources
    )

    # Prepare previous conversation context
    conversation_context = "\n\n".join(
        f"Previous Question: {item.get('question', '')}\n"
        f"Previous Answer: {item.get('answer', '')}"
        for item in history[-5:]
    )

    # Gemini model
    model = ChatGoogleGenerativeAI(
        model="gemini-flash-latest",
        temperature=0
    )

    # Grounded conversational RAG prompt
    prompt = f"""
You are a research paper assistant.

Answer the user's current question using ONLY the information provided
in the research paper context.

Rules:
1. Use the conversation history only to understand references such as
   "it", "they", "this", or "that".
2. Do not use outside knowledge.
3. Do not make up or assume information that is not present in the paper context.
4. When using information from the paper context, cite the page number
   using [Page X].
5. If the answer cannot be determined from the paper context, say:
"I could not find the answer in the provided paper."
6. Give a clear and concise answer.

Previous Conversation:
{conversation_context}

Research Paper Context:
{context}

Current Question:
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

    return {
        "answer": response.text,
        "sources": sources
    }