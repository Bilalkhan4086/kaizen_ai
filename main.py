from fastapi import FastAPI, Header, Depends
from pydantic import BaseModel
from tools.main import ask_llm_with_tools
from fastapi import FastAPI, Security, HTTPException
from fastapi.security import APIKeyHeader
from typing import Optional,Annotated
from fastapi.security import HTTPBearer
from middleware import app_middleware


app = FastAPI(title="RAG with FastAPI + LangChain")

security = HTTPBearer()

api_key_header = APIKeyHeader(name="Authorization", auto_error=False)

async def get_token(authorization: Optional[str] = Security(api_key_header)):
    if authorization:
        if authorization.startswith("Bearer "):
            token = authorization[7:]
            return token
        else:
            raise HTTPException(status_code=400, detail="Invalid authorization header format")
    else:
        raise HTTPException(status_code=403, detail="Authorization token missing")



# Add the middleware
app_middleware(app)



class QueryRequest(BaseModel):
    question: str

@app.post("/ask")
async def ask_question(req: QueryRequest,  uuid: Annotated[Optional[str] , Header(convert_underscores=True)], token: str = Depends(get_token),sandbox_uuid: Annotated[Optional[str] , Header(convert_underscores=True)] = "", organization_uuid: Annotated[Optional[str]  , Header(convert_underscores=True)] = ""):
    # Create a QuestionRequest object for ask_llm_with_tools
    print("req.headers", sandbox_uuid, organization_uuid, uuid)
    answer = await ask_llm_with_tools(req.question, session_id="1234567890123", headers={"sandbox_uuid": sandbox_uuid, "organization_uuid": organization_uuid, "uuid": uuid, "Authorization": f"Bearer {token}"})
    return {"answer": answer.answer}


