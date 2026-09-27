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
COMPARISON_COLLECTION_PREFIX = "comparison_"


embeddings = GoogleGenerativeAIEmbeddings(
    model="gemini-embedding-001"
)


def get_vector_store(collection_name):
    return Chroma(
        collection_name=collection_name,
        persist_directory=PERSIST_DIRECTORY,
        embedding_function=embeddings,
    )
    
def get_comparison_collection_name(paper_id):
    return f"{COMPARISON_COLLECTION_PREFIX}{paper_id}"

def retrieve_from_paper(query, paper_id, k=4, threshold=0.60):
    collection_name = get_comparison_collection_name(paper_id)

    vector_store = get_vector_store(collection_name)

    results_with_scores = vector_store.similarity_search_with_score(
        query,
        k=k
    )

    results = [
        result
        for result, score in results_with_scores
        if score <= threshold
    ][:3]

    sources = []
    seen_pages = set()

    for result in results:
        page = result.metadata.get("page", "Unknown")

        if page not in seen_pages:
            sources.append({
                "paper_id": paper_id,
                "page": page,
                "content": result.page_content
            })
            seen_pages.add(page)

    return sources

def compare_papers(query, paper1_id, paper2_id):
    paper1_query = (
        f"{query} "
        "Transformer self-attention multi-head attention architecture"
    )

    paper2_query = (
        f"{query} "
        "BERT bidirectional self-attention Transformer architecture"
    )

    paper1_sources = retrieve_from_paper(
        paper1_query,
        paper1_id
    )

    paper2_sources = retrieve_from_paper(
        paper2_query,
        paper2_id
    )

    if not paper1_sources and not paper2_sources:
        return {
            "answer": "I could not find relevant information in either paper.",
            "sources": []
        }

    if not paper1_sources:
        paper1_context = (
            "No relevant information was retrieved from Paper 1 "
            "for this question."
        )
    else:
        paper1_context = "\n\n".join(
            f"[Paper 1 - Page {source['page']}]\n{source['content']}"
            for source in paper1_sources
        )

    if not paper2_sources:
        paper2_context = (
            "No relevant information was retrieved from Paper 2 "
            "for this question."
        )
    else:
        paper2_context = "\n\n".join(
            f"[Paper 2 - Page {source['page']}]\n{source['content']}"
            for source in paper2_sources
        )

    context = f"""
===== PAPER 1 =====
Title: Attention Is All You Need

{paper1_context}

===== PAPER 2 =====
Title: BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding

{paper2_context}
"""

    return {
        "context": context,
        "paper1_sources": paper1_sources,
        "paper2_sources": paper2_sources
    }

def generate_comparison_answer(query, comparison_data):
    model = ChatGoogleGenerativeAI(
        model="gemini-flash-latest",
        temperature=0
    )

    prompt = f"""
You are an AI research paper comparison assistant.

Your task is to compare two research papers using ONLY the
information provided in the contexts below.

STRICT RULES:
1. Do not use outside knowledge.
2. Do not make up or assume information.
3. Keep Paper 1 and Paper 2 clearly separated.
4. Every factual claim must have a page citation.
5. Use citations exactly in this format:
   [Paper 1 - Page X]
   [Paper 2 - Page X]
6. If a fact is available in only one paper, explicitly mention that.
7. If the provided context does not contain enough information,
   say:
   "I could not find enough information in the provided papers."
8. Do not claim that one paper is better unless the provided
   context explicitly supports such a comparison.
9. Keep the answer concise but informative.

STRUCTURE YOUR ANSWER AS:

### Paper 1
Explain the relevant approach, method, architecture, or finding
from Paper 1 with citations.

### Paper 2
Explain the relevant approach, method, architecture, or finding
from Paper 2 with citations.

### Key Differences
List the important differences between the two papers.
Every difference must be supported by citations.

### Similarities
Mention important similarities if they are supported by
the provided contexts.

Research Paper Context:
{comparison_data["context"]}

Question:
{query}
"""

    try:
        response = model.invoke(prompt)

        return {
            "answer": response.text,
            "sources": (
                comparison_data["paper1_sources"]
                + comparison_data["paper2_sources"]
            )
        }

    except Exception as error:
        print("\nAI comparison error:")
        print(type(error).__name__)
        print(error)

        return {
            "answer": "The AI service is temporarily unavailable. Please try again later.",
            "sources": (
                comparison_data["paper1_sources"]
                + comparison_data["paper2_sources"]
            )
        }

def ask_comparison_question(query, paper1_id, paper2_id):
    comparison_data = compare_papers(
        query,
        paper1_id,
        paper2_id
    )

    if "answer" in comparison_data:
        return comparison_data

    result = generate_comparison_answer(
        query,
        comparison_data
    )

    return {
        "answer": result["answer"],
        "sources": result["sources"],
        "paper1_id": paper1_id,
        "paper2_id": paper2_id
    }

def ask_question(query, history=None, collection_name=COLLECTION_NAME):

    if history is None:
        history = []
        
    vector_store = get_vector_store(collection_name)
        
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