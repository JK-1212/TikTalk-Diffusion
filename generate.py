"""
TikTalk Diffusion Module - Image Generator

Uses OpenAI DALL-E 3 API to generate child-appropriate images
for English oral practice (PSLE Stimulus-Based Conversation).

Usage:
    # Generate a single image from a custom prompt
    python generate.py --prompt "A boy playing with a dog in the park"

    # Generate from a predefined scenario category
    python generate.py --category outdoor

    # Generate all predefined scenarios
    python generate.py --all

    # Specify number of images per prompt
    python generate.py --prompt "A girl reading" --num 4
"""

import argparse
import os
import time
from pathlib import Path

import requests
from dotenv import load_dotenv
from openai import OpenAI

from prompt_templates import (
    STYLE_SUFFIX,
    SCENARIO_TEMPLATES,
    CHARACTERS,
    ACTIONS,
    build_prompt,
    fill_template,
)

load_dotenv()

# --- Configuration ---
OUTPUT_DIR = Path(__file__).parent / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)

MODEL_NAME = "dall-e-3"


def get_client() -> OpenAI:
    """Create an OpenAI client."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError(
            "OPENAI_API_KEY not found. "
            "Copy .env.example to .env and fill in your API key.\n"
            "Get one at: https://platform.openai.com/api-keys"
        )
    return OpenAI(api_key=api_key)


def generate_image(
    client: OpenAI,
    prompt: str,
    num_images: int = 1,
    save_prefix: str = "img",
) -> list[Path]:
    """
    Generate images using OpenAI DALL-E 3.

    Args:
        client: OpenAI client
        prompt: Text prompt for image generation
        num_images: Number of images to generate (1-4)
        save_prefix: Filename prefix for saved images

    Returns:
        List of paths to saved images
    """
    full_prompt = build_prompt(prompt)
    print(f"Generating: {prompt}")
    print(f"Full prompt: {full_prompt[:100]}...")

    saved_paths = []
    timestamp = int(time.time())

    # DALL-E 3 only supports n=1, so loop for multiple images
    for i in range(num_images):
        print(f"  Requesting image {i+1}/{num_images}...")
        response = client.images.generate(
            model=MODEL_NAME,
            prompt=full_prompt,
            size="1024x1024",
            quality="standard",
            n=1,
        )

        image_url = response.data[0].url
        img_data = requests.get(image_url, timeout=60).content

        filename = f"{save_prefix}_{timestamp}_{i}.png"
        filepath = OUTPUT_DIR / filename
        filepath.write_bytes(img_data)
        print(f"  Saved: {filepath}")
        saved_paths.append(filepath)

    return saved_paths


def generate_from_category(client: OpenAI, category: str, num_images: int = 1):
    """Generate images for all prompts in a scenario category."""
    if category not in SCENARIO_TEMPLATES:
        print(f"Unknown category: {category}")
        print(f"Available: {list(SCENARIO_TEMPLATES.keys())}")
        return

    templates = SCENARIO_TEMPLATES[category]
    print(f"\n=== Category: {category} ({len(templates)} prompts) ===\n")

    for template in templates:
        prompt = fill_template(template, character="boy", action="playing")
        generate_image(client, prompt, num_images=num_images, save_prefix=category)
        print()


def main():
    parser = argparse.ArgumentParser(description="TikTalk Diffusion - Image Generator")
    parser.add_argument("--prompt", type=str, help="Custom prompt for image generation")
    parser.add_argument("--category", type=str, help="Scenario category to generate")
    parser.add_argument("--all", action="store_true", help="Generate all predefined scenarios")
    parser.add_argument("--num", type=int, default=1, help="Number of images per prompt (1-4)")
    parser.add_argument("--list", action="store_true", help="List all available categories")
    args = parser.parse_args()

    if args.list:
        print("Available scenario categories:")
        for cat, templates in SCENARIO_TEMPLATES.items():
            print(f"  {cat}: {len(templates)} prompts")
        return

    client = get_client()

    if args.prompt:
        generate_image(client, args.prompt, num_images=args.num, save_prefix="custom")

    elif args.category:
        generate_from_category(client, args.category, num_images=args.num)

    elif args.all:
        for category in SCENARIO_TEMPLATES:
            generate_from_category(client, category, num_images=args.num)

    else:
        # Default: generate one example image
        print("No arguments given. Generating a demo image...\n")
        generate_image(
            client,
            "A boy and a girl playing with a golden retriever in a sunny park",
            num_images=1,
            save_prefix="demo",
        )
        print("\nTip: Run with --help to see all options")


if __name__ == "__main__":
    main()
