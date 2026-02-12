
from faster_whisper import WhisperModel
import os

class STTService:
    def __init__(self, model_size: str = "small", compute_type: str = "int8"):
        """
        Initialize the Faster-Whisper model.
        Args:
            model_size: "small" or "medium"
            compute_type: "int8" for efficiency on GTX 1650 Ti
        """
        print(f"Loading Whisper model '{model_size}' with compute_type '{compute_type}'...")
        # Use GPU if available, otherwise fallback to CPU
        self.model = WhisperModel(model_size, device="auto", compute_type=compute_type)
        print(f"Whisper model loaded on {self.model.model.device}.")

    def transcribe(self, audio_path: str) -> str:
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        print(f"Transcribing {audio_path}...")
        segments, _ = self.model.transcribe(audio_path, beam_size=5)
        
        transcript = []
        for segment in segments:
            transcript.append(segment.text)
            
        full_text = " ".join(transcript).strip()
        print("Transcription complete.")
        return full_text
