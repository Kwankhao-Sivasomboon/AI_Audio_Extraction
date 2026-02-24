
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    WHISPER_MODEL_SIZE = os.getenv("WHISPER_MODEL_SIZE", "tiny")
    WHISPER_COMPUTE_TYPE = "int8"
    

