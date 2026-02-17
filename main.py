
import os
import json
import sys
import time
from src.config import Config
from src.stt_service import STTService
from src.llms_service import LLMService
from src.models import CustomerInfo

def main():
    # 1. Setup & Configuration
    if len(sys.argv) < 2:
        print("Usage: python main.py <path_to_audio_file>")
        return

    audio_path = sys.argv[1]
    
    # Initialize Services
    try:
        stt = STTService(model_size=Config.WHISPER_MODEL_SIZE, compute_type=Config.WHISPER_COMPUTE_TYPE)
        llm = LLMService()

        # Timing variables
        stt_duration = 0.0
        llm_extract_duration = 0.0
        llm_askback_duration = 0.0
    except Exception as e:
        print(f"Error initializing services: {e}")
        return

    # 2. Stage 1: Local STT
    try:
        stt_start = time.time()
        raw_transcript = stt.transcribe(audio_path)
        stt_duration = time.time() - stt_start
        print(f"\n--- Raw Transcript ---\n{raw_transcript}\n----------------------\n")
    except Exception as e:
        print(f"STT Error: {e}")
        return

    # 3. Stage 2: AI Extraction
    try:
        llm_start = time.time()
        json_str = llm.extract_info(raw_transcript)
        llm_extract_duration = time.time() - llm_start
        
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
    validated_data = CustomerInfo(**data_dict)
    
    # Check for completeness
    # Implementation Rule: "Complete" if all required fields are present and valid.
    required_fields = ["name", "surname", "gender", "phone", "license_plate"]
    missing_or_invalid_fields = []
    
    model_dump = validated_data.model_dump()
    
    for field in required_fields:
        if model_dump.get(field) is None:
            missing_or_invalid_fields.append(field)
            
    # 5. Final Output
    if not missing_or_invalid_fields:
        print(">>> STATUS: COMPLETE")
        print("Data:", json.dumps(model_dump, ensure_ascii=False, indent=2))
    else:
        print(">>> STATUS: INCOMPLETE")
        print(f"Missing/Invalid Fields: {missing_or_invalid_fields}")
        print("Current Data:", json.dumps(model_dump, ensure_ascii=False, indent=2))
        
        # Ask-back Logic
        askback_start = time.time()
        ask_back_msg = llm.generate_ask_back(missing_or_invalid_fields)
        llm_askback_duration = time.time() - askback_start
        print(f"\n--- AI Ask-Back ---\n{ask_back_msg}\n-------------------")

    # 6. Performance Summary
    print("\n========================================")
    print("       PERFORMANCE METRICS (LATENCY)    ")
    print("========================================")
    print(f"1. STT Transcribe  : {stt_duration:.4f} sec")
    print(f"2. LLM Extraction  : {llm_extract_duration:.4f} sec")
    if llm_askback_duration > 0:
        print(f"3. LLM Ask-Back    : {llm_askback_duration:.4f} sec")
    print(f"Total Processing   : {stt_duration + llm_extract_duration + llm_askback_duration:.4f} sec")
    print("========================================")

if __name__ == "__main__":
    main()
