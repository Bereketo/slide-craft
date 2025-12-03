#!/usr/bin/env python3
"""
Generate AI descriptions for cover images using Ollama's LLaVA model (FREE, runs locally).
This script analyzes each cover image and generates a description to help users
choose the appropriate cover based on content, theme, colors, and mood.

Requirements:
1. Install Ollama: https://ollama.ai
2. Pull the LLaVA model: ollama pull llava
3. Install requests: pip install requests
"""

import json
import base64
from pathlib import Path
from typing import Dict
import time
import requests


def encode_image_to_base64(image_path: Path) -> str:
    """Encode image to base64 string for API submission."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


def analyze_cover_image_ollama(image_path: Path, cover_id: int, model: str = "llava") -> str:
    """
    Use Ollama's LLaVA model to analyze a cover image and generate a description.
    
    Args:
        image_path: Path to the cover image
        cover_id: Cover ID number
        model: Ollama model to use (default: llava)
        
    Returns:
        Description string for the cover
    """
    print(f"  Analyzing cover {cover_id}...")
    
    # Encode image
    base64_image = encode_image_to_base64(image_path)
    
    # Create the prompt
    prompt = """Analyze this PowerPoint cover slide background image and provide a concise description (2-3 sentences max) that includes:
1. The main subject/theme (e.g., business meeting, technology, nature, cityscape, abstract)
2. The dominant colors and mood (e.g., professional blue tones, warm and energetic, minimalist and modern)
3. The best use case (e.g., suitable for corporate presentations, tech startups, creative projects, financial reports)

Be specific and practical to help users choose the right cover for their presentation content."""
    
    try:
        # Call Ollama API
        response = requests.post(
            'http://localhost:11434/api/generate',
            json={
                'model': model,
                'prompt': prompt,
                'images': [base64_image],
                'stream': False
            },
            timeout=120  # 2 minutes timeout
        )
        
        if response.status_code == 200:
            result = response.json()
            description = result['response'].strip()
            return description
        else:
            print(f"    Error: Ollama API returned status {response.status_code}")
            return "Standard title with subtitle cover"
            
    except requests.exceptions.ConnectionError:
        print(f"    Error: Cannot connect to Ollama. Make sure Ollama is running (ollama serve)")
        return "Standard title with subtitle cover"
    except Exception as e:
        print(f"    Error analyzing image: {e}")
        return "Standard title with subtitle cover"


def check_ollama_running() -> bool:
    """Check if Ollama service is running."""
    try:
        response = requests.get('http://localhost:11434/api/tags', timeout=5)
        return response.status_code == 200
    except:
        return False


def check_model_available(model: str = "llava") -> bool:
    """Check if the specified model is available in Ollama."""
    try:
        response = requests.get('http://localhost:11434/api/tags', timeout=5)
        if response.status_code == 200:
            models = response.json().get('models', [])
            model_names = [m['name'].split(':')[0] for m in models]
            return model in model_names
    except:
        return False
    return False


def update_index_with_descriptions(
    index_path: Path,
    images_dir: Path,
    model: str = "llava",
    start_from: int = 1,
    limit: int = None
):
    """
    Update the index.json file with AI-generated descriptions for each cover.
    
    Args:
        index_path: Path to index.json
        images_dir: Path to images directory
        model: Ollama model to use
        start_from: Cover ID to start from (useful for resuming)
        limit: Maximum number of covers to process (None for all)
    """
    # Check if Ollama is running
    if not check_ollama_running():
        print("❌ Error: Ollama is not running!")
        print("\nTo start Ollama, run:")
        print("  ollama serve")
        print("\nOr if Ollama is installed as a service, it should start automatically.")
        return
    
    # Check if model is available
    if not check_model_available(model):
        print(f"❌ Error: Model '{model}' not found!")
        print(f"\nTo install the {model} model, run:")
        print(f"  ollama pull {model}")
        return
    
    print(f"✓ Ollama is running and {model} model is available\n")
    
    # Load index.json
    print(f"Loading index from: {index_path}")
    with open(index_path, 'r', encoding='utf-8') as f:
        index_data = json.load(f)
    
    total_covers = len(index_data['covers'])
    print(f"Found {total_covers} covers in index\n")
    
    # Process each cover
    processed = 0
    for cover in index_data['covers']:
        cover_id = cover['id']
        
        # Skip if before start_from
        if cover_id < start_from:
            continue
        
        # Check limit
        if limit and processed >= limit:
            print(f"\nReached processing limit of {limit} covers")
            break
        
        image_filename = cover['image']
        image_path = images_dir / image_filename
        
        if not image_path.exists():
            print(f"  Warning: Image not found: {image_path}")
            continue
        
        print(f"Processing cover {cover_id}/{total_covers}: {image_filename}")
        
        # Generate description
        description = analyze_cover_image_ollama(image_path, cover_id, model)
        
        # Update the cover description
        cover['description'] = description
        print(f"  ✓ Description: {description[:80]}...")
        print()
        
        processed += 1
        
        # Small delay to let system breathe
        if processed < (limit or total_covers):
            time.sleep(0.2)
    
    # Save updated index
    print(f"Saving updated index to: {index_path}")
    with open(index_path, 'w', encoding='utf-8') as f:
        json.dump(index_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n{'='*60}")
    print(f"✓ Successfully processed {processed} covers!")
    print(f"{'='*60}")


def main():
    # Configuration
    project_root = Path("/Users/ahmshalan/Projects/mobifly/ppt-generate")
    index_path = project_root / "branding/covers/index.json"
    images_dir = project_root / "branding/covers/images"
    
    print("="*60)
    print("Cover Image Description Generator (Ollama/LLaVA - FREE)")
    print("="*60)
    print(f"Index file: {index_path}")
    print(f"Images directory: {images_dir}")
    print("="*60)
    print()
    
    # Process all covers
    # You can add parameters:
    # - start_from=10 to resume from cover 10
    # - limit=5 to process only 5 covers (useful for testing)
    # - model="llava:13b" to use a different model variant
    update_index_with_descriptions(
        index_path=index_path,
        images_dir=images_dir,
        model="llava",    # Model to use
        start_from=1,     # Start from cover 1
        limit=None        # Process all covers (change to 5 for testing)
    )


if __name__ == "__main__":
    main()

