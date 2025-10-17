# Audio Transcription & Diarization Server

A FastAPI server that provides audio transcription using OpenAI Whisper and speaker diarization using pyannote-audio. Perfect for processing meeting recordings, interviews, or any multi-speaker audio content.

## Features

- **Transcription**: Accurate speech-to-text using OpenAI Whisper
- **Speaker Diarization**: Identify and separate different speakers using pyannote-audio
- **Combined Output**: Clean JSON response with transcription aligned to speakers
- **Multiple Endpoints**: Process full audio or use transcription/diarization separately
- **File Support**: WAV, MP3, M4A, FLAC, OGG, MP4, AVI, MOV
- **GPU Support**: Automatic CUDA detection for faster processing

## Prerequisites

- Python 3.8+
- CUDA-compatible GPU (optional, but recommended for better performance)
- Hugging Face account and token (for pyannote-audio)

## Installation

### 1. Clone or navigate to the project directory

```bash
cd transcribe_diarization_server
```

### 2. Create virtual environment

```bash
python -m venv venv

# Activate on macOS/Linux
source venv/bin/activate

# Activate on Windows
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up Hugging Face authentication

1. Create a Hugging Face account at https://huggingface.co
2. Generate an access token at https://huggingface.co/settings/tokens
3. Accept the model terms at https://huggingface.co/pyannote/speaker-diarization-3.1

### 5. Configure environment

```bash
cp .env.example .env
```

Edit `.env` and add your Hugging Face token:

```env
HUGGINGFACE_TOKEN=your_actual_token_here
WHISPER_MODEL=base
HOST=0.0.0.0
PORT=8000
```

## Running the Server

### Development mode

```bash
python main.py
```

### Production mode with Uvicorn

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

The server will start at `http://localhost:8000`

## API Endpoints

### 1. Health Check

```bash
GET /
GET /health
```

Check if the server is running and services are initialized.

### 2. Process Audio (Transcription + Diarization)

```bash
POST /process-audio
```

Upload an audio file and get both transcription and speaker diarization.

**Parameters:**
- `file` (required): Audio file
- `language` (optional): Language code (e.g., 'en', 'id', 'es')
- `num_speakers` (optional): Number of speakers if known

**Example using cURL:**

```bash
curl -X POST "http://localhost:8000/process-audio" \
  -F "file=@meeting.mp3" \
  -F "language=en"
```

**Example using Python:**

```python
import requests

url = "http://localhost:8000/process-audio"
files = {"file": open("meeting.mp3", "rb")}
data = {"language": "en", "num_speakers": 2}

response = requests.post(url, files=files, data=data)
result = response.json()
print(result)
```

**Response format:**

```json
{
  "success": true,
  "transcription": {
    "full_text": "Complete transcription...",
    "language": "en",
    "segments": [
      {
        "start": 0.0,
        "end": 5.5,
        "text": "Hello everyone",
        "speaker": "SPEAKER_00",
        "duration": 5.5
      }
    ]
  },
  "diarization": {
    "num_speakers": 2,
    "speakers": ["SPEAKER_00", "SPEAKER_01"]
  },
  "speaker_transcript": [
    {
      "speaker": "SPEAKER_00",
      "text": "Hello everyone. Welcome to the meeting.",
      "start": 0.0,
      "end": 8.2
    },
    {
      "speaker": "SPEAKER_01",
      "text": "Thank you for having me.",
      "start": 8.5,
      "end": 10.3
    }
  ],
  "statistics": {
    "total_segments": 15,
    "total_duration": 120.5,
    "num_speakers": 2
  }
}
```

### 3. Transcribe Only

```bash
POST /transcribe-only
```

Get only the transcription without speaker diarization (faster).

**Parameters:**
- `file` (required): Audio file
- `language` (optional): Language code

**Example:**

```bash
curl -X POST "http://localhost:8000/transcribe-only" \
  -F "file=@audio.wav"
```

### 4. Diarize Only

```bash
POST /diarize-only
```

Get only speaker diarization without transcription.

**Parameters:**
- `file` (required): Audio file
- `num_speakers` (optional): Number of speakers

**Example:**

```bash
curl -X POST "http://localhost:8000/diarize-only" \
  -F "file=@audio.wav" \
  -F "num_speakers=3"
```

## Mobile Integration

### iOS (Swift)

```swift
func processAudio(audioURL: URL) async throws -> TranscriptionResult {
    let url = URL(string: "http://your-server:8000/process-audio")!
    var request = URLRequest(url: url)
    request.httpMethod = "POST"

    let boundary = UUID().uuidString
    request.setValue("multipart/form-data; boundary=\(boundary)", forHTTPHeaderField: "Content-Type")

    var data = Data()

    // Add file
    data.append("--\(boundary)\r\n".data(using: .utf8)!)
    data.append("Content-Disposition: form-data; name=\"file\"; filename=\"audio.m4a\"\r\n".data(using: .utf8)!)
    data.append("Content-Type: audio/m4a\r\n\r\n".data(using: .utf8)!)
    data.append(try Data(contentsOf: audioURL))
    data.append("\r\n".data(using: .utf8)!)
    data.append("--\(boundary)--\r\n".data(using: .utf8)!)

    let (responseData, _) = try await URLSession.shared.upload(for: request, from: data)
    let result = try JSONDecoder().decode(TranscriptionResult.self, from: responseData)
    return result
}
```

### Android (Kotlin)

```kotlin
fun processAudio(audioFile: File): TranscriptionResult {
    val client = OkHttpClient()

    val requestBody = MultipartBody.Builder()
        .setType(MultipartBody.FORM)
        .addFormDataPart(
            "file",
            audioFile.name,
            audioFile.asRequestBody("audio/*".toMediaType())
        )
        .addFormDataPart("language", "en")
        .build()

    val request = Request.Builder()
        .url("http://your-server:8000/process-audio")
        .post(requestBody)
        .build()

    client.newCall(request).execute().use { response ->
        val json = response.body?.string()
        return Gson().fromJson(json, TranscriptionResult::class.java)
    }
}
```

### React Native

```javascript
async function processAudio(audioUri) {
  const formData = new FormData();
  formData.append('file', {
    uri: audioUri,
    type: 'audio/m4a',
    name: 'recording.m4a',
  });
  formData.append('language', 'en');

  const response = await fetch('http://your-server:8000/process-audio', {
    method: 'POST',
    body: formData,
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });

  return await response.json();
}
```

## Configuration

### Whisper Model Options

Edit `.env` to change the Whisper model:

- `tiny`: Fastest, least accurate
- `base`: Good balance (default)
- `small`: Better accuracy
- `medium`: High accuracy
- `large`: Best accuracy, slowest

### File Size Limits

Default: 100MB. Change in `.env`:

```env
MAX_FILE_SIZE_MB=200
```

### Supported Languages

Whisper supports 99+ languages. Common codes:
- `en` - English
- `id` - Indonesian
- `es` - Spanish
- `fr` - French
- `de` - German
- `zh` - Chinese
- `ja` - Japanese
- `ko` - Korean

Or omit the language parameter for auto-detection.

## Performance Tips

1. **Use GPU**: Install CUDA and PyTorch with CUDA support for 10x faster processing
2. **Choose appropriate Whisper model**: Larger models are more accurate but slower
3. **Pre-specify speaker count**: If you know the number of speakers, pass `num_speakers`
4. **Use separate endpoints**: If you only need transcription, use `/transcribe-only`

## Troubleshooting

### "HUGGINGFACE_TOKEN is required"

Make sure you've:
1. Created a Hugging Face account
2. Generated an access token
3. Accepted the pyannote model terms
4. Added the token to your `.env` file

### Out of memory errors

- Use a smaller Whisper model (`tiny` or `base`)
- Process shorter audio files
- Reduce audio quality/sample rate before uploading

### Slow processing

- Install CUDA for GPU acceleration
- Use smaller Whisper model
- Use `/transcribe-only` if you don't need diarization

## Project Structure

```
transcribe_diarization_server/
├── main.py                 # FastAPI application
├── requirements.txt        # Python dependencies
├── .env.example           # Environment template
├── .gitignore            # Git ignore rules
├── README.md             # This file
├── services/
│   ├── __init__.py
│   ├── transcription.py  # Whisper service
│   ├── diarization.py    # pyannote service
│   └── formatter.py      # Response formatting
└── utils/
    ├── __init__.py
    └── file_handler.py   # File upload/validation
```

## License

MIT

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review the API documentation
3. Check Whisper docs: https://github.com/openai/whisper
4. Check pyannote docs: https://github.com/pyannote/pyannote-audio
