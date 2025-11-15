from fastapi import APIRouter
from pydantic import BaseModel
from rag.query import generate_answer

router = APIRouter()

class Question(BaseModel):
    question: str

@router.post("")
def chat(q: Question):
    answer = generate_answer(q.question)
    return {"answer": answer}