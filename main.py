import os
import tempfile
import logging
from typing import Optional
from pathlib import Path

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

from services.transcription import TranscriptionService
from services.diarization import DiarizationService
from services.formatter import format_response
from utils.file_handler import save_upload_file, cleanup_file, validate_audio_file

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Audio Transcription & Diarization API",
    description="API for transcribing audio and identifying speakers using Whisper and pyannote-audio",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
transcription_service = None
diarization_service = None


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    global transcription_service, diarization_service

    logger.info("Initializing services...")

    try:
        # Initialize transcription service
        whisper_model = os.getenv("WHISPER_MODEL", "base")
        transcription_service = TranscriptionService(model_name=whisper_model)
        logger.info(f"Transcription service initialized with model: {whisper_model}")

        # Initialize diarization service
        hf_token = os.getenv("HUGGINGFACE_TOKEN")
        if not hf_token:
            logger.warning("HUGGINGFACE_TOKEN not set. Diarization will not work!")

        diarization_service = DiarizationService(hf_token=hf_token)
        logger.info("Diarization service initialized")

    except Exception as e:
        logger.error(f"Error initializing services: {str(e)}")
        raise


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "ok",
        "service": "Audio Transcription & Diarization API",
        "version": "1.0.0"
    }


@app.get("/health")
async def health():
    """Detailed health check"""
    return {
        "status": "ok",
        "transcription_service": transcription_service is not None,
        "diarization_service": diarization_service is not None,
        "whisper_model": os.getenv("WHISPER_MODEL", "base")
    }


@app.post("/process-audio")
async def process_audio(
    file: UploadFile = File(...),
    language: Optional[str] = None,
    num_speakers: Optional[int] = None
):
    """
    Process audio file for transcription and diarization

    Args:
        file: Audio file (wav, mp3, m4a, flac, ogg)
        language: Optional language code for Whisper (e.g., 'en', 'id')
        num_speakers: Optional number of speakers for diarization

    Returns:
        JSON with transcription and speaker diarization results
    """
    temp_file_path = None

    try:
        # Validate file
        validate_audio_file(file)

        # Save uploaded file to temporary location
        temp_file_path = await save_upload_file(file)
        logger.info(f"Processing audio file: {file.filename}")

        # Run transcription
        logger.info("Starting transcription...")
        transcription_result = transcription_service.transcribe(
            audio_path=temp_file_path,
            language=language
        )

        # Run diarization
        logger.info("Starting diarization...")
        diarization_result = diarization_service.diarize(
            audio_path=temp_file_path,
            num_speakers=num_speakers
        )

        # Format and combine results
        logger.info("Formatting results...")
        response = format_response(
            transcription=transcription_result,
            diarization=diarization_result
        )

        logger.info("Processing completed successfully")
        return JSONResponse(content=response)

    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        logger.error(f"Error processing audio: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error processing audio: {str(e)}")

    finally:
        # Clean up temporary file
        if temp_file_path:
            cleanup_file(temp_file_path)


@app.post("/transcribe-only")
async def transcribe_only(
    file: UploadFile = File(...),
    language: Optional[str] = None
):
    """
    Transcribe audio file only (without diarization)

    Args:
        file: Audio file
        language: Optional language code for Whisper

    Returns:
        JSON with transcription results
    """
    temp_file_path = None

    try:
        validate_audio_file(file)
        temp_file_path = await save_upload_file(file)

        logger.info(f"Transcribing audio file: {file.filename}")
        result = transcription_service.transcribe(
            audio_path=temp_file_path,
            language=language
        )

        return JSONResponse(content=result)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error transcribing audio: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if temp_file_path:
            cleanup_file(temp_file_path)


@app.post("/diarize-only")
async def diarize_only(
    file: UploadFile = File(...),
    num_speakers: Optional[int] = None
):
    """
    Diarize audio file only (without transcription)

    Args:
        file: Audio file
        num_speakers: Optional number of speakers

    Returns:
        JSON with diarization results
    """
    temp_file_path = None

    try:
        validate_audio_file(file)
        temp_file_path = await save_upload_file(file)

        logger.info(f"Diarizing audio file: {file.filename}")
        result = diarization_service.diarize(
            audio_path=temp_file_path,
            num_speakers=num_speakers
        )

        return JSONResponse(content=result)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error diarizing audio: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if temp_file_path:
            cleanup_file(temp_file_path)


if __name__ == "__main__":
    import uvicorn

    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))

    uvicorn.run(app, host=host, port=port)
