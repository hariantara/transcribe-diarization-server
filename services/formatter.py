import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


def format_response(
    transcription: Dict[str, Any],
    diarization: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Combine transcription and diarization results into a clean format

    Args:
        transcription: Whisper transcription results
        diarization: pyannote diarization results

    Returns:
        Combined and formatted response
    """
    try:
        # Combine transcription segments with speaker information
        combined_segments = []

        for trans_segment in transcription["segments"]:
            start_time = trans_segment["start"]
            end_time = trans_segment["end"]
            text = trans_segment["text"]

            # Find the primary speaker for this segment
            speaker = find_primary_speaker(
                start_time,
                end_time,
                diarization["segments"]
            )

            combined_segments.append({
                "start": start_time,
                "end": end_time,
                "text": text,
                "speaker": speaker,
                "duration": end_time - start_time
            })

        # Create speaker-wise transcript
        speaker_transcript = create_speaker_transcript(combined_segments)

        # Build final response
        response = {
            "success": True,
            "transcription": {
                "full_text": transcription["text"],
                "language": transcription.get("language"),
                "segments": combined_segments
            },
            "diarization": {
                "num_speakers": diarization["num_speakers"],
                "speakers": diarization["speakers"]
            },
            "speaker_transcript": speaker_transcript,
            "statistics": {
                "total_segments": len(combined_segments),
                "total_duration": sum(seg["duration"] for seg in combined_segments),
                "num_speakers": diarization["num_speakers"]
            }
        }

        return response

    except Exception as e:
        logger.error(f"Error formatting response: {str(e)}")
        raise


def find_primary_speaker(
    start_time: float,
    end_time: float,
    diarization_segments: List[Dict[str, Any]]
) -> str:
    """
    Find the primary speaker for a given time range

    Args:
        start_time: Start time of segment
        end_time: End time of segment
        diarization_segments: List of speaker segments

    Returns:
        Speaker label (e.g., "SPEAKER_00")
    """
    speaker_durations = {}

    for dia_segment in diarization_segments:
        dia_start = dia_segment["start"]
        dia_end = dia_segment["end"]
        speaker = dia_segment["speaker"]

        # Calculate overlap between transcription segment and diarization segment
        overlap_start = max(start_time, dia_start)
        overlap_end = min(end_time, dia_end)

        if overlap_start < overlap_end:
            overlap_duration = overlap_end - overlap_start

            if speaker not in speaker_durations:
                speaker_durations[speaker] = 0
            speaker_durations[speaker] += overlap_duration

    # Return speaker with longest overlap, or "UNKNOWN" if no overlap
    if speaker_durations:
        return max(speaker_durations.items(), key=lambda x: x[1])[0]
    else:
        return "UNKNOWN"


def create_speaker_transcript(segments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Create a clean transcript grouped by speaker turns

    Args:
        segments: List of segments with text and speaker info

    Returns:
        List of speaker turns with combined text
    """
    if not segments:
        return []

    speaker_transcript = []
    current_speaker = None
    current_text = []
    current_start = None

    for segment in segments:
        speaker = segment["speaker"]
        text = segment["text"]

        if speaker != current_speaker:
            # Save previous turn if exists
            if current_speaker is not None and current_text:
                speaker_transcript.append({
                    "speaker": current_speaker,
                    "text": " ".join(current_text).strip(),
                    "start": current_start,
                    "end": segment["start"]
                })

            # Start new turn
            current_speaker = speaker
            current_text = [text]
            current_start = segment["start"]
        else:
            # Continue current turn
            current_text.append(text)

    # Add final turn
    if current_speaker is not None and current_text:
        speaker_transcript.append({
            "speaker": current_speaker,
            "text": " ".join(current_text).strip(),
            "start": current_start,
            "end": segments[-1]["end"]
        })

    return speaker_transcript
