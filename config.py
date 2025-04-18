from dotenv import load_dotenv
import os
from pathlib import Path

# Load .env just once, early
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

# Access variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
