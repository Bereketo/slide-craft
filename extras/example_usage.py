#!/usr/bin/env python3
"""
Example usage of the auto-alignment system with your PowerPoint generator.
"""

from ppt_auto_align_integration import fix_overlapping_components, analyze_overlaps, create_auto_aligned_presentation


def main():
    """Demonstrate how to use the auto-alignment system."""
    
    print("🎯 PowerPoint Auto-Alignment Example Usage\n")
    
    # Example 1: Analyze your existing JSON for overlaps
    print("1️⃣ Analyzing your existing presentation for overlaps...")
    try:
        analysis = analyze_overlaps("ppt-json-sample.json")
        print(f"   📊 Analysis Results:")
        print(f"   - Total slides: {len(analysis['slides'])}")
        print(f"   - Total overlaps: {analysis['total_overlaps']}")
        print(f"   - Total components: {analysis['total_components']}")
        
        if analysis['total_overlaps'] > 0:
            print(f"   ⚠️  Found overlaps in the following slides:")
            for slide in analysis['slides']:
                if slide['overlaps_count'] > 0:
                    print(f"      - {slide['slide_title']}: {slide['overlaps_count']} overlaps")
        else:
            print(f"   ✅ No overlaps found - your presentation is already well-aligned!")
            
    except FileNotFoundError:
        print("   ❌ ppt-json-sample.json not found")
    
    print()
    
    # Example 2: Fix overlapping components (even if none exist, this shows the process)
    print("2️⃣ Fixing overlapping components...")
    try:
        fixed_data = fix_overlapping_components(
            "ppt-json-sample.json", 
            "ppt-json-sample-fixed.json",
            strategy="preserve_order"
        )
        print("   ✅ Components processed and saved to ppt-json-sample-fixed.json")
        
        # Show validation results
        validation = fixed_data["slides"][0].get("_alignment_validation", {})
        if validation:
            print(f"   📊 Validation: {validation['overlaps_detected']} overlaps, height: {validation['total_height']:.1f}px")
            
    except FileNotFoundError:
        print("   ❌ ppt-json-sample.json not found")
    
    print()
    
    # Example 3: Complete workflow - fix JSON and generate PowerPoint
    print("3️⃣ Complete workflow: Fix JSON + Generate PowerPoint...")
    try:
        success = create_auto_aligned_presentation(
            "ppt-json-sample.json",
            "ppt-json-sample-auto-fixed.json", 
            "presentation-auto-aligned.pptx",
            strategy="preserve_order"
        )
        
        if success:
            print("   ✅ Complete workflow successful!")
            print("   📁 Files created:")
            print("      - ppt-json-sample-auto-fixed.json (fixed JSON)")
            print("      - presentation-auto-aligned.pptx (PowerPoint)")
        else:
            print("   ❌ Workflow failed - check error messages above")
            
    except FileNotFoundError:
        print("   ❌ Required files not found")
    
    print()
    
    # Example 4: Show how to use with your own data
    print("4️⃣ How to use with your own data:")
    print("""
   # Method 1: Simple fix
   from ppt_auto_align_integration import fix_overlapping_components
   fixed_data = fix_overlapping_components('your_file.json', 'fixed_file.json')
   
   # Method 2: Complete workflow
   from ppt_auto_align_integration import create_auto_aligned_presentation
   create_auto_aligned_presentation('input.json', 'fixed.json', 'output.pptx')
   
   # Method 3: Analyze first
   from ppt_auto_align_integration import analyze_overlaps
   analysis = analyze_overlaps('your_file.json')
   print(f"Found {analysis['total_overlaps']} overlaps")
   """)


if __name__ == "__main__":
    main()
