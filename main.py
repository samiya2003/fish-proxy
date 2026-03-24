from fastapi import FastAPI, Request
from fastapi.responses import Response
import httpx
import os
import subprocess
import tempfile

app = FastAPI()

FISH_API_KEY = os.environ.get("FISH_API_KEY")
VOICE_ID = os.environ.get("VOICE_ID")

@app.post("/tts")
async def tts(request: Request):
    data = await request.json()
    text = data.get("text", "")
    sample_rate = data.get("sampleRate", 16000)

    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.fish.audio/v1/tts",
            headers={"Authorization": f"Bearer {FISH_API_KEY}"},
            json={"text": text, "reference_id": VOICE_ID, "format": "mp3"},
            timeout=30
        )

    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
        f.write(response.content)
        mp3_path = f.name

    pcm_path = mp3_path.replace(".mp3", ".pcm")
    subprocess.run([
        "ffmpeg", "-y", "-i", mp3_path,
        "-f", "s16le", "-ac", "1", "-ar", str(sample_rate),
        pcm_path
    ], capture_output=True)

    with open(pcm_path, "rb") as f:
        pcm = f.read()

    os.unlink(mp3_path)
    os.unlink(pcm_path)

    return Response(content=pcm, media_type="audio/raw")
