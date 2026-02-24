# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PORT=8080

# Install system dependencies for faster-whisper (requires FFmpeg and some libraries)
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libgl1 \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install FastAPI and other production dependencies
RUN pip install --no-cache-dir -r requirements.txt \
    fastapi uvicorn python-multipart jinja2 aiofiles

# Download the model during build to save startup time and avoid runtime download issues
ENV HF_HOME=/root/.cache/huggingface
RUN python -c "from faster_whisper import WhisperModel; WhisperModel('tiny', device='cpu', compute_type='int8')"

# Copy the rest of the application code
COPY . .

# Expose the port (informative only for Cloud Run)
EXPOSE 8080

# Command to run the application
# Use the PORT environment variable as required by Cloud Run
CMD ["sh", "-c", "uvicorn web_app:app --host 0.0.0.0 --port ${PORT}"]
