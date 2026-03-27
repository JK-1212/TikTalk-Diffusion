# TikTalk Diffusion Module

Text-to-Image generation module for [TikTalk](https://github.com/JK-1212/TikTalk-Diffusion) — an AI-powered English speaking coach for primary school students in Singapore.

Uses **Google Imagen 3** API to generate child-appropriate images for PSLE oral practice.

## Quick Start

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Set up API key

```bash
cp .env.example .env
# Edit .env and paste your Google API key
# Get one at: https://aistudio.google.com/apikey
```

### 3. Generate images

```bash
# Generate a single image
python generate.py --prompt "A boy playing with a dog in the park"

# Generate from a category (daily_life / school / outdoor / community / nature)
python generate.py --category outdoor

# Generate all predefined scenarios
python generate.py --all

# List all categories
python generate.py --list
```

### 4. Run API server (for other modules to call)

```bash
uvicorn app:app --reload --port 8000
```

Then call from other modules:

```python
import requests

resp = requests.post("http://localhost:8000/generate", json={
    "prompt": "A girl reading a book in the library",
    "num_images": 1
})
data = resp.json()
# data["image_base64"][0] — base64 encoded image for VLM module
# data["image_paths"][0]  — local file path
```

## Project Structure

```
├── generate.py          # CLI tool for generating images
├── app.py               # FastAPI server for other modules
├── prompt_templates.py  # Prompt engineering & scenario templates
├── requirements.txt
├── .env.example         # API key template
└── outputs/             # Generated images saved here
```

## Prompt Design

All prompts are automatically enhanced with a child-friendly style suffix to ensure:
- Cartoon / illustration style
- Simple composition with clear objects
- Bright, cheerful colors
- No text or watermarks

Edit `prompt_templates.py` to customize prompts and add new scenarios.

## Team

NUS ISS - ISY5004 Intelligent Sensing Systems

TikTalk Team: Yu Guotao, Ke Liwen, Liu Jiajia, Zheng Jiecheng, Shang Jiakun
