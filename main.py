from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
from tools.main import ask_llm_with_tools
from utils.common import token_validator
from fastapi.responses import JSONResponse

app = FastAPI(title="RAG with FastAPI + LangChain")

# Add the middleware
@app.middleware("http")
async def token_validation_middleware(request: Request, call_next):
    try:
        token = request.headers.get("Authorization")

        if not token:
            return JSONResponse(status_code=401, content={"detail": "Missing token"})

        if token.lower().startswith("bearer "):
            token = token[7:]

        if not token_validator(token):
            return JSONResponse(status_code=401, content={"detail": "Invalid token"})

        return await call_next(request)

    except Exception as e:
        return JSONResponse(status_code=500, content={"detail": "Internal server error"})

class QueryRequest(BaseModel):
    question: str

@app.post("/ask")
async def ask_question(req: QueryRequest):
    answer = await ask_llm_with_tools(req.question)
    return {"answer": answer.answer}
