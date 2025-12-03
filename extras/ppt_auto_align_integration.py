#!/usr/bin/env python3
"""
PowerPoint Auto-Alignment Integration
Easy-to-use functions for integrating auto-alignment with the PowerPoint generator.
"""

import json
from typing import Dict, Any, List
from grid_auto_align import auto_align_presentation, auto_align_slide_components


def fix_overlapping_components(json_file_path: str, output_file_path: str = None, 
                             strategy: str = "preserve_order") -> Dict[str, Any]:
    """
    Fix overlapping components in a PowerPoint JSON file.
    
    Args:
        json_file_path: Path to the input JSON file
        output_file_path: Path to save the fixed JSON (optional)
        strategy: Alignment strategy ("preserve_order", "compact", "balanced")
    
    Returns:
        Fixed presentation data
    """
    # Load the JSON data
    with open(json_file_path, 'r', encoding='utf-8') as f:
        presentation_data = json.load(f)
    
    # Apply auto-alignment
    fixed_data = auto_align_presentation(presentation_data, strategy)
    
    # Save the fixed data if output path provided
    if output_file_path:
        with open(output_file_path, 'w', encoding='utf-8') as f:
            json.dump(fixed_data, f, indent=2, ensure_ascii=False)
        print(f"Fixed presentation saved to: {output_file_path}")
    
    return fixed_data


def fix_single_slide_components(slide_data: Dict[str, Any], tokens: Dict[str, Any],
                               strategy: str = "preserve_order") -> Dict[str, Any]:
    """
    Fix overlapping components in a single slide.
    
    Args:
        slide_data: Single slide data
        tokens: Design tokens from the presentation
        strategy: Alignment strategy
    
    Returns:
        Fixed slide data
    """
    return auto_align_slide_components(slide_data, tokens, strategy)


def analyze_overlaps(json_file_path: str) -> Dict[str, Any]:
    """
    Analyze overlaps in a PowerPoint JSON file without fixing them.
    
    Args:
        json_file_path: Path to the JSON file
    
    Returns:
        Analysis results
    """
    from grid_auto_align import GridAutoAligner
    
    with open(json_file_path, 'r', encoding='utf-8') as f:
        presentation_data = json.load(f)
    
    tokens = presentation_data["tokens"]
    aligner = GridAutoAligner(tokens)
    
    analysis = {
        "slides": [],
        "total_overlaps": 0,
        "total_components": 0
    }
    
    for i, slide in enumerate(presentation_data["slides"]):
        if "components" not in slide:
            continue
            
        rects = aligner.extract_grid_rects(slide["components"])
        overlaps = aligner.detect_overlaps(rects)
        validation = aligner.validate_alignment(slide["components"])
        
        slide_analysis = {
            "slide_index": i,
            "slide_title": slide.get("title", f"Slide {i+1}"),
            "components_count": len(rects),
            "overlaps_count": len(overlaps),
            "overlapping_components": [(r1.component_id, r2.component_id) for r1, r2 in overlaps],
            "total_height": validation["total_height"],
            "column_usage": validation["column_usage"]
        }
        
        analysis["slides"].append(slide_analysis)
        analysis["total_overlaps"] += len(overlaps)
        analysis["total_components"] += len(rects)
    
    return analysis


def create_auto_aligned_presentation(input_json: str, output_json: str, 
                                   output_pptx: str, strategy: str = "preserve_order"):
    """
    Complete workflow: fix JSON and generate PowerPoint.
    
    Args:
        input_json: Input JSON file path
        output_json: Fixed JSON output path
        output_pptx: PowerPoint output path
        strategy: Alignment strategy
    """
    import subprocess
    import sys
    from pathlib import Path
    
    # Step 1: Fix overlapping components
    print("🔧 Fixing overlapping components...")
    fixed_data = fix_overlapping_components(input_json, output_json, strategy)
    
    # Step 2: Generate PowerPoint
    print("📊 Generating PowerPoint presentation...")
    
    # Find schema file (assume it's in the same directory)
    input_path = Path(input_json)
    schema_path = input_path.parent / "ppt-json-schema.json"
    
    if not schema_path.exists():
        print(f"❌ Schema file not found: {schema_path}")
        return False
    
    # Run the PowerPoint generator
    try:
        cmd = [
            sys.executable, "ppt-generator.py",
            "--schema", str(schema_path),
            "--input", output_json,
            "--out", output_pptx
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=input_path.parent)
        
        if result.returncode == 0:
            print(f"✅ PowerPoint generated successfully: {output_pptx}")
            return True
        else:
            print(f"❌ PowerPoint generation failed:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Error generating PowerPoint: {e}")
        return False


# Example usage functions
def example_usage():
    """Show example usage of the auto-alignment functions."""
    
    print("=== PowerPoint Auto-Alignment Examples ===\n")
    
    # Example 1: Analyze overlaps
    print("1. Analyzing overlaps in a presentation:")
    try:
        analysis = analyze_overlaps("ppt-json-sample.json")
        print(f"   Total slides: {len(analysis['slides'])}")
        print(f"   Total overlaps: {analysis['total_overlaps']}")
        print(f"   Total components: {analysis['total_components']}")
        
        for slide in analysis['slides']:
            if slide['overlaps_count'] > 0:
                print(f"   📍 {slide['slide_title']}: {slide['overlaps_count']} overlaps")
    except FileNotFoundError:
        print("   (Example file not found)")
    
    print()
    
    # Example 2: Fix overlapping components
    print("2. Fixing overlapping components:")
    try:
        fixed_data = fix_overlapping_components(
            "ppt-json-sample.json", 
            "ppt-json-sample-fixed.json",
            strategy="preserve_order"
        )
        print("   ✅ Components fixed and saved to ppt-json-sample-fixed.json")
    except FileNotFoundError:
        print("   (Example file not found)")
    
    print()
    
    # Example 3: Complete workflow
    print("3. Complete workflow (fix + generate PowerPoint):")
    print("   create_auto_aligned_presentation(")
    print("       'input.json', 'fixed.json', 'output.pptx', 'preserve_order'")
    print("   )")


if __name__ == "__main__":
    example_usage()
