from fastapi import FastAPI, Request
from fastapi.responses import Response
import httpx
import os

app = FastAPI()

FISH_API_KEY = os.environ.get("FISH_API_KEY")
VOICE_ID = os.environ.get("VOICE_ID")

@app.post("/tts")
async def tts(request: Request):
    data = await request.json()
    message = data.get("message", {})
    text = message.get("text", data.get("text", ""))

    print(f"TEXT: {text}", flush=True)

    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.fish.audio/v1/tts",
            headers={"Authorization": f"Bearer {FISH_API_KEY}"},
            json={"text": text, "reference_id": VOICE_ID, "format": "mp3"},
            timeout=30
        )

    return Response(content=response.content, media_type="audio/mpeg")
