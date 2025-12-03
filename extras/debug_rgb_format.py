#!/usr/bin/env python3
"""
Debug RGB color format
"""

from pptx import Presentation

def debug_rgb(pptx_path, slide_num):
    """Debug RGB format"""
    prs = Presentation(pptx_path)
    slide = prs.slides[slide_num]
    layout = slide.slide_layout
    layout_fill = layout.background.fill
    
    rgb = layout_fill.fore_color.rgb
    
    print(f"RGB Type: {type(rgb)}")
    print(f"RGB Value: {rgb}")
    print(f"RGB repr: {repr(rgb)}")
    
    # Try different ways to convert
    print("\nTrying different conversions:")
    
    # Method 1: Direct attributes
    try:
        print(f"  Method 1 (r,g,b attrs): #{rgb.r:02X}{rgb.g:02X}{rgb.b:02X}")
    except Exception as e:
        print(f"  Method 1 failed: {e}")
    
    # Method 2: Indexing
    try:
        print(f"  Method 2 (indexing): #{rgb[0]:02X}{rgb[1]:02X}{rgb[2]:02X}")
    except Exception as e:
        print(f"  Method 2 failed: {e}")
    
    # Method 3: Direct string
    try:
        print(f"  Method 3 (str): {str(rgb)}")
    except Exception as e:
        print(f"  Method 3 failed: {e}")
    
    # Method 4: Check if it has __int__
    try:
        val = int(rgb)
        print(f"  Method 4 (int): {val:06X}")
    except Exception as e:
        print(f"  Method 4 failed: {e}")

if __name__ == "__main__":
    pptx_path = "branding/PwC_ppt_graphic_elements_level1.pptx"
    slide_num = 1
    debug_rgb(pptx_path, slide_num)




