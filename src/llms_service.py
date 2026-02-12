
import json
import google.generativeai as genai
from typing import List, Optional
from .config import Config

class LLMService:
    def __init__(self):
        """
        Initialize Gemini API integration.
        """
        genai.configure(api_key=Config.GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-1.5-flash')

    def extract_info(self, transcript: str) -> str:
        """
        Extract structured information from transcript using Gemini.
        Returns a JSON string.
        """
        prompt = f"""
        You are an AI assistant that extracts structured data from text.
        Extract the following information from the text below:
        - name (First name only)
        - surname (Last name only)
        - gender (Male/Female/Other)
        - phone (Phone number)
        - license_plate (Vehicle license plate number)

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
