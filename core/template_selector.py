"""
PwC Template Selector
Helps AI agents select appropriate templates based on slide content
"""

import json
import random
from pathlib import Path
from typing import Dict, List, Optional, Tuple

class PwCTemplateSelector:
    """
    AI Agent helper for selecting appropriate PwC presentation templates
    """
    
    def __init__(self, base_path: str = "branding"):
        self.base_path = Path(base_path)
        self.content_elements_path = self.base_path / "content_elements"
        self.covers_path = self.base_path / "covers"
        self.load_indexes()
    
    def load_indexes(self):
        """Load all template indexes"""
        # Load content elements index
        layouts_index_file = self.content_elements_path / "layouts_index.json"
        if layouts_index_file.exists():
            with open(layouts_index_file, 'r') as f:
                self.layouts = json.load(f)
        else:
            self.layouts = {"layout_types": {}}
        
        # Load covers index
        covers_index_file = self.covers_path / "index.json"
        if covers_index_file.exists():
            with open(covers_index_file, 'r') as f:
                self.covers = json.load(f)
        else:
            self.covers = {"covers": []}
    
    def select_cover_template(self, title: str = "", description: str = "") -> Dict:
        """
        Select an appropriate cover page template
        
        Args:
            title: Presentation title
            description: Brief description to match mood/theme
        
        Returns:
            Dictionary with cover template information
        """
        if not self.covers.get("covers"):
            return None
        
        # For now, select randomly - can be enhanced with semantic matching
        cover = random.choice(self.covers["covers"])
        
        # Load the cover template
        cover_file = self.covers_path / "subtitles" / cover["file"]
        if cover_file.exists():
            with open(cover_file, 'r') as f:
                template = json.load(f)
            
            return {
                "id": cover["id"],
                "file": cover["file"],
                "image": cover["image"],
                "category": cover["category"],
                "description": cover["description"],
                "template": template
            }
        
        return None
    
    def select_content_template(
        self, 
        slide_position: int, 
        content_description: str, 
        content_keywords: Optional[List[str]] = None,
        total_slides: int = 5,
        is_topic_transition: bool = False
    ) -> Dict:
        """
        Select the most appropriate content template based on slide content
        
        Args:
            slide_position: Position in presentation (0-based)
            content_description: Description of slide content
            content_keywords: Optional list of keywords
            total_slides: Total number of slides in presentation
            is_topic_transition: True if this slide is a transition between major topics
        
        Returns:
            Dictionary with template information
        """
        
        # First slide = title slide
        if slide_position == 0:
            return self._get_template_from("title_slides")
        
        # Check for topic separator/transition
        if is_topic_transition or any(k in content_description.lower() for k in ["topic separator", "topic transition", "new topic"]):
            return self._get_template_from("topic_separators")
        
        # Last slide could be conclusion or summary
        if slide_position == total_slides - 1:
            # Could use title_slides or content_standard
            if any(k in content_description.lower() for k in ["conclusion", "summary", "thank", "contact"]):
                return self._get_template_from("title_slides")
        
        # Convert to lowercase for matching
        desc_lower = content_description.lower()
        keywords_str = " ".join(content_keywords) if content_keywords else ""
        search_text = f"{desc_lower} {keywords_str}".lower()
        
        # Priority matching based on content type
        if any(k in search_text for k in ["section", "chapter", "divider", "break"]):
            return self._get_template_from("section_headers")
        
        if any(k in search_text for k in ["timeline", "roadmap", "process", "step", "flow", "sequence"]):
            return self._get_template_from("timelines")
        
        if any(k in search_text for k in ["table", "data", "grid", "spreadsheet", "comparison"]):
            return self._get_template_from("tables")
        
        if any(k in search_text for k in ["image", "photo", "picture", "visual", "gallery"]):
            return self._get_template_from("content_image")
        
        if any(k in search_text for k in ["two column", "split", "versus", "vs", "compare", "side by side"]):
            return self._get_template_from("content_two_column")
        
        if any(k in search_text for k in ["bullet", "list", "point", "key points"]):
            return self._get_template_from("bullet_lists")
        
        if any(k in search_text for k in ["complex", "mixed", "multiple", "rich", "detailed"]):
            return self._get_template_from("complex")
        
        # Default to standard content
        return self._get_template_from("content_standard")
    
    def _get_template_from(self, layout_type: str) -> Dict:
        """
        Get a random template from specified layout type
        
        Args:
            layout_type: Type of layout (e.g., "title_slides", "tables")
        
        Returns:
            Dictionary with template information
        """
        layout_dir = self.content_elements_path / layout_type
        index_file = layout_dir / "index.json"
        
        if not index_file.exists():
            return {
                "layout_type": layout_type,
                "error": "Layout type not found",
                "template": None
            }
        
        with open(index_file, 'r') as f:
            index = json.load(f)
        
        if not index.get("elements"):
            return {
                "layout_type": layout_type,
                "error": "No elements in layout",
                "template": None
            }
        
        # Pick random element from this layout type
        element = random.choice(index['elements'])
        template_file = layout_dir / element['file']
        
        if template_file.exists():
            with open(template_file, 'r') as f:
                template = json.load(f)
            
            return {
                "layout_type": layout_type,
                "element_id": element['id'],
                "file": element['file'],
                "category": element['category'],
                "description": element['description'],
                "template": template
            }
        
        return {
            "layout_type": layout_type,
            "error": "Template file not found",
            "template": None
        }
    
    def get_topic_separator_template(self) -> Dict:
        """
        Get a topic separator template specifically
        
        Returns:
            Dictionary with topic separator template information
        """
        return self._get_template_from("topic_separators")
    
    def get_layout_suggestions(self, content_description: str) -> List[Tuple[str, float]]:
        """
        Get ranked layout suggestions based on content description
        
        Args:
            content_description: Description of the content
        
        Returns:
            List of (layout_type, confidence_score) tuples, sorted by confidence
        """
        desc_lower = content_description.lower()
        suggestions = []
        
        # Scoring based on keyword matches
        keyword_map = {
            "title_slides": ["title", "cover", "introduction", "welcome"],
            "section_headers": ["section", "chapter", "divider", "break"],
            "topic_separators": ["topic transition", "new topic", "topic separator", "topic divider"],
            "timelines": ["timeline", "roadmap", "process", "steps", "flow"],
            "tables": ["table", "data", "grid", "comparison"],
            "content_image": ["image", "photo", "visual"],
            "content_two_column": ["two column", "split", "versus"],
            "bullet_lists": ["bullet", "list", "points"],
            "content_standard": ["text", "content", "information"],
        }
        
        for layout_type, keywords in keyword_map.items():
            matches = sum(1 for k in keywords if k in desc_lower)
            if matches > 0:
                confidence = min(matches / len(keywords), 1.0)
                suggestions.append((layout_type, confidence))
        
        # Sort by confidence score (highest first)
        suggestions.sort(key=lambda x: x[1], reverse=True)
        
        return suggestions
    
    def get_all_layout_types(self) -> Dict:
        """Get all available layout types with counts"""
        return self.layouts.get("layout_types", {})
    
    def get_template_info(self, layout_type: str) -> Optional[Dict]:
        """Get information about a specific layout type"""
        return self.layouts.get("layout_types", {}).get(layout_type)


# Convenience function for quick access
def select_template(slide_position: int, content_description: str, content_keywords: List[str] = None) -> Dict:
    """
    Quick function to select appropriate template
    
    Args:
        slide_position: Slide number (0-based)
        content_description: What the slide is about
        content_keywords: Optional keywords
    
    Returns:
        Template information dictionary
    """
    selector = PwCTemplateSelector()
    return selector.select_content_template(slide_position, content_description, content_keywords)



