import jwt
from config import JWT_SECRET_KEY, REDIS_URL
from langchain_community.chat_message_histories import RedisChatMessageHistory

def token_validator(token: str) -> bool:
    try:    
        # In a real application, you would use your secret key here
        jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])
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