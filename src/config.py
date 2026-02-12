
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    WHISPER_MODEL_SIZE = "small"
    WHISPER_COMPUTE_TYPE = "int8"
    
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY is not set in environment variables.")
