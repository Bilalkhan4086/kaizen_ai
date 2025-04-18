from fastapi import FastAPI, Request, Depends
from pydantic import BaseModel
from tools.main import ask_llm_with_tools
from utils.common import token_validator
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

app = FastAPI(title="RAG with FastAPI + LangChain")

security = HTTPBearer()

# Add the middleware
@app.middleware("http")
async def token_validation_middleware(request: Request, call_next):
    if request.url.path in ["/docs", "/openapi.json", "/redoc"]:
        return await call_next(request)
    
    try:
        token = request.headers.get("Authorization")

        if not token:
            return JSONResponse(status_code=401, content={"detail": "Missing token"})

        if token.lower().startswith("bearer "):
            token = token[7:]

        if not token_validator(token):
            return JSONResponse(status_code=401, content={"detail": "Invalid token"})
        
        request.state.user_uuid = token
        return await call_next(request)

    except Exception as e:
        return JSONResponse(status_code=500, content={"detail": "Internal server error"})

class QueryRequest(BaseModel):
    question: str

@app.post("/ask")
async def ask_question(req: QueryRequest,request: Request,token: HTTPAuthorizationCredentials = Depends(security)):
    answer = await ask_llm_with_tools(req.question,session_id=request.state.user_uuid)
    return {"answer": answer.answer}
