"""
Template Provider for LLM
Provides template structure examples to the LLM for proper layout generation
"""

import json
import random
from pathlib import Path
from typing import Dict, List, Optional


class TemplateProvider:
    """
    Provides template structure examples to guide LLM generation
    """
    
    def __init__(self, base_path: str = "branding/content_elements"):
        self.base_path = Path(base_path)
        self.templates_cache = {}
    
    def get_template_examples(self) -> Dict[str, str]:
        """
        Get example template structures for each category to guide LLM
        
        Returns:
            Dictionary mapping category names to example template JSON strings
        """
        examples = {}
        
        # Get one example from each major category
        categories = {
            "title_slides": "Title/Introduction Slides",
            "content_standard": "Standard Content Slides",
            "tables": "Data Table Slides",
            "timelines": "Timeline/Process Slides",
            "content_two_column": "Two-Column Comparison Slides"
        }
        
        for category, description in categories.items():
            template = self._load_random_template(category)
            if template:
                # Simplify the template for the LLM (remove some complexity)
                simplified = self._simplify_template(template)
                examples[category] = {
                    "description": description,
                    "structure": simplified
                }
        
        return examples
    
    def _load_random_template(self, category: str) -> Optional[Dict]:
        """Load a random template from a category"""
        try:
            category_dir = self.base_path / category
            index_file = category_dir / "index.json"
            
            if not index_file.exists():
                return None
            
            with open(index_file, 'r') as f:
                index = json.load(f)
            
            if not index.get("elements"):
                return None
            
            # Pick the first element (or random)
            element = index['elements'][0]
            template_file = category_dir / element['file']
            
            if template_file.exists():
                with open(template_file, 'r') as f:
                    return json.load(f)
        
        except Exception as e:
            print(f"Error loading template from {category}: {e}")
        
        return None
    
    def _simplify_template(self, template: Dict) -> Dict:
        """
        Simplify template for LLM guidance (keep structure, remove some details)
        """
        if not template or 'slide' not in template:
            return {}
        
        slide = template['slide']
        
        # Keep only essential structure
        simplified = {
            "background": slide.get("background", {}),
            "components": []
        }
        
        # Simplify components
        for comp in slide.get("components", []):
            simplified_comp = {
                "type": comp.get("type"),
            }
            
            # Keep layout info
            if "grid" in comp:
                simplified_comp["grid"] = comp["grid"]
            elif "box" in comp:
                simplified_comp["box"] = comp["box"]
            
            # Keep style essentials
            if "style" in comp:
                style = comp["style"]
                simplified_comp["style"] = {
                    "font_family": style.get("font_family"),
                    "font_size": style.get("font_size"),
                    "bold": style.get("bold"),
                    "color": style.get("color"),
                    "fill": style.get("fill"),
                    "align": style.get("align")
                }
            
            # Keep text_type if present
            if "text_type" in comp:
                simplified_comp["text_type"] = comp["text_type"]
            
            # Add placeholder for content
            if comp.get("type") in ["text", "richtext"]:
                simplified_comp["content"] = "[Your content here]"
            elif comp.get("type") == "image":
                simplified_comp["content"] = "[Image URL here]"
            
            simplified["components"].append(simplified_comp)
        
        return simplified
    
    def format_examples_for_prompt(self) -> str:
        """
        Format template examples as a string for inclusion in LLM prompt
        
        Returns:
            Formatted string with template examples
        """
        examples = self.get_template_examples()
        
        if not examples:
            return "No templates available."
        
        output = []
        output.append("=" * 80)
        output.append(" TEMPLATE STRUCTURE EXAMPLES")
        output.append("=" * 80)
        output.append("")
        output.append("Follow these PwC-branded layout patterns when generating slides:")
        output.append("")
        
        for category, data in examples.items():
            output.append(f"\n{data['description'].upper()} ({category})")
            output.append("-" * 80)
            output.append("Structure pattern:")
            output.append(json.dumps(data['structure'], indent=2))
            output.append("")
        
        output.append("=" * 80)
        output.append("IMPORTANT: Match these exact layout patterns, styles, and positioning.")
        output.append("Replace placeholder content with your generated content.")
        output.append("=" * 80)
        
        return "\n".join(output)


def get_template_guidance() -> str:
    """
    Convenience function to get template guidance for LLM prompt
    
    Returns:
        Formatted template examples string
    """
    provider = TemplateProvider()
    return provider.format_examples_for_prompt()




