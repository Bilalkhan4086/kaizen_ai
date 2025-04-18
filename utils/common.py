from jwt import JWT
from config import JWT_SECRET_KEY

def token_validator(token: str) -> bool:
    try:
        # Remove 'Bearer ' prefix if present
        if token.startswith('Bearer '):
            token = token.split(' ')[1]
            
        # In a real application, you would use your secret key here
        JWT.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])
        return True
    except Exception as e:
        return False