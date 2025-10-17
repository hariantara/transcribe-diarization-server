---
title: Audio Transcription & Diarization API
emoji: 🎙️
colorFrom: blue
colorTo: purple
sdk: docker
pinned: false
license: mit
app_port: 7860
short_description: Transcribe audio and identify speakers using Whisper and pyannote
---

# Audio Transcription & Diarization API

Transcribe audio files and identify speakers using Whisper and pyannote-audio.

## API Endpoints

- `GET /` - Health check
- `GET /health` - Detailed health check
- `POST /process-audio` - Full transcription + diarization
- `POST /transcribe-only` - Transcription only
- `POST /diarize-only` - Diarization only

## Usage

```bash
curl -X POST "https://hariantara-transcribe-diarization-server.hf.space/process-audio" \
  -F "file=@audio.mp3" \
  -F "language=en"
```

## Configuration

Set your `HUGGINGFACE_TOKEN` in Space Settings > Repository secrets.

Make sure you've accepted the terms for:
- https://huggingface.co/pyannote/speaker-diarization-3.1
- https://huggingface.co/pyannote/segmentation-3.0
- https://huggingface.co/pyannote/wespeaker-voxceleb-resnet34-LM
