import asyncio
import logging
import os
from urllib.parse import quote

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel, Field

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("thumbai")

app = FastAPI(title="ThumbAI", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

HF_API_KEY = os.getenv("HF_API_KEY")
HF_API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
POLLINATIONS_URL = "https://image.pollinations.ai/prompt"


class GenerateRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=1000)


@app.post("/api/generate")
async def generate(req: GenerateRequest):
    prompt = req.prompt.strip()
    if not prompt:
        raise HTTPException(400, "Prompt is required")

    if HF_API_KEY:
        try:
            headers = {"Authorization": f"Bearer {HF_API_KEY}"}
            payload = {"inputs": prompt}
            async with httpx.AsyncClient() as client:
                for attempt in range(3):
                    resp = await client.post(
                        HF_API_URL, headers=headers, json=payload, timeout=120.0
                    )
                    if resp.status_code == 200:
                        content_type = resp.headers.get("content-type", "image/png")
                        return Response(
                            content=resp.content, media_type=content_type
                        )
                    try:
                        err = resp.json()
                        if "loading" in err.get("error", ""):
                            logger.info(
                                "Model loading, retrying in 5s (attempt %d/3)",
                                attempt + 1,
                            )
                            await asyncio.sleep(5)
                            continue
                    except Exception:
                        pass
                    resp.raise_for_status()
        except Exception as e:
            logger.warning("Hugging Face failed: %s", e)

    logger.info("Falling back to Pollinations.ai")
    url = f"{POLLINATIONS_URL}/{quote(prompt)}?width=1280&height=720&nologo=true"
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, timeout=120.0)
        resp.raise_for_status()
        return Response(content=resp.content, media_type="image/png")


@app.get("/")
async def root():
    return {"name": "ThumbAI", "version": "1.0.0", "endpoints": {"/api/generate": "POST - generate image from prompt"}}


@app.get("/health")
async def health():
    return {"status": "ok"}
