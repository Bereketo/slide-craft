#!/usr/bin/env python3
"""
Test the extraction on slide 2 specifically to verify font properties
"""

import json
import sys
from pathlib import Path
from pptx import Presentation

# Add the parent directory to the path
sys.path.insert(0, str(Path(__file__).parent))

# Import the functions from extract_content_elements
exec(open('extract_content_elements.py').read())

def test_slide_2():
    elements_file = Path("/Users/ahmshalan/Projects/mobifly/ppt-generate/branding/PwC_ppt_graphic_elements_level1.pptx")
    
    print("Loading presentation...")
    prs = Presentation(str(elements_file))
    
    # Get slide 2 (index 1)
    slide = prs.slides[1]
    
    print("\nExtracting slide 2...")
    element_json = extract_slide_to_json(slide, 2)
    
    print("\n=== EXTRACTED JSON ===")
    print(json.dumps(element_json, indent=2))
    
    print("\n=== TEXT COMPONENTS ===")
    for idx, comp in enumerate(element_json['slide']['components']):
        if comp['type'] == 'richtext':
            print(f"\nComponent {idx}:")
            for run in comp['runs']:
                print(f"  Text: '{run['text']}'")
                print(f"  Font Size: {run.get('font_size', 'NOT SET')}")
                print(f"  Font Family: {run.get('font_family', 'NOT SET')}")
                print(f"  Color: {run.get('color', 'NOT SET')}")
                print(f"  Bold: {run.get('bold', 'NOT SET')}")

if __name__ == "__main__":
    test_slide_2()




