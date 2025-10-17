import logging
from typing import Optional, Dict, Any
import whisper
import torch

logger = logging.getLogger(__name__)


class TranscriptionService:
    """Service for transcribing audio using OpenAI Whisper"""

    def __init__(self, model_name: str = "base"):
        """
        Initialize Whisper model

        Args:
            model_name: Model size (tiny, base, small, medium, large)
        """
        self.model_name = model_name
        logger.info(f"Loading Whisper model: {model_name}")

        # Check if CUDA is available
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Using device: {self.device}")

        # Load model
        self.model = whisper.load_model(model_name, device=self.device)
        logger.info(f"Whisper model {model_name} loaded successfully")

    def transcribe(
        self,
        audio_path: str,
        language: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Transcribe audio file

        Args:
            audio_path: Path to audio file
            language: Optional language code (e.g., 'en', 'id')

        Returns:
            Dictionary containing transcription results
        """
        try:
            logger.info(f"Transcribing audio: {audio_path}")

            # Transcribe with Whisper
            options = {
                "task": "transcribe",
                "verbose": False
            }

            if language:
                options["language"] = language
                logger.info(f"Using language: {language}")

            result = self.model.transcribe(audio_path, **options)

            # Extract segments with timing information
            segments = []
            for segment in result["segments"]:
                segments.append({
                    "start": segment["start"],
                    "end": segment["end"],
                    "text": segment["text"].strip(),
                    "confidence": segment.get("confidence", None)
                })

            transcription_result = {
                "text": result["text"].strip(),
                "language": result.get("language", language),
                "segments": segments
            }

            logger.info("Transcription completed successfully")
            return transcription_result

        except Exception as e:
            logger.error(f"Error during transcription: {str(e)}")
            raise Exception(f"Transcription failed: {str(e)}")
