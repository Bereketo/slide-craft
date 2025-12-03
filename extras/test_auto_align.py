#!/usr/bin/env python3
"""
Test the auto-alignment functionality with sample data.
"""

import json
from grid_auto_align import auto_align_presentation, GridAutoAligner


def create_test_data_with_overlaps():
    """Create test data with intentionally overlapping components."""
    return {
        "deck": {
            "title": "Test Presentation",
            "slide_size": "16x9"
        },
        "tokens": {
            "grid": {"columns": 12, "unit": "px"},
            "spacing": {"margin": 48, "gutter": 12},
            "color": {"text": "#000000"},
            "font": {"body_family": "Arial", "title_family": "Arial"}
        },
        "slides": [
            {
                "title": "Overlapping Components Test",
                "components": [
                    {
                        "type": "text",
                        "text_type": "h2",
                        "value": "Title 1",
                        "grid": {"col": 1, "span": 6, "row_h": 60, "y": 100}
                    },
                    {
                        "type": "text",
                        "text_type": "body", 
                        "value": "This overlaps with Title 1",
                        "grid": {"col": 4, "span": 6, "row_h": 100, "y": 100}  # Overlaps!
                    },
                    {
                        "type": "text",
                        "text_type": "body",
                        "value": "This also overlaps",
                        "grid": {"col": 1, "span": 4, "row_h": 80, "y": 120}  # Overlaps!
                    },
                    {
                        "type": "table",
                        "grid": {"col": 1, "span": 12, "row_h": 200, "y": 200}
                    },
                    {
                        "type": "text",
                        "text_type": "body",
                        "value": "This should be placed after the table",
                        "grid": {"col": 1, "span": 6, "row_h": 60, "y": 200}  # Overlaps with table!
                    }
                ]
            }
        ]
    }


def test_auto_alignment():
    """Test the auto-alignment functionality."""
    print("🧪 Testing Auto-Alignment System\n")
    
    # Create test data with overlaps
    test_data = create_test_data_with_overlaps()
    
    print("📋 Original Components (with overlaps):")
    for i, comp in enumerate(test_data["slides"][0]["components"]):
        if "grid" in comp:
            grid = comp["grid"]
            print(f"   {i+1}. {comp['type']} - col:{grid['col']}, span:{grid['span']}, y:{grid['y']}, h:{grid['row_h']}")
    
    print("\n🔍 Analyzing overlaps...")
    aligner = GridAutoAligner(test_data["tokens"])
    rects = aligner.extract_grid_rects(test_data["slides"][0]["components"])
    overlaps = aligner.detect_overlaps(rects)
    
    print(f"   Found {len(overlaps)} overlapping pairs:")
    for r1, r2 in overlaps:
        print(f"   - {r1.component_id} overlaps with {r2.component_id}")
    
    print("\n🔧 Applying auto-alignment (preserve_order strategy)...")
    fixed_data = auto_align_presentation(test_data, strategy="preserve_order")
    
    print("\n✅ Fixed Components:")
    for i, comp in enumerate(fixed_data["slides"][0]["components"]):
        if "grid" in comp:
            grid = comp["grid"]
            print(f"   {i+1}. {comp['type']} - col:{grid['col']}, span:{grid['span']}, y:{grid['y']}, h:{grid['row_h']}")
    
    # Validate the result
    validation = fixed_data["slides"][0]["_alignment_validation"]
    print(f"\n📊 Validation Results:")
    print(f"   Overlaps detected: {validation['overlaps_detected']}")
    print(f"   Total height: {validation['total_height']:.1f}px")
    print(f"   Is valid: {validation['is_valid']}")
    print(f"   Column usage: {validation['column_usage']}")
    
    # Test different strategies
    print("\n🔄 Testing different strategies...")
    
    strategies = ["preserve_order", "compact", "balanced"]
    for strategy in strategies:
        print(f"\n   Strategy: {strategy}")
        strategy_data = auto_align_presentation(test_data, strategy=strategy)
        strategy_validation = strategy_data["slides"][0]["_alignment_validation"]
        print(f"   - Total height: {strategy_validation['total_height']:.1f}px")
        print(f"   - Overlaps: {strategy_validation['overlaps_detected']}")
    
    return fixed_data


def test_with_real_data():
    """Test with the actual sample data."""
    print("\n" + "="*50)
    print("🧪 Testing with Real Sample Data\n")
    
    try:
        with open("ppt-json-sample.json", "r", encoding="utf-8") as f:
            real_data = json.load(f)
        
        print("📋 Original sample data loaded")
        
        # Analyze overlaps in original data
        aligner = GridAutoAligner(real_data["tokens"])
        total_overlaps = 0
        
        for i, slide in enumerate(real_data["slides"]):
            if "components" not in slide:
                continue
            rects = aligner.extract_grid_rects(slide["components"])
            overlaps = aligner.detect_overlaps(rects)
            if overlaps:
                print(f"   Slide {i+1} ({slide.get('title', 'Untitled')}): {len(overlaps)} overlaps")
                total_overlaps += len(overlaps)
        
        if total_overlaps == 0:
            print("   ✅ No overlaps found in original data")
        else:
            print(f"   ⚠️  Total overlaps found: {total_overlaps}")
            
            # Fix the overlaps
            print("\n🔧 Fixing overlaps...")
            fixed_data = auto_align_presentation(real_data, strategy="preserve_order")
            
            # Save the fixed data
            with open("ppt-json-sample-auto-aligned.json", "w", encoding="utf-8") as f:
                json.dump(fixed_data, f, indent=2, ensure_ascii=False)
            
            print("   ✅ Fixed data saved to ppt-json-sample-auto-aligned.json")
            
    except FileNotFoundError:
        print("   ❌ ppt-json-sample.json not found")


if __name__ == "__main__":
    # Run tests
    test_auto_alignment()
    test_with_real_data()
    
    print("\n" + "="*50)
    print("🎉 Auto-alignment testing complete!")
    print("\nTo use with your own data:")
    print("1. from ppt_auto_align_integration import fix_overlapping_components")
    print("2. fixed_data = fix_overlapping_components('your_file.json', 'fixed_file.json')")
    print("3. python ppt-generator.py --schema schema.json --input fixed_file.json --out output.pptx")
