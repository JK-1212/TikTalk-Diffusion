# TikTalk Diffusion Module

Text-to-Image generation module for **TikTalk** — an AI-powered English speaking coach designed for Singapore primary school students preparing for the PSLE Stimulus-Based Conversation.

This module generates **child-appropriate, cartoon-style images** that serve as visual stimuli for oral practice. Students observe the generated image and practice describing scenes, actions, and emotions in English.

**Model:** OpenAI DALL-E 3 &nbsp;|&nbsp; **Output:** 1024 x 1024 PNG &nbsp;|&nbsp; **Predefined Scenarios:** 80 prompts across 8 categories

---

## Table of Contents

- [How It Works — Prompt Assembly Pipeline](#how-it-works--prompt-assembly-pipeline)
- [User Input Specification](#user-input-specification)
- [Output Specification](#output-specification)
- [Quick Start](#quick-start)
- [API Reference](#api-reference)
- [Scenario Categories](#scenario-categories)
- [Project Structure](#project-structure)
- [Team](#team)

---

## How It Works — Prompt Assembly Pipeline

The core design of this module is a **3-layer prompt assembly** that turns simple user selections into a high-quality, child-friendly image prompt:

```
┌─────────────────────────────────────────────────────────────────┐
│                     USER INPUT (Layer 1)                        │
│  The user provides ONE of the following:                        │
│                                                                 │
│  Option A: Select a Category + Character + Action               │
│            e.g. category="outdoor", character="girl",           │
│                 action="riding a bicycle"                       │
│                                                                 │
│  Option B: Write a free-form prompt                             │
│            e.g. "A boy feeding ducks at a pond"                 │
├─────────────────────────────────────────────────────────────────┤
│                  TEMPLATE FILLING (Layer 2)                     │
│                                                                 │
│  If Option A: a template is selected from the category,         │
│  and {character} / {action} placeholders are replaced:          │
│                                                                 │
│  Template:  "A {character} {action} in the park"                │
│  Filled:    "A girl riding a bicycle in the park"               │
│                                                                 │
│  If Option B: the free-form prompt is used as-is.               │
├─────────────────────────────────────────────────────────────────┤
│                  STYLE SUFFIX (Layer 3)                         │
│                                                                 │
│  A fixed style suffix is automatically appended:                │
│                                                                 │
│  "children's book illustration style, bright and cheerful       │
│   colors, simple composition, clear objects, white background   │
│   or simple background, cute cartoon style, no text,            │
│   no watermark, child-friendly"                                 │
├─────────────────────────────────────────────────────────────────┤
│                  FINAL PROMPT → DALL-E 3                        │
│                                                                 │
│  "A girl riding a bicycle in the park, children's book          │
│   illustration style, bright and cheerful colors, simple        │
│   composition, clear objects, white background or simple        │
│   background, cute cartoon style, no text, no watermark,        │
│   child-friendly"                                               │
└─────────────────────────────────────────────────────────────────┘
```

This design ensures that **regardless of input method**, every generated image is consistently child-friendly and suitable for oral practice.

---

## User Input Specification

### Option A: Category-based Selection (Recommended for Frontend)

The user selects from three dropdown menus:

| Field | Type | Required | Description | Example Values |
|-------|------|----------|-------------|----------------|
| `category` | `string` | Yes | Scene category | `"outdoor"`, `"school"`, `"festivals"` |
| `character` | `string` | No (default: `"boy"`) | Main character in the scene | `"girl"`, `"mother"`, `"group of children"` |
| `action` | `string` | No (default: `"playing"`) | What the character is doing | `"cooking"`, `"reading a book"`, `"jumping rope"` |

**Available Characters** (14):
```
boy, girl, child, mother, father, grandmother, grandfather,
young boy, young girl, brother and sister, group of children,
little girl with pigtails, boy wearing glasses, girl in a school uniform
```

**Available Actions** (22):
```
cooking, reading a book, playing with a ball, drawing a picture,
eating, cleaning, talking to a friend, walking the dog,
watering plants, doing homework, singing, dancing,
playing with building blocks, writing in a notebook,
taking a photograph, playing a guitar, baking cookies,
feeding a bird, blowing bubbles, playing catch,
jumping rope, looking at a rainbow
```

**Example flow:**
```
User selects:  category = "outdoor"
               character = "girl"
               action = "riding a bicycle"

System picks a matching template from the "outdoor" category:
  → "A {character} riding a bicycle on a path"
  → Filled: "A girl riding a bicycle on a path"
  → + Style suffix
  → Final prompt sent to DALL-E 3
```

### Option B: Free-form Prompt

| Field | Type | Required | Description | Example |
|-------|------|----------|-------------|---------|
| `prompt` | `string` | Yes | A plain English description of the desired scene | `"A boy feeding ducks at a pond in the park"` |
| `num_images` | `int` | No (default: `1`, max: `4`) | Number of images to generate | `2` |
| `apply_style` | `bool` | No (default: `true`) | Whether to append the child-friendly style suffix | `true` |

The style suffix is appended automatically unless `apply_style` is set to `false`.

---

## Output Specification

### Generated Image

| Property | Value |
|----------|-------|
| Format | PNG |
| Resolution | 1024 x 1024 pixels |
| Style | Children's book illustration, cartoon |
| Color Palette | Bright, cheerful |
| Content Safety | Child-friendly, no violence, no text/watermarks |

### API Response Format

```json
{
  "success": true,
  "prompt_used": "A girl riding a bicycle on a path, children's book illustration style, bright and cheerful colors, simple composition, clear objects, white background or simple background, cute cartoon style, no text, no watermark, child-friendly",
  "image_paths": [
    "outputs/api_1711800000_0.png"
  ],
  "image_base64": [
    "iVBORw0KGgoAAAANSUhEUgAA..."
  ]
}
```

| Field | Type | Description |
|-------|------|-------------|
| `success` | `bool` | Whether generation succeeded |
| `prompt_used` | `string` | The full prompt sent to DALL-E 3 (including style suffix) |
| `image_paths` | `list[string]` | Local file paths of saved PNG images |
| `image_base64` | `list[string]` | Base64-encoded PNG images (for direct use by VLM module) |

---

## Quick Start

### 1. Install dependencies

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Set up API key

```bash
cp .env.example .env
```

Edit `.env` and paste your OpenAI API key (get one at https://platform.openai.com/api-keys):

```
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxx
```

### 3. Generate images via CLI

```bash
# Free-form prompt
python generate.py --prompt "A boy playing with a dog in the park"

# Category-based (generates all 10 prompts in the category)
python generate.py --category outdoor

# Generate all 80 predefined scenarios
python generate.py --all

# List all available categories
python generate.py --list

# Generate multiple images for one prompt
python generate.py --prompt "A girl reading" --num 4
```

Generated images are saved to the `outputs/` directory.

### 4. Run as API server

```bash
uvicorn app:app --reload --port 8000
```

Interactive API docs available at http://localhost:8000/docs.

---

## API Reference

### `GET /health`

Health check endpoint.

**Response:**
```json
{ "status": "ok", "model": "dall-e-3" }
```

### `GET /categories`

Returns all available scenario categories, characters, and actions.

**Response:**
```json
{
  "categories": {
    "daily_life": ["A boy playing in the kitchen", "..."],
    "school": ["..."],
    "outdoor": ["..."],
    "community": ["..."],
    "nature": ["..."],
    "festivals": ["..."],
    "helping": ["..."],
    "transportation": ["..."]
  },
  "characters": ["boy", "girl", "child", "..."],
  "actions": ["cooking", "reading a book", "..."]
}
```

### `POST /generate`

Generate image(s) from a text prompt.

**Request Body:**
```json
{
  "prompt": "A boy feeding ducks at a pond in the park",
  "num_images": 1,
  "apply_style": true
}
```

**Response Body:**
```json
{
  "success": true,
  "prompt_used": "A boy feeding ducks at a pond in the park, children's book illustration style, ...",
  "image_paths": ["outputs/api_1711800000_0.png"],
  "image_base64": ["iVBORw0KGgoAAAANSUhEUgAA..."]
}
```

### `GET /outputs/{filename}`

Serve a previously generated image file by filename.

---

## Scenario Categories

8 categories, 10 prompts each, 80 total — all designed around scenes familiar to Singapore primary school students.

| Category | Description | Example Prompts |
|----------|-------------|-----------------|
| `daily_life` | Home and family activities | Cooking in the kitchen, family breakfast, feeding a pet cat |
| `school` | Classroom and campus scenes | Science experiment, art class, presenting a project |
| `outdoor` | Parks, playgrounds, beaches | Flying kites, building sandcastles, feeding ducks |
| `community` | Neighbourhood and public spaces | Hawker centre, library, lion dance performance |
| `nature` | Animals, plants, weather | Zoo visit, planting flowers, stargazing with telescope |
| `festivals` | Cultural celebrations | Chinese New Year red packets, Mid-Autumn lanterns, Christmas tree |
| `helping` | Kindness and social responsibility | Helping elderly cross road, picking up litter, donating toys |
| `transportation` | Vehicles and travel | MRT train, school bus, airport, ferry |

---

## Project Structure

```
TikTalk-Diffusion/
├── generate.py            # CLI tool — generate images from terminal
├── app.py                 # FastAPI server — HTTP API for other modules
├── prompt_templates.py    # Prompt engineering: templates, characters, actions, style suffix
├── requirements.txt       # Python dependencies
├── .env.example           # API key template
├── .gitignore
├── outputs/               # Generated images saved here (git-ignored)
└── README.md
```

### Integration with Other TikTalk Modules

```
┌──────────────┐     POST /generate      ┌──────────────────┐
│   Frontend   │ ──────────────────────→  │    Diffusion     │
│   (React)    │ ←──────────────────────  │  Module (this)   │
│              │    image_base64 / path   │   DALL-E 3 API   │
└──────────────┘                          └──────────────────┘
                                                  │
                                           image_base64
                                                  │
                                                  ▼
                                          ┌──────────────┐
                                          │  VLM Module   │
                                          │ (GPT-4 Vision)│
                                          │ → Oral Q&A    │
                                          └──────────────┘
```

---

## Team

**NUS ISS — ISY5004 Intelligent Sensing Systems**

TikTalk Team: Yu Guotao, Ke Liwen, Liu Jiajia, Zheng Jiecheng, Shang Jiakun
