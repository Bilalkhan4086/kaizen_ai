import jwt
from config import JWT_SECRET_KEY, REDIS_URL
from langchain_community.chat_message_histories import RedisChatMessageHistory
from fastapi import Request
def token_validator(token: str,request: Request) -> bool:
    try:    
        # In a real application, you would use your secret key here
        decoded_dict = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])
        request.state.user_id = str(decoded_dict.get('user_id'))
        return True
    except Exception as e:
        return False
    
def get_redis_message_history(session_id: str) -> RedisChatMessageHistory:
    """
    Factory function to get Redis chat message history for a given session ID.
    Includes a TTL (Time-To-Live) for automatic session cleanup.
    """
    try:
        x = RedisChatMessageHistory(session_id=session_id, url=REDIS_URL, ttl=3600)
        return x
    except Exception as e:
        return None
    
def format_header(uuid: str, sandbox_uuid: str, organization_uuid: str, token: str) -> dict:
    headers = {
        "sandbox_uuid": sandbox_uuid,
        "organization_uuid": organization_uuid,
        "uuid": uuid,
        "Authorization": f"Bearer {token}"
    }
    return {k: v for k, v in headers.items() if v}