from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from rag import ask_question, ask_comparison_question
from pydantic import BaseModel, Field, field_validator


app = FastAPI()

class AskRequest(BaseModel):
    question: str
    history: list[dict] = Field(default_factory=list)

    @field_validator("question")
    @classmethod
    def validate_question(cls, value):
        if not value.strip():
            raise ValueError("Question cannot be empty.")
        return value.strip()


class CompareRequest(BaseModel):
    question: str
    paper1_id: str
    paper2_id: str

    @field_validator("question")
    @classmethod
    def validate_question(cls, value):
        if not value.strip():
            raise ValueError("Question cannot be empty.")
        return value.strip()

    @field_validator("paper1_id", "paper2_id")
    @classmethod
    def validate_paper_id(cls, value):
        if not value.strip():
            raise ValueError("Paper ID cannot be empty.")
        return value.strip()

COMPARISON_PAPERS = {
    "paper1": {
        "id": "paper1",
        "title": "Attention Is All You Need",
        "collection": "comparison_paper1"
    },
    "paper2": {
        "id": "paper2",
        "title": "BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding",
        "collection": "comparison_paper2"
    }
}


def get_comparison_papers(paper1_id, paper2_id):
    paper1 = COMPARISON_PAPERS.get(paper1_id)
    paper2 = COMPARISON_PAPERS.get(paper2_id)

    if not paper1 or not paper2:
        return None

    if paper1_id == paper2_id:
        return None

    return paper1, paper2


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -----------------------------
# Basic Endpoints
# -----------------------------

@app.get("/")
def home():
    return {
        "message": "Research Paper AI API is running"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


# -----------------------------
# Paper Information
# -----------------------------

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

@app.post("/ask")
def ask(request: AskRequest):
    try:
        result = ask_question(
            request.question,
            request.history
        )

        return {
            "success": True,
            "question": request.question,
            "answer": result["answer"],
            "sources": result["sources"]
        }

    except Exception as error:
        print("API Error:", error)

        return {
            "success": False,
            "question": request.question,
            "error": "Unable to process the question."
        }


@app.post("/compare")
def compare(request: CompareRequest):
    try:
        papers = get_comparison_papers(
            request.paper1_id,
            request.paper2_id
        )

        if not papers:
            return {
                "success": False,
                "question": request.question,
                "error": "Please select two different valid papers."
            }

        result = ask_comparison_question(
            request.question,
            request.paper1_id,
            request.paper2_id
        )

        return {
            "success": True,
            "question": request.question,
            "answer": result["answer"],
            "sources": result["sources"]
        }

    except Exception as error:
        print("Comparison API Error:", error)

        return {
            "success": False,
            "question": request.question,
            "error": "Unable to compare the papers."
        }