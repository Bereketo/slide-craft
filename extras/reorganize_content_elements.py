#!/usr/bin/env python3
"""
Reorganize content elements into separate directories by layout type.
This makes it easier for AI agents to select appropriate templates.
"""

import json
import shutil
from pathlib import Path

def reorganize_content_elements():
    """Reorganize content elements into categorized directories"""
    
    base_dir = Path("/Users/ahmshalan/Projects/mobifly/ppt-generate/branding/content_elements")
    elements_dir = base_dir / "elements"
    
    # Define directory structure based on use cases
    layout_categories = {
        "title_slides": {
            "description": "Title and cover slides for presentations",
            "categories": ["chart"]  # The "chart" category includes title slides
        },
        "section_headers": {
            "description": "Section divider and header slides",
            "categories": ["section_divider"]
        },
        "content_standard": {
            "description": "Standard content layouts with text",
            "categories": ["content", "simple"]
        },
        "content_two_column": {
            "description": "Two-column content layouts",
            "categories": ["two_column"]
        },
        "content_image": {
            "description": "Image-focused content layouts",
            "categories": ["image_layout"]
        },
        "timelines": {
            "description": "Timeline and process flow layouts",
            "categories": ["timeline"]
        },
        "tables": {
            "description": "Table and data grid layouts",
            "categories": ["table"]
        },
        "bullet_lists": {
            "description": "Bullet point and list layouts",
            "categories": ["bullet_list"]
        },
        "title_content": {
            "description": "Title with content layouts",
            "categories": ["title_content"]
        },
        "complex": {
            "description": "Complex multi-element layouts",
            "categories": ["complex"]
        },
        "blank": {
            "description": "Blank or minimal layouts",
            "categories": ["blank"]
        }
    }
    
    # Load index
    with open(base_dir / "index.json", 'r') as f:
        index = json.load(f)
    
    # Create new directory structure
    organized_structure = {}
    
    for layout_type, info in layout_categories.items():
        layout_dir = base_dir / layout_type
        layout_dir.mkdir(exist_ok=True)
        
        organized_structure[layout_type] = {
            "description": info["description"],
            "count": 0,
            "elements": []
        }
    
    # Copy and organize files
    print("Organizing content elements by layout type...\n")
    
    for element in index['elements']:
        category = element['category']
        element_file = element['file']
        source_file = elements_dir / element_file
        
        # Find which layout directory this belongs to
        target_layout = None
        for layout_type, info in layout_categories.items():
            if category in info['categories']:
                target_layout = layout_type
                break
        
        if target_layout:
            # Copy file to appropriate directory
            target_dir = base_dir / target_layout
            target_file = target_dir / element_file
            
            if source_file.exists():
                shutil.copy2(source_file, target_file)
                
                organized_structure[target_layout]["count"] += 1
                organized_structure[target_layout]["elements"].append({
                    "id": element["id"],
                    "file": element_file,
                    "category": category,
                    "description": element["description"]
                })
                
                print(f"✓ {element_file} → {target_layout}/")
    
    # Create index files for each category
    print("\nCreating category index files...\n")
    
    for layout_type, data in organized_structure.items():
        if data["count"] > 0:
            category_index = {
                "layout_type": layout_type,
                "description": data["description"],
                "total_elements": data["count"],
                "elements": data["elements"]
            }
            
            index_file = base_dir / layout_type / "index.json"
            with open(index_file, 'w', encoding='utf-8') as f:
                json.dump(category_index, f, indent=2, ensure_ascii=False)
            
            print(f"✓ Created {layout_type}/index.json ({data['count']} elements)")
    
    # Create master directory index
    master_index = {
        "total_elements": len(index['elements']),
        "layout_types": {}
    }
    
    for layout_type, data in organized_structure.items():
        if data["count"] > 0:
            master_index["layout_types"][layout_type] = {
                "description": data["description"],
                "count": data["count"],
                "index_file": f"{layout_type}/index.json"
            }
    
    master_index_file = base_dir / "layouts_index.json"
    with open(master_index_file, 'w', encoding='utf-8') as f:
        json.dump(master_index, f, indent=2, ensure_ascii=False)
    
    print(f"\n✓ Created master layouts_index.json")
    
    # Print summary
    print("\n" + "="*60)
    print("REORGANIZATION COMPLETE")
    print("="*60)
    print(f"\nTotal elements organized: {len(index['elements'])}")
    print("\nLayout Type Breakdown:")
    print("-" * 60)
    
    for layout_type, data in sorted(organized_structure.items(), key=lambda x: x[1]["count"], reverse=True):
        if data["count"] > 0:
            print(f"  {layout_type:.<30} {data['count']:>3} elements")
    
    print("\n" + "="*60)
    print("Directory structure:")
    print("  content_elements/")
    for layout_type, data in organized_structure.items():
        if data["count"] > 0:
            print(f"    ├── {layout_type}/")
            print(f"    │   ├── index.json")
            print(f"    │   └── element_XX_*.json ({data['count']} files)")
    print("    ├── images/")
    print("    ├── elements/ (original)")
    print("    ├── index.json (original)")
    print("    └── layouts_index.json (master index)")
    print("="*60)

if __name__ == "__main__":
    reorganize_content_elements()




