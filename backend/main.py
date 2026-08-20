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

@app.get("/ask")
def ask(question: str):
    try:
        answer = ask_question(question)

        return {
            "success": True,
            "question": question,
            "answer": answer
        }

    except Exception as error:
        print("API Error:", error)

        return {
            "success": False,
            "question": question,
            "error": "Unable to process the question."
        }