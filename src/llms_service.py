
import json
import google.generativeai as genai
from typing import List, Optional
from .config import Config

class LLMService:
    def __init__(self):
        """
        Initialize Gemini API integration.
        """
        if not Config.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is not set in environment variables.")
        genai.configure(api_key=Config.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(
            model_name='gemini-2.5-flash',
            generation_config={"temperature": 0.4}
        )

    def extract_info(self, transcript: str) -> str:
        """
        Extract structured information from transcript using Gemini.
        Returns a JSON string.
        """
        prompt = f"""
        You are an AI assistant that extracts structured data from Thai text.
        Extract the following information from the text below:
        - name (First name only)
        - surname (Last name only)
        - gender (Male/Female/Other)
        - phone (Phone number, remove any hyphens or spaces, keep only digits)
        - license_plate (Vehicle license plate number)

        Specific Instructions for Thai Logic:
        1. **Name/Surname**: 
           - Usually follows "ชื่อ" (Name) and then Surname.
           - "สมชาย" is a common Thai Name. "ใจดี" is a common Surname.
        2. **Gender**: 
           - Words like "เพศชาย", "เพชรชาย" (misheard), "ผู้ชาย", "ผม" imply Gender = Male.
           - Words like "เพศหญิง", "ผู้หญิง", "ดิฉัน" imply Gender = Female.
           - Do NOT use "เพชรชาย" or similar gender words as a Name or Surname.
        3. **License Plate**:
           - Convert phonetic Thai words like "ก็ขอ", "กอขอ" to standard two-letter thai vehicle codes "กข".
           - Ensure the format matches standard Thai license plates (e.g., "1กข 1234", "กข 1234", "70-1234").

        Text: "{transcript}"

        Return the result strictly in JSON format. 
        If a field is missing or ambiguous, set it to null.
        Do not include any markdown formatting (like ```json), just the raw JSON string.
        """
        
        response = self.model.generate_content(prompt)
        # Cleanup response to ensure valid JSON (remove backticks if any)
        text = response.text.strip()
        if text.startswith("```json"):
            text = text[7:]
        if text.endswith("```"):
            text = text[:-3]
        return text.strip()

    def generate_ask_back(self, missing_fields: List[str]) -> str:
        """
        Generate a polite question to ask for missing information.
        """
        fields_str = ", ".join(missing_fields)
        prompt = f"""
        You are a polite and helpful customer service AI.
        The user provided some information, but the following fields are missing or invalid: {fields_str}.
        
        Please generate a polite, clear, and friendly message in Thai asking the user for this specific missing information.
        Keep it concise.
        """
        
        response = self.model.generate_content(prompt)
        return response.text.strip()
