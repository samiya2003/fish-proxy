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
    message = data.get("message", {})
    text = message.get("text", data.get("text", ""))
    sample_rate = int(message.get("sampleRate", 16000))
    
    print(f"TEXT: {text}, SAMPLE RATE: {sample_rate}", flush=True)

    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.fish.audio/v1/tts",
            headers={"Authorization": f"Bearer {FISH_API_KEY}"},
            json={"text": text, "reference_id": VOICE_ID, "format": "mp3"},
            timeout=30
        )

    mp3_file = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
    mp3_file.write(response.content)
    mp3_file.close()
    
    pcm_file = tempfile.NamedTemporaryFile(suffix=".pcm", delete=False)
    pcm_path = pcm_file.name
    pcm_file.close()

    result = subprocess.run([
        "ffmpeg", "-y", "-i", mp3_file.name,
        "-f", "s16le", "-ac", "1", "-ar", str(sample_rate),
        pcm_path
    ], capture_output=True, text=True)
    
    print(f"FFMPEG: {result.stderr}", flush=True)

    with open(pcm_path, "rb") as f:
        pcm = f.read()

    os.unlink(mp3_file.name)
    os.unlink(pcm_path)

    return Response(content=pcm, media_type="audio/raw")
