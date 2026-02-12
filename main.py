
import os
import json
import sys
from src.config import Config
from src.stt_service import STTService
from src.llms_service import LLMService
from src.models import CustomerInfo

def main():
    # 1. Setup & Configuration
    if len(sys.argv) < 2:
        print("Usage: python main.py <path_to_audio_file>")
        # For testing purposes, if no arg, we might want to check if a specific test file exists or just exit.
        # creating a dummy file fallback for logic testing if user allows, but for now strict.
        return

    audio_path = sys.argv[1]
    
    # Initialize Services
    try:
        stt = STTService(model_size=Config.WHISPER_MODEL_SIZE, compute_type=Config.WHISPER_COMPUTE_TYPE)
        llm = LLMService()
    except Exception as e:
        print(f"Error initializing services: {e}")
        return

    # 2. Stage 1: Local STT
    try:
        raw_transcript = stt.transcribe(audio_path)
        print(f"\n--- Raw Transcript ---\n{raw_transcript}\n----------------------\n")
    except Exception as e:
        print(f"STT Error: {e}")
        return

    # 3. Stage 2: AI Extraction
    try:
        json_str = llm.extract_info(raw_transcript)
        print(f"--- Extracted JSON (Raw) ---\n{json_str}\n----------------------------\n")
        
        # Parse JSON safely
        try:
            data_dict = json.loads(json_str)
        except json.JSONDecodeError:
            print("Error: LLM returned invalid JSON.")
            return

    except Exception as e:
        print(f"Extraction Error: {e}")
        return

    # 4. Stage 3: Validation & Logic
    # We use the Pydantic model to validate.
    # Note: Our validators return None for invalid fields instead of raising errors hard, 
    # to allow identifying *which* fields are invalid/missing.
    
    validated_data = CustomerInfo(**data_dict)
    
    # Check for completeness
    # Fields are Optional, so they can be None.
    # Implementation Rule: "Complete" if all required fields are present and valid.
    # Let's assume ALL fields in CustomerInfo are required for "Complete" status based on the problem description implies "Customer Info" needs these.
    
    required_fields = ["name", "surname", "gender", "phone", "license_plate"]
    missing_or_invalid = []
    
    model_dump = validated_data.model_dump()
    
    for field in required_fields:
        if model_dump.get(field) is None:
            missing_or_invalid.append(field)
            
    # 5. Final Output
    if not missing_or_invalid:
        print(">>> STATUS: COMPLETE")
        print("Data:", json.dumps(model_dump, ensure_ascii=False, indent=2))
    else:
        print(">>> STATUS: INCOMPLETE")
        print(f"Missing/Invalid Fields: {missing_or_invalid}")
        
        # Ask-back Logic
        ask_back_msg = llm.generate_ask_back(missing_or_invalid)
        print(f"\n--- AI Ask-Back ---\n{ask_back_msg}\n-------------------")

if __name__ == "__main__":
    main()
