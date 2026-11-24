
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from backend.hybrid_rag import (
    get_vector_answer,
    get_graph_answer,
    get_hybrid_answer
)

# Step 1: Create FastAPI application
app = FastAPI(title="Spotify Hybrid RAG API")


# Step 2: Define question input
class QuestionRequest(BaseModel):
    question: str
    mode: str = "Hybrid RAG"


# Step 3: Check API status
@app.get("/")
def home():
    return {"message": "Spotify Hybrid RAG API is running"}


# Step 4: Answer using selected RAG mode
@app.post("/ask")
def ask_question(request: QuestionRequest):

    if not request.question.strip():
        raise HTTPException(
            status_code=400,
            detail="Please enter a question."
        )

    if request.mode == "Vector RAG":
        answer = get_vector_answer(request.question)

    elif request.mode == "Graph RAG":
        answer = get_graph_answer(request.question)

    elif request.mode == "Hybrid RAG":
        answer = get_hybrid_answer(request.question)

    else:
        raise HTTPException(
            status_code=400,
            detail="Invalid RAG mode selected."
        )

    return {"answer": answer}
