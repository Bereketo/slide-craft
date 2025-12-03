# PwC Content Elements Library

A comprehensive, organized collection of **95 PwC-branded slide templates** extracted from official PwC presentation templates, with accurate font properties, colors, and layouts.

## 📁 Directory Structure

```
content_elements/
├── layouts_index.json          # Master index of all layout types
├── images/                     # All extracted images (287 files)
│
├── title_slides/               # 25 title and cover slides
│   ├── index.json
│   └── element_*.json
│
├── section_headers/            # 2 section divider slides
│   ├── index.json
│   └── element_*.json
│
├── content_standard/           # 15 standard content layouts
│   ├── index.json
│   └── element_*.json
│
├── content_two_column/         # 4 two-column layouts
│   ├── index.json
│   └── element_*.json
│
├── content_image/              # 3 image-focused layouts
│   ├── index.json
│   └── element_*.json
│
├── timelines/                  # 14 timeline/process flows
│   ├── index.json
│   └── element_*.json
│
├── tables/                     # 14 table/data layouts
│   ├── index.json
│   └── element_*.json
│
├── bullet_lists/               # 1 bullet list layout
│   ├── index.json
│   └── element_*.json
│
├── title_content/              # 1 title+content layout
│   ├── index.json
│   └── element_*.json
│
├── complex/                    # 13 complex layouts
│   ├── index.json
│   └── element_*.json
│
└── blank/                      # 3 blank/minimal layouts
    ├── index.json
    └── element_*.json
```

## 🎯 Layout Types for AI Agent Selection

### 1. **Title Slides** (25 templates)
**Use when:** Starting a presentation, introducing main topics, or creating cover slides
- Large prominent numbers
- Orange accent colors (#D04A02)
- Minimalist design
- **Font sizes:** 350pt (numbers), 48pt (titles)

**Example files:** `title_slides/element_01_chart.json`, `element_02_chart.json`

---

### 2. **Section Headers** (2 templates)
**Use when:** Dividing presentation into major sections, chapter breaks
- Bold section titles
- Transitional slides
- Clean, minimal design

**Example files:** `section_headers/element_31_section_divider.json`

---

### 3. **Content Standard** (15 templates)
**Use when:** Presenting standard text content, explanations, descriptions
- Body text layouts
- Simple, readable design
- **Font sizes:** 36pt (headings), 18pt (body)

**Example files:** `content_standard/element_03_content.json`, `element_04_content.json`

---

### 4. **Content Two Column** (4 templates)
**Use when:** Comparing items, showing before/after, listing features vs benefits
- Split-screen layouts
- Side-by-side content
- Good for comparisons

**Example files:** `content_two_column/element_09_two_column.json`

---

### 5. **Content Image** (3 templates)
**Use when:** Showcasing photos, visual content, image-heavy slides
- Large image placeholders
- Photo-centric layouts
- Minimal text areas

**Example files:** `content_image/element_17_image_layout.json`

---

### 6. **Timelines** (14 templates)
**Use when:** Showing project timelines, roadmaps, process flows, chronological steps
- Horizontal/vertical timelines
- Step-by-step processes
- Sequential information

**Example files:** `timelines/element_23_timeline.json`, `element_24_timeline.json`

---

### 7. **Tables** (14 templates)
**Use when:** Displaying data, comparisons, structured information, spreadsheet data
- Grid layouts
- Tabular data
- Comparative information

**Example files:** `tables/element_54_table.json`, `element_55_table.json`

---

### 8. **Bullet Lists** (1 template)
**Use when:** Listing key points, bullet-point summaries, action items
- Structured lists
- Key takeaways
- Action items

**Example files:** `bullet_lists/element_94_bullet_list.json`

---

### 9. **Title Content** (1 template)
**Use when:** Need both a prominent title and content area together
- Title + body combination
- Balanced layout

**Example files:** `title_content/element_83_title_content.json`

---

### 10. **Complex** (13 templates)
**Use when:** Need multiple content types, rich layouts, advanced designs
- Multi-element slides
- Advanced compositions
- Mixed content types

**Example files:** `complex/element_15_complex.json`, `element_16_complex.json`

---

### 11. **Blank** (3 templates)
**Use when:** Creating custom layouts, minimal designs, flexible content
- Minimal structure
- Maximum flexibility
- Custom designs

**Example files:** `blank/element_77_blank.json`

---

## 🤖 AI Agent Usage Guide

### Quick Selection Logic

```python
import json
from pathlib import Path

def select_template_for_content(content_type, content_description):
    """
    AI Agent logic for selecting the right template
    
    Args:
        content_type: Type of content to display
        content_description: Description of the content
    
    Returns:
        Path to appropriate template directory
    """
    
    base_path = Path("branding/content_elements")
    
    # Load master index
    with open(base_path / "layouts_index.json") as f:
        layouts = json.load(f)
    
    # Selection rules
    rules = {
        "title": "title_slides",
        "cover": "title_slides",
        "introduction": "title_slides",
        
        "section": "section_headers",
        "chapter": "section_headers",
        "divider": "section_headers",
        
        "timeline": "timelines",
        "roadmap": "timelines",
        "process": "timelines",
        "steps": "timelines",
        
        "table": "tables",
        "data": "tables",
        "comparison": "tables",
        "grid": "tables",
        
        "image": "content_image",
        "photo": "content_image",
        "visual": "content_image",
        
        "two column": "content_two_column",
        "split": "content_two_column",
        "versus": "content_two_column",
        
        "bullets": "bullet_lists",
        "list": "bullet_lists",
        "points": "bullet_lists",
        
        "text": "content_standard",
        "paragraph": "content_standard",
        "description": "content_standard",
    }
    
    # Match content type to template
    content_lower = f"{content_type} {content_description}".lower()
    
    for keyword, layout_type in rules.items():
        if keyword in content_lower:
            return base_path / layout_type
    
    # Default to standard content
    return base_path / "content_standard"

# Example usage
template_dir = select_template_for_content("timeline", "project roadmap for 2024")
# Returns: branding/content_elements/timelines/
```

### Loading a Template

```python
import json
import random

def load_random_template(layout_type):
    """Load a random template from a specific layout type"""
    
    layout_dir = Path(f"branding/content_elements/{layout_type}")
    index_file = layout_dir / "index.json"
    
    with open(index_file) as f:
        index = json.load(f)
    
    # Pick a random element
    element = random.choice(index['elements'])
    element_file = layout_dir / element['file']
    
    with open(element_file) as f:
        template = json.load(f)
    
    return template

# Example
template = load_random_template("title_slides")
print(f"Loaded: {template['metadata']['description']}")
```

## 📊 JSON Structure

Each template follows this structure:

```json
{
  "metadata": {
    "element_number": 2,
    "category": "chart",
    "description": "Chart or graph layout",
    "extracted_text": "Sample text..."
  },
  "slide": {
    "title": "PwC Content Element 2",
    "background": {
      "type": "solid",
      "color": "#FFFFFF"
    },
    "components": [
      {
        "type": "richtext",
        "runs": [
          {
            "text": "Sample Text",
            "bold": false,
            "font_size": 350,
            "color": "#D04A02"
          }
        ],
        "box": {"x": 860, "y": 60, "w": 363, "h": 452, "unit": "px"},
        "style": {"align": "left"}
      }
    ]
  }
}
```

## 🎨 PwC Brand Colors

Extracted colors found in templates:

- **PwC Orange (Primary)**: `#D04A02`
- **Black (Text)**: `#000000`
- **White (Background)**: `#FFFFFF`
- **Gray (Secondary)**: `#595959`, `#F2F2F2`

## 📈 Statistics

- **Total Templates**: 95
- **Total Images**: 287
- **Layout Types**: 11
- **Font Sizes**: Accurately extracted (10pt - 350pt)
- **Colors**: Scheme colors mapped to hex values

## 🔄 Regenerating Templates

If you need to regenerate or re-extract templates:

```bash
# Re-extract all content elements
python3 extras/extract_content_elements.py

# Re-extract images
python3 extras/extract_content_element_images.py

# Reorganize into directories
python3 extras/reorganize_content_elements.py
```

## 📚 Related Files

- **Cover Pages**: `branding/covers/` - 75 cover page templates
- **Extraction Scripts**: `extras/extract_*.py`
- **Source Template**: `branding/PwC_ppt_graphic_elements_level1.pptx`

---

**Last Updated**: November 2025  
**Source**: PwC Official Presentation Templates  
**Total Templates**: 95 across 11 layout categories
