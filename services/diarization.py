import logging
from typing import Optional, Dict, Any, List
import torch
from pyannote.audio import Pipeline

logger = logging.getLogger(__name__)


class DiarizationService:
    """Service for speaker diarization using pyannote-audio"""

    def __init__(self, hf_token: Optional[str] = None):
        """
        Initialize pyannote diarization pipeline

        Args:
            hf_token: Hugging Face authentication token
        """
        if not hf_token:
            raise ValueError(
                "HUGGINGFACE_TOKEN is required for diarization. "
                "Get it from https://huggingface.co/settings/tokens and "
                "accept terms at https://huggingface.co/pyannote/speaker-diarization-3.1"
            )

        self.hf_token = hf_token

        # Check if CUDA is available
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        logger.info(f"Using device: {self.device}")

        # Load diarization pipeline
        logger.info("Loading pyannote diarization pipeline...")
        self.pipeline = Pipeline.from_pretrained(
            "pyannote/speaker-diarization-3.1",
            use_auth_token=hf_token
        )

        # Move to appropriate device
        self.pipeline.to(self.device)
        logger.info("Diarization pipeline loaded successfully")

    def diarize(
        self,
        audio_path: str,
        num_speakers: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Perform speaker diarization on audio file

        Args:
            audio_path: Path to audio file
            num_speakers: Optional number of speakers (if known)

        Returns:
            Dictionary containing diarization results with speaker segments
        """
        try:
            logger.info(f"Diarizing audio: {audio_path}")

            # Run diarization
            diarization_params = {}
            if num_speakers is not None:
                diarization_params["num_speakers"] = num_speakers
                logger.info(f"Using fixed number of speakers: {num_speakers}")

            diarization = self.pipeline(audio_path, **diarization_params)

            # Extract segments
            segments = []
            for turn, _, speaker in diarization.itertracks(yield_label=True):
                segments.append({
                    "start": float(turn.start),
                    "end": float(turn.end),
                    "speaker": speaker,
                    "duration": float(turn.end - turn.start)
                })

            # Get unique speakers
            speakers = list(set([seg["speaker"] for seg in segments]))
            speakers.sort()

            result = {
                "segments": segments,
                "speakers": speakers,
                "num_speakers": len(speakers)
            }

            logger.info(f"Diarization completed. Found {len(speakers)} speakers")
            return result

        except Exception as e:
            logger.error(f"Error during diarization: {str(e)}")
            raise Exception(f"Diarization failed: {str(e)}")

    def get_speaker_at_time(
        self,
        segments: List[Dict[str, Any]],
        timestamp: float
    ) -> Optional[str]:
        """
        Get the speaker at a specific timestamp

        Args:
            segments: List of diarization segments
            timestamp: Time in seconds

        Returns:
            Speaker label or None
        """
        for segment in segments:
            if segment["start"] <= timestamp <= segment["end"]:
                return segment["speaker"]
        return None
