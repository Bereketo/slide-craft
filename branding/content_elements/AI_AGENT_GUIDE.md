# AI Agent Template Selection Guide

Quick reference for AI agents to select appropriate PwC presentation templates.

## 🎯 Template Selection Decision Tree

```
START
  ↓
Is this the first slide of the presentation?
  YES → Use: title_slides/ (25 options)
  NO  → Continue
  ↓
Is this a transition between major topics?
  (e.g., from "Market Analysis" to "Financial Strategy")
  YES → Use: topic_separators/ (1 option)
  NO  → Continue
  ↓
Is this a section divider or chapter break?
  YES → Use: section_headers/ (2 options)
  NO  → Continue
  ↓
Does content include a timeline, roadmap, or process?
  YES → Use: timelines/ (14 options)
  NO  → Continue
  ↓
Does content include tabular data or comparisons?
  YES → Use: tables/ (14 options)
  NO  → Continue
  ↓
Does content feature large images or photos?
  YES → Use: content_image/ (3 options)
  NO  → Continue
  ↓
Does content need two-column layout or side-by-side comparison?
  YES → Use: content_two_column/ (4 options)
  NO  → Continue
  ↓
Does content have bullet points or list items?
  YES → Use: bullet_lists/ (1 option)
  NO  → Continue
  ↓
Is the slide complex with multiple content types?
  YES → Use: complex/ (13 options)
  NO  → Use: content_standard/ (15 options)
```

## 📋 Quick Keywords → Template Mapping

| Keywords | Template Directory | Count |
|----------|-------------------|-------|
| title, cover, introduction, start | `title_slides/` | 25 |
| topic transition, new topic, topic separator | `topic_separators/` | 1 |
| section, chapter, divider, break | `section_headers/` | 2 |
| timeline, roadmap, process, steps, flow | `timelines/` | 14 |
| table, data, grid, spreadsheet, compare | `tables/` | 14 |
| image, photo, picture, visual, gallery | `content_image/` | 3 |
| two column, split, versus, side-by-side | `content_two_column/` | 4 |
| bullets, list, points, items, key points | `bullet_lists/` | 1 |
| text, paragraph, content, description | `content_standard/` | 15 |
| complex, mixed, multi-element, rich | `complex/` | 13 |
| blank, custom, flexible, minimal | `blank/` | 3 |

## 🔄 Topic Separator Usage (IMPORTANT for AI)

### When to Use Topic Separators

**Topic separators** should be automatically inserted between major topic transitions in a presentation.

### Detection Logic

The AI should insert a topic separator when:

1. **Major Topic Change**: Content shifts from one main subject to a completely different subject
   - Example: From "Market Analysis" → Insert Separator → "Financial Projections"
   - Example: From "Product Features" → Insert Separator → "Implementation Strategy"

2. **Slide Count Threshold**: After 3-5 consecutive content slides about one topic, before starting a new topic
   - If slides 2-5 discuss "Customer Demographics", insert separator before slide 6 on "Revenue Model"

3. **Content Structure Indicators**: Keywords that indicate major topic shift:
   - "Next", "Moving on to", "Now let's discuss", "Turning to"
   - "Part 2", "Section 2", "Topic 2"

### What NOT to Use Separators For

- **Don't use for**: Sub-topics within the same main topic
- **Don't use for**: Every single slide change
- **Don't use for**: The first slide (use title_slides instead)
- **Don't use for**: Minor transitions or elaborations on the same topic

### Separator Slide Components

When generating a topic separator slide, update these 3 components:

```json
{
  "components": [
    {
      "type": "richtext",
      "runs": [{"text": "NEW TOPIC NAME HERE", "font_size": 48.0}],
      "box": {"x": 41, "y": 363, "w": 592, "h": 272}
    },
    {
      "type": "richtext",
      "runs": [{"text": "2", "font_size": 350.0, "color": "#FD5108"}],
      "box": {"x": 860, "y": 60, "w": 363, "h": 452}
    },
    {
      "type": "richtext",
      "runs": [{"text": "Presentation Title", "font_size": 10.5}],
      "box": {"x": 112, "y": 682, "w": 925, "h": 16}
    }
  ]
}
```

**Key Updates:**
1. **Topic Title** (component 0): Replace "NEW TOPIC NAME HERE" with actual topic name
2. **Topic Number** (component 1): Update "2" to sequential number (1, 2, 3, 4...)
3. **Footer** (component 2): Keep presentation title consistent across all separators

### Example Presentation Structure

```
Slide 1: Title slide (title_slides)
Slide 2: Market overview (content_standard)
Slide 3: Customer demographics (content_standard)
Slide 4: Market trends chart (content_standard + chart)
Slide 5: TOPIC SEPARATOR - "Competitive Analysis" (topic_separators) ← NUMBER: 1
Slide 6: Competitor comparison table (tables)
Slide 7: SWOT analysis (content_two_column)
Slide 8: TOPIC SEPARATOR - "Our Solution" (topic_separators) ← NUMBER: 2
Slide 9: Product features (bullet_lists)
Slide 10: Implementation timeline (timelines)
Slide 11: TOPIC SEPARATOR - "Financial Projections" (topic_separators) ← NUMBER: 3
Slide 12: Revenue forecast (content_standard + chart)
Slide 13: Investment requirements (tables)
Slide 14: Conclusion (title_slides)
```

## 🤖 Python Implementation

```python
import json
from pathlib import Path
import random

class PwCTemplateSelector:
    """AI Agent for selecting appropriate PwC templates"""
    
    def __init__(self, base_path="branding/content_elements"):
        self.base_path = Path(base_path)
        self.load_layouts()
    
    def load_layouts(self):
        """Load the master layouts index"""
        with open(self.base_path / "layouts_index.json") as f:
            self.layouts = json.load(f)
    
    def select_template(self, slide_position, content_description, content_keywords=None):
        """
        Select the most appropriate template
        
        Args:
            slide_position: int or "first", "last", "middle"
            content_description: str describing the slide content
            content_keywords: list of keywords (optional)
        
        Returns:
            dict with template information
        """
        
        # First slide = always title
        if slide_position == "first" or slide_position == 0:
            return self._get_template_from("title_slides")
        
        # Convert to lowercase for matching
        desc_lower = content_description.lower()
        keywords_str = " ".join(content_keywords) if content_keywords else ""
        search_text = f"{desc_lower} {keywords_str}".lower()
        
        # Priority matching
        if any(k in search_text for k in ["section", "chapter", "divider"]):
            return self._get_template_from("section_headers")
        
        if any(k in search_text for k in ["timeline", "roadmap", "process", "step"]):
            return self._get_template_from("timelines")
        
        if any(k in search_text for k in ["table", "data", "grid", "comparison"]):
            return self._get_template_from("tables")
        
        if any(k in search_text for k in ["image", "photo", "picture", "visual"]):
            return self._get_template_from("content_image")
        
        if any(k in search_text for k in ["two column", "split", "versus", "vs"]):
            return self._get_template_from("content_two_column")
        
        if any(k in search_text for k in ["bullet", "list", "point"]):
            return self._get_template_from("bullet_lists")
        
        if any(k in search_text for k in ["complex", "mixed", "multiple"]):
            return self._get_template_from("complex")
        
        # Default to standard content
        return self._get_template_from("content_standard")
    
    def _get_template_from(self, layout_type):
        """Get a random template from specified layout type"""
        layout_dir = self.base_path / layout_type
        
        with open(layout_dir / "index.json") as f:
            index = json.load(f)
        
        # Pick random element
        element = random.choice(index['elements'])
        
        with open(layout_dir / element['file']) as f:
            template = json.load(f)
        
        return {
            "layout_type": layout_type,
            "element_id": element['id'],
            "file": element['file'],
            "template": template
        }
    
    def get_all_from_type(self, layout_type):
        """Get all templates of a specific type"""
        layout_dir = self.base_path / layout_type
        
        with open(layout_dir / "index.json") as f:
            index = json.load(f)
        
        return index['elements']

# Usage Example
selector = PwCTemplateSelector()

# Select first slide
first_slide = selector.select_template("first", "Introduction to our company")
print(f"Selected: {first_slide['layout_type']}/{first_slide['file']}")

# Select timeline slide
timeline = selector.select_template("middle", "Project roadmap for Q1 2024", ["timeline", "steps"])
print(f"Selected: {timeline['layout_type']}/{timeline['file']}")

# Select data slide
data_slide = selector.select_template("middle", "Quarterly revenue comparison", ["table", "data"])
print(f"Selected: {data_slide['layout_type']}/{data_slide['file']}")
```

## 📊 Template Statistics by Type

| Layout Type | Count | Best For |
|------------|-------|----------|
| **title_slides** | 25 | Opening slides, section intros |
| **content_standard** | 15 | General text content |
| **timelines** | 14 | Sequential processes |
| **tables** | 14 | Data and comparisons |
| **complex** | 13 | Multi-element slides |
| **content_two_column** | 4 | Side-by-side content |
| **content_image** | 3 | Visual-heavy slides |
| **blank** | 3 | Custom layouts |
| **section_headers** | 2 | Chapter breaks |
| **topic_separators** | 1 | Major topic transitions |
| **bullet_lists** | 1 | List items |
| **title_content** | 1 | Title + body combo |

## 🎨 Design Considerations

### Font Sizes by Template Type
- **Title Slides**: 350pt (numbers), 48pt (titles), 10pt (subtitles)
- **Content Standard**: 36pt (headings), 18pt (body)
- **Section Headers**: Varies based on hierarchy
- **Tables**: 14-18pt (cell content)

### Color Usage
- **#D04A02** (PwC Orange): Accent elements, important numbers
- **#000000** (Black): Body text, primary content
- **#FFFFFF** (White): Backgrounds, contrast elements

## ⚡ Quick Commands

```python
# Get specific template
template = selector._get_template_from("title_slides")

# List all available types
print(list(selector.layouts['layout_types'].keys()))

# Get count for each type
for layout, info in selector.layouts['layout_types'].items():
    print(f"{layout}: {info['count']} templates")

# Load specific element by ID
# (Requires custom implementation based on element number)
```

## 🔍 Template Selection Examples

### Example 1: Presentation Opening
```python
slide = selector.select_template(
    slide_position="first",
    content_description="Welcome to Annual Report 2024"
)
# Returns: title_slides/element_XX_chart.json
```

### Example 2: Project Timeline
```python
slide = selector.select_template(
    slide_position="middle",
    content_description="Implementation phases over 6 months",
    content_keywords=["timeline", "phases"]
)
# Returns: timelines/element_XX_timeline.json
```

### Example 3: Data Comparison
```python
slide = selector.select_template(
    slide_position="middle",
    content_description="Revenue vs Costs Q1-Q4",
    content_keywords=["comparison", "data"]
)
# Returns: tables/element_XX_table.json
```

---

**For detailed template information, see:**
- `README.md` - Complete documentation
- `layouts_index.json` - Master index
- `{layout_type}/index.json` - Category-specific indexes



