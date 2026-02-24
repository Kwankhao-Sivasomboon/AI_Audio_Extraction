import os
import json
import time
import uuid
import shutil
from fastapi import FastAPI, Request, File, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from src.config import Config
from src.stt_service import STTService
from src.llms_service import LLMService
from src.models import CustomerInfo

app = FastAPI()

# Setup templates
templates = Jinja2Templates(directory="templates")

# Initialize services globally so they don't reload on every request
print("Initializing STT and LLM Services...")
stt_service = STTService(model_size=Config.WHISPER_MODEL_SIZE, compute_type=Config.WHISPER_COMPUTE_TYPE)
llm_service = LLMService()
print("Services Initialized.")

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/process_audio")
async def process_audio(audio_file: UploadFile = File(...)):
    # Create a temporary directory or use the audio folder
    os.makedirs("audio", exist_ok=True)
    temp_filename = f"audio/{uuid.uuid4().hex}_{audio_file.filename}"
    
    # Save the uploaded file
    with open(temp_filename, "wb") as buffer:
        shutil.copyfileobj(audio_file.file, buffer)
        
    response_data = {
        "status": "error",
        "message": "",
        "data": None,
        "transcript": "",
        "metrics": {}
    }
    
    try:
        # Stage 1: STT
        stt_start = time.time()
        raw_transcript = stt_service.transcribe(temp_filename)
        stt_duration = time.time() - stt_start
        response_data["transcript"] = raw_transcript
        
        # Stage 2: LLM Extraction
        llm_start = time.time()
        json_str = llm_service.extract_info(raw_transcript)
        llm_extract_duration = time.time() - llm_start
        
        try:
            data_dict = json.loads(json_str)
        except json.JSONDecodeError:
            response_data["message"] = "LLM returned invalid JSON."
            return response_data
            
        # Stage 3: Validation
        validated_data = CustomerInfo(**data_dict)
        required_fields = ["name", "surname", "gender", "phone", "license_plate"]
        missing_or_invalid_fields = []
        model_dump = validated_data.model_dump()
        
        for field in required_fields:
            if model_dump.get(field) is None:
                missing_or_invalid_fields.append(field)
                
        # Stage 4: Ask-back logic
        llm_askback_duration = 0.0
        ask_back_msg = ""
        if not missing_or_invalid_fields:
            response_data["status"] = "COMPLETE"
        else:
            response_data["status"] = "INCOMPLETE"
            response_data["missing_fields"] = missing_or_invalid_fields
            askback_start = time.time()
            ask_back_msg = llm_service.generate_ask_back(missing_or_invalid_fields)
            llm_askback_duration = time.time() - askback_start
            
        response_data["data"] = model_dump
        response_data["message"] = ask_back_msg
        
        response_data["metrics"] = {
            "stt_duration": round(stt_duration, 4),
            "llm_extract_duration": round(llm_extract_duration, 4),
            "llm_askback_duration": round(llm_askback_duration, 4),
            "total_duration": round(stt_duration + llm_extract_duration + llm_askback_duration, 4)
        }
    except Exception as e:
        response_data["message"] = f"Processing Error: {str(e)}"
    finally:
        # Cleanup
        if os.path.exists(temp_filename):
            try:
                os.remove(temp_filename)
            except Exception as cleanup_error:
                print(f"Error cleaning up temp file: {cleanup_error}")
                
    return response_data
