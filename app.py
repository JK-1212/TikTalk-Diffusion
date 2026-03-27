"""
TikTalk Diffusion Module - API Server

Simple FastAPI server for other modules (VLM, Frontend) to call.

Usage:
    uvicorn app:app --reload --port 8000

API Endpoints:
    POST /generate         - Generate image from prompt
    GET  /categories       - List available scenario categories
    GET  /health           - Health check
"""

import os
import time
import base64
from io import BytesIO
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field

from google import genai
from google.genai import types

from prompt_templates import (
    build_prompt,
    fill_template,
    SCENARIO_TEMPLATES,
    CHARACTERS,
    ACTIONS,
)

load_dotenv()

app = FastAPI(title="TikTalk Diffusion Module", version="0.1.0")

OUTPUT_DIR = Path(__file__).parent / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)
MODEL_NAME = "imagen-3.0-generate-002"


def get_client() -> genai.Client:
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="GOOGLE_API_KEY not configured")
    return genai.Client(api_key=api_key)


# --- Request / Response Models ---

class GenerateRequest(BaseModel):
    prompt: str = Field(..., description="Text prompt describing the scene")
    num_images: int = Field(default=1, ge=1, le=4, description="Number of images (1-4)")
    apply_style: bool = Field(default=True, description="Whether to apply child-friendly style suffix")


class GenerateResponse(BaseModel):
    success: bool
    prompt_used: str
    image_paths: list[str]
    image_base64: list[str] = Field(default_factory=list, description="Base64-encoded images")


# --- Endpoints ---

@app.get("/health")
def health():
    return {"status": "ok", "model": MODEL_NAME}


@app.get("/categories")
def list_categories():
    """List all available scenario categories and their prompts."""
    return {
        "categories": {
            cat: [fill_template(t) for t in templates]
            for cat, templates in SCENARIO_TEMPLATES.items()
        },
        "characters": CHARACTERS,
        "actions": ACTIONS,
    }


@app.post("/generate", response_model=GenerateResponse)
def generate(req: GenerateRequest):
    """Generate image(s) from a text prompt."""
    client = get_client()

    full_prompt = build_prompt(req.prompt) if req.apply_style else req.prompt

    try:
        response = client.models.generate_images(
            model=MODEL_NAME,
            prompt=full_prompt,
            config=types.GenerateImagesConfig(
                number_of_images=req.num_images,
                aspect_ratio="1:1",
                safety_filter_level="BLOCK_LOW_AND_ABOVE",
            ),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image generation failed: {e}")

    timestamp = int(time.time())
    image_paths = []
    image_base64_list = []

    for i, gen_img in enumerate(response.generated_images):
        filename = f"api_{timestamp}_{i}.png"
        filepath = OUTPUT_DIR / filename
        gen_img.image.save(str(filepath))
        image_paths.append(str(filepath))

        # Also return base64 so VLM module can use it directly
        buffer = BytesIO()
        gen_img.image.save(buffer, format="PNG")
        b64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
        image_base64_list.append(b64)

    return GenerateResponse(
        success=True,
        prompt_used=full_prompt,
        image_paths=image_paths,
        image_base64=image_base64_list,
    )


@app.get("/outputs/{filename}")
def get_image(filename: str):
    """Serve a generated image file."""
    filepath = OUTPUT_DIR / filename
    if not filepath.exists():
        raise HTTPException(status_code=404, detail="Image not found")
    return FileResponse(filepath, media_type="image/png")
