from fastapi import FastAPI, Request
from fastapi.responses import Response
import httpx
import os
from pydub import AudioSegment
import io

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
    
    audio = AudioSegment.from_mp3(io.BytesIO(response.content))
    audio = audio.set_channels(1).set_frame_rate(sample_rate).set_sample_width(2)
    pcm = audio.raw_data
    
    return Response(content=pcm, media_type="audio/raw")
