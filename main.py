from fastapi import FastAPI
from pydantic import BaseModel
from tools.main import ask_llm_with_tools

app = FastAPI(title="RAG with FastAPI + LangChain")


class QueryRequest(BaseModel):
    question: str

@app.post("/ask")
async def ask_question(req: QueryRequest):
    answer = await ask_llm_with_tools(req.question)
    return {"answer": answer.answer}
