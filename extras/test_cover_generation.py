#!/usr/bin/env python3
"""
Test script to verify cover generation works correctly.
"""

import json
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.ppt import (
    load_covers_index,
    select_best_cover,
    load_and_customize_cover,
    extract_presentation_info
)

def test_cover_generation():
    """Test the complete cover generation flow."""
    
    print("="*60)
    print("Testing Cover Generation")
    print("="*60)
    
    # Test 1: Load covers index
    print("\n1. Loading covers index...")
    covers_index = load_covers_index()
    if covers_index:
        print(f"   ✓ Loaded {len(covers_index['covers'])} covers")
    else:
        print("   ✗ Failed to load covers index")
        return
    
    # Test 2: Extract presentation info
    test_input = "Create a financial analysis presentation for Q4 earnings"
    print(f"\n2. Extracting info from: '{test_input}'")
    pres_info = extract_presentation_info(test_input)
    print(f"   Title: {pres_info.get('presentation_title')}")
    print(f"   Use Case: {pres_info.get('use_case')[:60]}...")
    print(f"   Author: {pres_info.get('author')}")
    
    # Test 3: Select best cover
    print(f"\n3. Selecting best cover...")
    selected_cover = select_best_cover(pres_info['use_case'], covers_index)
    if selected_cover:
        print(f"   ✓ Selected Cover {selected_cover['id']}")
        print(f"   Description: {selected_cover['description'][:80]}...")
    else:
        print("   ✗ Failed to select cover")
        return
    
    # Test 4: Load and customize cover
    print(f"\n4. Loading and customizing cover...")
    cover_slide = load_and_customize_cover(
        selected_cover,
        pres_info['presentation_title'],
        pres_info.get('author')
    )
    
    if cover_slide:
        print(f"   ✓ Cover slide created")
        print(f"   Components: {len(cover_slide['components'])}")
        
        # Check for background image
        for idx, component in enumerate(cover_slide['components']):
            if component['type'] == 'image':
                print(f"   Image {idx}: {component['src']}")
                if 'box' in component:
                    box = component['box']
                    print(f"     Size: {box['w']}x{box['h']} at ({box['x']}, {box['y']})")
                    if box['w'] == 1280 and box['h'] == 720:
                        print(f"     ✓ Full-slide background image detected!")
        
        # Save to file for inspection
        output_file = Path("test_cover_output.json")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({"slide": cover_slide}, f, indent=2)
        print(f"\n   Saved test output to: {output_file}")
        
    else:
        print("   ✗ Failed to create cover slide")
        return
    
    print("\n" + "="*60)
    print("✓ All tests passed!")
    print("="*60)

if __name__ == "__main__":
    test_cover_generation()






