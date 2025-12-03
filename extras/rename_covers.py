#!/usr/bin/env python3
"""
Rename slide_XX_image_1.jpg files to cover_XX.jpg
"""

import os
from pathlib import Path

def main():
    images_dir = Path("/Users/ahmshalan/Projects/mobifly/ppt-generate/branding/covers/images")
    
    if not images_dir.exists():
        print(f"Error: Directory not found: {images_dir}")
        return
    
    # Get all files matching the pattern
    files = sorted(images_dir.glob("slide_*_image_1.jpg"))
    
    if not files:
        print("No files matching pattern 'slide_*_image_1.jpg' found")
        return
    
    print(f"Found {len(files)} files to rename\n")
    
    renamed_count = 0
    for file_path in files:
        # Extract the slide number from the filename
        filename = file_path.name
        parts = filename.split("_")
        if len(parts) >= 3:
            slide_num = parts[1]  # Gets '01', '02', etc.
            new_filename = f"cover_{slide_num}.jpg"
            new_path = images_dir / new_filename
            
            try:
                file_path.rename(new_path)
                print(f"✓ Renamed: {filename} -> {new_filename}")
                renamed_count += 1
            except Exception as e:
                print(f"✗ Error renaming {filename}: {e}")
    
    print(f"\n{'='*60}")
    print(f"✓ Renaming complete!")
    print(f"  Total files renamed: {renamed_count}")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()



