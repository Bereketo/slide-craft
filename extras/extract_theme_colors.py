#!/usr/bin/env python3
"""
Extract actual theme colors from PowerPoint file
"""

from pptx import Presentation
import zipfile
import xml.etree.ElementTree as ET

def extract_theme_colors(pptx_path):
    """Extract theme colors from PowerPoint file"""
    
    print(f"\n{'='*80}")
    print(f"EXTRACTING THEME COLORS FROM PPTX")
    print(f"{'='*80}\n")
    
    # Open the PPTX as a zip file
    with zipfile.ZipFile(pptx_path, 'r') as zip_file:
        # List all files
        print("Files in PPTX:")
        for name in zip_file.namelist():
            if 'theme' in name.lower():
                print(f"  {name}")
        
        print("\n" + "="*80)
        
        # Try to read theme file
        theme_files = [name for name in zip_file.namelist() if 'theme' in name.lower() and name.endswith('.xml')]
        
        if theme_files:
            theme_file = theme_files[0]
            print(f"\nReading theme file: {theme_file}\n")
            
            with zip_file.open(theme_file) as f:
                content = f.read()
                root = ET.fromstring(content)
                
                # Find color scheme
                ns = {
                    'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
                    'p': 'http://schemas.openxmlformats.org/presentationml/2006/main'
                }
                
                # Find clrScheme
                clrScheme = root.find('.//a:clrScheme', ns)
                
                if clrScheme:
                    print("Color Scheme Found:")
                    print("-" * 80)
                    
                    color_map = {}
                    
                    for color_elem in clrScheme:
                        color_name = color_elem.tag.split('}')[-1]  # Get tag name without namespace
                        
                        # Look for srgbClr
                        srgb = color_elem.find('.//a:srgbClr', ns)
                        if srgb is not None:
                            val = srgb.get('val')
                            color_map[color_name] = f"#{val}"
                            print(f"  {color_name:15s} = #{val}")
                        
                        # Look for sysClr
                        sys = color_elem.find('.//a:sysClr', ns)
                        if sys is not None:
                            val = sys.get('lastClr')
                            if val:
                                color_map[color_name] = f"#{val}"
                                print(f"  {color_name:15s} = #{val} (system)")
                    
                    print("\n" + "="*80)
                    print("PYTHON MAPPING FOR SCHEME_COLORS:")
                    print("="*80)
                    print("SCHEME_COLORS = {")
                    for name, color in color_map.items():
                        print(f'    "{name}": "{color}",')
                    print("}")
                    
                else:
                    print("No color scheme found in theme")
        else:
            print("No theme files found")

if __name__ == "__main__":
    pptx_path = "branding/PwC_ppt_graphic_elements_level1.pptx"
    extract_theme_colors(pptx_path)




