# Deploy to Hugging Face Spaces (FREE)

## Step 1: Create a New Space

1. Go to https://huggingface.co/new-space
2. Fill in:
   - **Space name**: `audio-transcription-api` (or your choice)
   - **License**: MIT
   - **SDK**: Docker
   - **Hardware**: CPU basic (FREE)
   - **Visibility**: Public or Private
3. Click **Create Space**

## Step 2: Prepare Your Code

Make sure you have these files:
- ✅ `Dockerfile`
- ✅ `requirements.txt`
- ✅ `main.py`
- ✅ `services/` folder
- ✅ `utils/` folder

## Step 3: Rename README for Space

```bash
# Rename the Space README
mv README_SPACE.md README.md

# Backup the original README
mv README.md README_LOCAL.md
mv README_SPACE.md README.md
```

## Step 4: Push to Hugging Face

### Option A: Using Git

```bash
# Initialize git if not already done
git init

# Add Hugging Face remote
git remote add space https://huggingface.co/spaces/YOUR-USERNAME/YOUR-SPACE-NAME

# Add files
git add .

# Commit
git commit -m "Initial commit"

# Push to Hugging Face
git push space main
```

### Option B: Using Hugging Face Hub CLI

```bash
# Install huggingface-hub CLI
pip install huggingface-hub[cli]

# Login
huggingface-cli login

# Upload
huggingface-cli upload YOUR-USERNAME/YOUR-SPACE-NAME . --repo-type=space
```

## Step 5: Set Environment Variables

1. Go to your Space settings: `https://huggingface.co/spaces/YOUR-USERNAME/YOUR-SPACE-NAME/settings`
2. Scroll to **Repository secrets**
3. Add secret:
   - **Name**: `HUGGINGFACE_TOKEN`
   - **Value**: Your HF token (from https://huggingface.co/settings/tokens)
4. Click **Add**

## Step 6: Wait for Build

- Go to your Space page
- Watch the build logs
- First build takes 5-10 minutes (downloading models)
- Status will change to "Running" when ready

## Step 7: Test Your API

Your API will be available at:
```
https://YOUR-USERNAME-YOUR-SPACE-NAME.hf.space
```

Test with curl:
```bash
curl -X POST "https://YOUR-USERNAME-YOUR-SPACE-NAME.hf.space/process-audio" \
  -F "file=@test.mp3" \
  -F "language=en"
```

Or visit the docs:
```
https://YOUR-USERNAME-YOUR-SPACE-NAME.hf.space/docs
```

## Troubleshooting

### Build fails
- Check logs in Space page
- Make sure all dependencies are in requirements.txt
- Verify Dockerfile syntax

### 403 Forbidden errors
- Set HUGGINGFACE_TOKEN in Space secrets
- Accept model terms:
  - https://huggingface.co/pyannote/speaker-diarization-3.1
  - https://huggingface.co/pyannote/segmentation-3.0
  - https://huggingface.co/pyannote/wespeaker-voxceleb-resnet34-LM

### Space sleeps after inactivity
- Free tier sleeps after 48h of inactivity
- Wakes up automatically on first request (takes ~30s)
- Upgrade to persistent ($5/month) to keep always-on

### Out of memory
- Reduce WHISPER_MODEL to "tiny" or "base"
- Upgrade to CPU Upgrade tier ($5/month for 32GB RAM)

## Cost Summary

- **CPU Basic (FREE)**: 16GB RAM, 2 vCPU
  - Perfect for development/low traffic
  - Sleeps after 48h inactivity

- **CPU Upgrade ($5/month)**: 32GB RAM, 8 vCPU
  - Better performance
  - Always-on option available

- **T4 GPU ($0.60/hour)**: Only if you need faster processing
  - ~$45/month if always-on
  - Can use on-demand (charged per second)

## Next Steps

1. Test your API thoroughly
2. Share the API URL with your mobile app
3. Monitor usage in Space analytics
4. Upgrade hardware if needed when you have users
