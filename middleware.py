
from utils.common import token_validator
from fastapi.responses import JSONResponse
from fastapi import Request
from fastapi import FastAPI

def app_middleware(app: FastAPI):
    @app.middleware("http")
    async def token_validation_middleware(request: Request, call_next):
        if request.url.path in ["/docs", "/openapi.json", "/redoc"]:
            return await call_next(request)
        
        try:
            token = request.headers.get("Authorization")

            if not token:
                return JSONResponse(status_code=401, content={"detail": "Missing token"})
            if token.startswith("Bearer "):
                token = token.split(" ")[1]

            if not token_validator(token,request):
                return JSONResponse(status_code=401, content={"detail": "Invalid token"})
            
            return await call_next(request)

        except Exception as e:
            print(e)
            return JSONResponse(status_code=500, content={"detail": "Internal server error"})