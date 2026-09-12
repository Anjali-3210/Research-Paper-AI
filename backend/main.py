from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.rag import ask_question

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def home():
    return {"message": "Research Paper AI API is running"}

@app.get("/health")
def health():
    return {
        "status": "healthy"
    }
    
@app.get("/paper")
def paper_info():
    return {
        "title": "Attention Is All You Need",
        "authors": [
            "Ashish Vaswani",
            "Noam Shazeer",
            "Niki Parmar",
            "Jakob Uszkoreit",
            "Llion Jones",
            "Aidan N. Gomez",
            "Łukasz Kaiser",
            "Illia Polosukhin"
        ],
        "pages": 15,
        "status": "ready"
    }

@app.get("/ask")
def ask(question: str):
    try:
        result = ask_question(question)

        return {
            "success": True,
            "question": question,
            "answer": result["answer"],
            "sources": result["sources"]
        }

    except Exception as error:
        print("API Error:", error)

        return {
            "success": False,
            "question": question,
            "error": "Unable to process the question."
        }