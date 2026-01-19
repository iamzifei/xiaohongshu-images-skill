#!/usr/bin/env python3
"""
Cover Image Generation Script - Using Gemini REST API

Usage:
    python generate_images.py <prompts.json>

The prompts JSON file should be located in the article folder directory,
and generated images will be saved to <article-folder>/_attachments/ directory.

JSON Format:
{
    "article": {
        "title": "Article Title",
        "theme": "Brief description of article theme"
    },
    "cover": {
        "prompt": "Full image generation prompt",
        "aspect_ratio": "600x350"
    }
}

Or simplified format:
{
    "theme": "Article theme description for cover image generation"
}
"""

import os
import sys
import json
import re
import base64
import urllib.request
import urllib.error
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file in script's parent directory
script_dir = Path(__file__).parent.parent
load_dotenv(script_dir / ".env")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    print("Error: GEMINI_API_KEY environment variable not found")
    print("Please create a .env file with GEMINI_API_KEY=your_key")
    print("Get your API key from: https://aistudio.google.com/app/apikey")
    sys.exit(1)


# Cover image template - New Yorker editorial cartoon style
COVER_TEMPLATE = """Generate a hand-drawn illustration in the style of *The New Yorker* editorial cartoons.

Style specifications:
- Hand-drawn, sketch-like quality
- Minimalist and thoughtful composition
- Subtle humor or irony if appropriate
- Clean lines with cross-hatching for shading
- Limited color palette or black and white
- Editorial cartoon aesthetic

Image dimensions: 600px width × 350px height (landscape)

Theme to illustrate:
{theme}

The illustration should visually capture the essence and main message of this theme in a clever, artistic way typical of New Yorker cartoons."""


def sanitize_prompt(prompt: str) -> str:
    """
    Sanitize prompt text to handle newlines, paragraph separators, and special characters.
    """
    if not prompt:
        return prompt

    # Normalize line endings: CRLF -> LF, CR -> LF
    text = prompt.replace('\r\n', '\n').replace('\r', '\n')

    # Replace paragraph separator (U+2029) and line separator (U+2028) with newlines
    text = text.replace('\u2029', '\n\n').replace('\u2028', '\n')

    # Split into lines and strip each line
    lines = [line.strip() for line in text.split('\n')]

    # Collapse multiple empty lines into single empty line
    collapsed_lines = []
    prev_empty = False
    for line in lines:
        is_empty = len(line) == 0
        if is_empty:
            if not prev_empty:
                collapsed_lines.append('')
            prev_empty = True
        else:
            collapsed_lines.append(line)
            prev_empty = False

    # Join with single newlines
    text = '\n'.join(collapsed_lines)

    # Strip leading/trailing whitespace from the entire text
    text = text.strip()

    # Collapse multiple spaces into single space (but preserve newlines)
    text = re.sub(r'[ \t]+', ' ', text)

    return text


def generate_image(prompt: str, filename: str, images_dir: Path) -> str:
    """Generate image using Gemini REST API"""
    print(f"Generating: {filename}...")

    # Sanitize the prompt to handle newlines and special characters
    clean_prompt = sanitize_prompt(prompt)

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3-pro-image-preview:generateContent?key={GEMINI_API_KEY}"

    payload = {
        "contents": [{
            "parts": [{"text": clean_prompt}]
        }],
        "generationConfig": {
            "responseModalities": ["TEXT", "IMAGE"]
        }
    }

    headers = {"Content-Type": "application/json"}

    try:
        req = urllib.request.Request(url, data=json.dumps(payload).encode(), headers=headers)
        with urllib.request.urlopen(req, timeout=180) as response:
            result = json.loads(response.read().decode())

        # Extract image
        for part in result.get("candidates", [{}])[0].get("content", {}).get("parts", []):
            if "inlineData" in part:
                image_data = base64.b64decode(part["inlineData"]["data"])
                filepath = images_dir / filename
                with open(filepath, "wb") as f:
                    f.write(image_data)
                print(f"  Saved: {filepath}")
                return str(filepath)

        print(f"  {filename} generation failed: No image returned")
        return None

    except urllib.error.HTTPError as e:
        error_body = e.read().decode() if e.fp else ""
        print(f"  {filename} generation failed: HTTP {e.code}")
        print(f"  Error details: {error_body[:200]}")
        return None
    except Exception as e:
        print(f"  {filename} generation failed: {e}")
        return None


def load_prompts_json(json_path: Path) -> dict:
    """
    Load prompts JSON file.

    Supports two formats:
    1. Full format: {"article": {...}, "cover": {"prompt": "..."}}
    2. Simple format: {"theme": "..."}

    Returns:
        Dictionary with cover prompt ready to use
    """
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Determine prompt
    if "cover" in data and "prompt" in data["cover"]:
        # Full prompt provided
        prompt = data["cover"]["prompt"]
    elif "theme" in data:
        # Use template with theme
        prompt = COVER_TEMPLATE.format(theme=data["theme"])
    elif "article" in data and "theme" in data["article"]:
        # Theme in article object
        prompt = COVER_TEMPLATE.format(theme=data["article"]["theme"])
    else:
        raise ValueError("JSON must contain 'cover.prompt' or 'theme' field")

    return {
        "title": data.get("article", {}).get("title", "Untitled"),
        "prompt": prompt
    }


def main():
    # Check command line arguments
    if len(sys.argv) < 2:
        print("Usage: python generate_images.py <prompts.json>")
        print()
        print("The prompts JSON file should be in the article folder directory.")
        print("Generated cover image will be saved to <article-folder>/_attachments/cover-xhs.png")
        print()
        print("JSON format examples:")
        print()
        print("Simple format:")
        print('''
{
    "theme": "The irony of social media bringing people together while isolating them"
}
''')
        print("Full format:")
        print('''
{
    "article": {
        "title": "Article Title",
        "theme": "Article theme description"
    },
    "cover": {
        "prompt": "Full custom image generation prompt..."
    }
}
''')
        sys.exit(1)

    json_path = Path(sys.argv[1]).resolve()

    if not json_path.exists():
        print(f"Error: File does not exist: {json_path}")
        sys.exit(1)

    # Determine output directory (_attachments subdirectory of JSON file's directory)
    output_dir = json_path.parent
    attachments_dir = output_dir / "_attachments"
    attachments_dir.mkdir(parents=True, exist_ok=True)

    # Load prompts
    try:
        config = load_prompts_json(json_path)
    except Exception as e:
        print(f"Error: Failed to load prompts file: {e}")
        sys.exit(1)

    print("=" * 60)
    print("Cover Image Generation")
    print(f"Article: {config['title']}")
    print(f"Prompts file: {json_path}")
    print(f"Output directory: {attachments_dir}")
    print("=" * 60)

    # Generate cover image
    result = generate_image(config["prompt"], "cover-xhs.png", attachments_dir)

    print()
    print("=" * 60)
    if result:
        print("Cover image generated successfully!")
        print(f"Location: {result}")
    else:
        print("Cover image generation failed.")
    print("=" * 60)

    return 0 if result else 1


if __name__ == "__main__":
    sys.exit(main())
