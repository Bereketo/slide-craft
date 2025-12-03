#!/usr/bin/env python3
"""
Check both theme files
"""

from pptx import Presentation
import zipfile
import xml.etree.ElementTree as ET

def extract_all_themes(pptx_path):
    """Extract colors from all theme files"""
    
    with zipfile.ZipFile(pptx_path, 'r') as zip_file:
        theme_files = [name for name in zip_file.namelist() if 'theme' in name.lower() and name.endswith('.xml')]
        
        for theme_file in theme_files:
            print(f"\n{'='*80}")
            print(f"THEME: {theme_file}")
            print(f"{'='*80}\n")
            
            with zip_file.open(theme_file) as f:
                content = f.read()
                root = ET.fromstring(content)
                
                ns = {'a': 'http://schemas.openxmlformats.org/drawingml/2006/main'}
                
                clrScheme = root.find('.//a:clrScheme', ns)
                
                if clrScheme:
                    for color_elem in clrScheme:
                        color_name = color_elem.tag.split('}')[-1]
                        
                        srgb = color_elem.find('.//a:srgbClr', ns)
                        if srgb is not None:
                            val = srgb.get('val')
                            print(f"  {color_name:15s} = #{val}")
                        
                        sys = color_elem.find('.//a:sysClr', ns)
                        if sys is not None:
                            val = sys.get('lastClr')
                            if val:
                                print(f"  {color_name:15s} = #{val} (system)")

if __name__ == "__main__":
    pptx_path = "branding/PwC_ppt_graphic_elements_level1.pptx"
    extract_all_themes(pptx_path)




