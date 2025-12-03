#!/usr/bin/env python3
"""
Reorganize PwC cover images:
- Move PwC logo to a separate logo directory
- Keep only unique cover photos (even-numbered images)
- Update JSON files with correct references
"""

import json
import shutil
from pathlib import Path

def main():
    covers_dir = Path("/Users/ahmshalan/Projects/mobifly/ppt-generate/branding/covers")
    images_dir = covers_dir / "images"
    logo_dir = covers_dir / "logo"
    
    # Create logo directory
    logo_dir.mkdir(exist_ok=True)
    
    # Move the first PwC logo image to logo directory
    first_logo = images_dir / "cover_01_image_1.png"
    if first_logo.exists():
        logo_dest = logo_dir / "pwc_logo.png"
        shutil.copy2(first_logo, logo_dest)
        print(f"✓ Copied PwC logo to: {logo_dest}")
    
    # Process each cover
    total_deleted = 0
    total_updated = 0
    
    for cover_num in range(1, 76):
        json_file = covers_dir / f"cover_{cover_num:02d}_title_subtitle.json"
        
        if not json_file.exists():
            continue
        
        # Load JSON
        with open(json_file, 'r', encoding='utf-8') as f:
            cover_data = json.load(f)
        
        components = cover_data['slide']['components']
        updated = False
        
        # Update image references
        for component in components:
            if component['type'] == 'image':
                src = component.get('src', '')
                
                # Check if it's the logo (image_1)
                if f'cover_{cover_num:02d}_image_1' in src:
                    # Update to reference shared logo
                    component['src'] = 'logo/pwc_logo.png'
                    updated = True
                    
                    # Delete the duplicate logo file
                    logo_file = images_dir / f"cover_{cover_num:02d}_image_1.png"
                    if logo_file.exists() and cover_num > 1:  # Keep the first one as source
                        logo_file.unlink()
                        total_deleted += 1
                
                # Check if it's a cover photo (image_2) - rename to simpler name
                elif f'cover_{cover_num:02d}_image_2' in src:
                    old_filename = f"cover_{cover_num:02d}_image_2.png"
                    new_filename = f"cover_{cover_num:02d}.png"
                    
                    old_path = images_dir / old_filename
                    new_path = images_dir / new_filename
                    
                    if old_path.exists():
                        shutil.move(str(old_path), str(new_path))
                        component['src'] = f'images/{new_filename}'
                        updated = True
        
        # For cover_02, also handle the JPEG background image
        if cover_num == 2:
            for component in components:
                if component['type'] == 'image':
                    src = component.get('src', '')
                    if 'cover_02_image_1.jpg' in src:
                        # This is the background photo for cover 2
                        old_path = images_dir / 'cover_02_image_1.jpg'
                        new_path = images_dir / 'cover_02_photo.jpg'
                        if old_path.exists():
                            shutil.move(str(old_path), str(new_path))
                            component['src'] = 'images/cover_02_photo.jpg'
                            updated = True
        
        # Save updated JSON
        if updated:
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(cover_data, f, indent=2, ensure_ascii=False)
            total_updated += 1
            print(f"✓ Updated: cover_{cover_num:02d}_title_subtitle.json")
    
    print(f"\n✓ Reorganization complete!")
    print(f"  Logo saved to: {logo_dir}/pwc_logo.png")
    print(f"  Duplicate logos deleted: {total_deleted}")
    print(f"  JSON files updated: {total_updated}")
    print(f"  Cover photos remain in: {images_dir}")

if __name__ == "__main__":
    main()








