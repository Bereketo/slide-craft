#!/usr/bin/env python3
"""
Generate AI descriptions for cover images using OpenAI's GPT-4 Vision API.
This script analyzes each cover image and generates a description to help users
choose the appropriate cover based on content, theme, colors, and mood.

Features:
- Parallel processing with configurable batch size (default: 16)
- Automatic retry on failures
- Progress tracking
"""

import json
import os
import base64
from pathlib import Path
from typing import List, Dict, Tuple
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

# You'll need to install: pip install openai
try:
    from openai import OpenAI
except ImportError:
    print("Error: OpenAI library not installed. Run: pip install openai")
    exit(1)


def encode_image_to_base64(image_path: Path) -> str:
    """Encode image to base64 string for API submission."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


def analyze_cover_image(client: OpenAI, image_path: Path, cover_id: int, max_retries: int = 3) -> Tuple[int, str, bool]:
    """
    Use GPT-4 Vision to analyze a cover image and generate a description.
    
    Args:
        client: OpenAI client instance
        image_path: Path to the cover image
        cover_id: Cover ID number
        max_retries: Maximum number of retry attempts
        
    Returns:
        Tuple of (cover_id, description, success)
    """
    # Encode image
    base64_image = encode_image_to_base64(image_path)
    
    # Create the prompt
    prompt = """Analyze this PowerPoint cover slide background image and provide a concise description (2-3 sentences max) that includes:
1. The main subject/theme (e.g., business meeting, technology, nature, cityscape, abstract)
2. The dominant colors and mood (e.g., professional blue tones, warm and energetic, minimalist and modern)
3. The best use case (e.g., suitable for corporate presentations, tech startups, creative projects, financial reports)

Be specific and practical to help users choose the right cover for their presentation content.
Format: Just provide the description directly, no labels or prefixes."""
    
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",  # Fast and cost-effective model with vision
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}",
                                    "detail": "low"  # Use "low" for faster/cheaper processing
                                }
                            }
                        ]
                    }
                ],
                max_tokens=150
            )
            
            description = response.choices[0].message.content.strip()
            return (cover_id, description, True)
            
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
                continue
            else:
                return (cover_id, f"Error: {str(e)}", False)


def update_index_with_descriptions(
    index_path: Path,
    images_dir: Path,
    api_key: str,
    start_from: int = 1,
    limit: int = None,
    batch_size: int = 16
):
    """
    Update the index.json file with AI-generated descriptions for each cover.
    Uses parallel processing to handle multiple images concurrently.
    
    Args:
        index_path: Path to index.json
        images_dir: Path to images directory
        api_key: OpenAI API key
        start_from: Cover ID to start from (useful for resuming)
        limit: Maximum number of covers to process (None for all)
        batch_size: Number of parallel requests (default: 16)
    """
    # Initialize OpenAI client
    client = OpenAI(api_key=api_key)
    
    # Load index.json
    print(f"Loading index from: {index_path}")
    with open(index_path, 'r', encoding='utf-8') as f:
        index_data = json.load(f)
    
    # Create a dictionary for quick lookup by cover ID
    covers_dict = {cover['id']: cover for cover in index_data['covers']}
    
    total_covers = len(index_data['covers'])
    print(f"Found {total_covers} covers in index")
    print(f"Batch size: {batch_size} parallel requests\n")
    
    # Prepare list of covers to process
    covers_to_process = []
    for cover in index_data['covers']:
        cover_id = cover['id']
        
        # Skip if before start_from
        if cover_id < start_from:
            continue
        
        # Check limit
        if limit and len(covers_to_process) >= limit:
            break
        
        image_filename = cover['image']
        image_path = images_dir / image_filename
        
        if not image_path.exists():
            print(f"  Warning: Image not found: {image_path}")
            continue
        
        covers_to_process.append((cover_id, image_path))
    
    total_to_process = len(covers_to_process)
    print(f"Processing {total_to_process} covers...\n")
    
    # Process covers in parallel
    successful = 0
    failed = 0
    start_time = time.time()
    
    with ThreadPoolExecutor(max_workers=batch_size) as executor:
        # Submit all tasks
        future_to_cover = {
            executor.submit(analyze_cover_image, client, image_path, cover_id): cover_id
            for cover_id, image_path in covers_to_process
        }
        
        # Process completed tasks
        for i, future in enumerate(as_completed(future_to_cover), 1):
            cover_id = future_to_cover[future]
            try:
                result_id, description, success = future.result()
                
                if success:
                    # Update the cover description
                    covers_dict[result_id]['description'] = description
                    successful += 1
                    status = "✓"
                    preview = description[:60] + "..." if len(description) > 60 else description
                else:
                    failed += 1
                    status = "✗"
                    preview = description
                
                # Progress update
                elapsed = time.time() - start_time
                avg_time = elapsed / i
                remaining = (total_to_process - i) * avg_time
                
                print(f"[{i}/{total_to_process}] {status} Cover {result_id:02d} | "
                      f"Success: {successful} | Failed: {failed} | "
                      f"ETA: {remaining:.1f}s")
                print(f"    {preview}")
                
            except Exception as e:
                failed += 1
                print(f"[{i}/{total_to_process}] ✗ Cover {cover_id:02d} - Exception: {str(e)}")
    
    # Save updated index
    print(f"\nSaving updated index to: {index_path}")
    with open(index_path, 'w', encoding='utf-8') as f:
        json.dump(index_data, f, indent=2, ensure_ascii=False)
    
    total_time = time.time() - start_time
    
    print(f"\n{'='*60}")
    print(f"✓ Processing Complete!")
    print(f"{'='*60}")
    print(f"  Total processed: {total_to_process}")
    print(f"  Successful: {successful}")
    print(f"  Failed: {failed}")
    print(f"  Total time: {total_time:.1f}s")
    print(f"  Average time per image: {total_time/total_to_process:.2f}s")
    print(f"{'='*60}")


def main():
    # Configuration
    project_root = Path("/Users/ahmshalan/Projects/mobifly/ppt-generate")
    index_path = project_root / "branding/covers/index.json"
    images_dir = project_root / "branding/covers/images"
    
    # Get API key from environment variable
    # ⚠️  WARNING: API key is hardcoded below - for production, use environment variables only!
    # To use env var: export OPENAI_API_KEY='your-key-here' and remove the default value below
    api_key = os.environ.get("OPENAI_API_KEY", "")

    print("="*60)
    print("Cover Image Description Generator")
    print("="*60)
    print(f"Index file: {index_path}")
    print(f"Images directory: {images_dir}")
    print("="*60)
    print()
    
    # Process all covers
    # You can add parameters:
    # - start_from=10 to resume from cover 10
    # - limit=5 to process only 5 covers (useful for testing)
    # - batch_size=8 to reduce parallel requests (if hitting rate limits)
    update_index_with_descriptions(
        index_path=index_path,
        images_dir=images_dir,
        api_key=api_key,
        start_from=1,   # Start from cover 1
        limit=None,     # Process all covers (change to 5 for testing, e.g., limit=5)
        batch_size=16   # Number of parallel requests (default: 16)
    )


if __name__ == "__main__":
    main()

