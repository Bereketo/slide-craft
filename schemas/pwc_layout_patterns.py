"""
PwC Layout Patterns for LLM Guidance
Clear, grid-based layout patterns with proper PwC branding
"""

PWC_LAYOUT_PATTERNS = """
══════════════════════════════════════════════════════════════════════════════
 PwC SLIDE LAYOUT PATTERNS (MANDATORY - FOLLOW THESE EXACTLY)
══════════════════════════════════════════════════════════════════════════════

Use these exact layout patterns for professional PwC-branded slides.
All patterns use 12-column grid system with proper spacing and PwC colors.

────────────────────────────────────────────────────────────────────────────
PATTERN 1: TITLE SLIDE (Use for first slide, section intros)
────────────────────────────────────────────────────────────────────────────

NOTE: Many PwC title slides use a beige/cream background (#FFE8D4) instead of white.
Consider using #FFE8D4 for a warm, professional look matching PwC templates.

{{
  "title": "Your Title",
  "background": {{"type": "solid", "color": "#FFE8D4"}},
  "components": [
    {{
      "type": "text",
      "text_type": "title",
      "value": "Your Main Title Here",
      "style": {{
        "font_family": "Georgia",
        "font_size": 44,
        "bold": true,
        "color": "#FFFFFF",
        "fill": "#E0301E",
        "align": "left",
        "valign": "middle",
        "border_color": "#E0301E",
        "border_width": 0
      }},
      "grid": {{"col": 1, "span": 12, "row_h": 2, "y": 1}}
    }},
    {{
      "type": "text",
      "text_type": "body",
      "value": "Subtitle or description text here",
      "style": {{
        "font_family": "Georgia",
        "font_size": 18,
        "bold": false,
        "color": "#2D2D2D",
        "fill": "#CCCCCC",
        "align": "left",
        "valign": "top",
        "border_color": "#CCCCCC",
        "border_width": 0
      }},
      "grid": {{"col": 2, "span": 9, "row_h": 5, "y": 3.5}}
    }}
  ]
}}

────────────────────────────────────────────────────────────────────────────
PATTERN 2: CONTENT WITH IMAGE (Standard content + visual)
────────────────────────────────────────────────────────────────────────────

{{
  "components": [
    {{
      "type": "text",
      "text_type": "h2",
      "value": "Section Heading",
      "style": {{
        "font_family": "Arial",
        "font_size": 28,
        "bold": true,
        "color": "#000000",
        "fill": "#FFFFFF",
        "align": "left",
        "valign": "top",
        "border_color": "#FFFFFF",
        "border_width": 0
      }},
      "grid": {{"col": 1, "span": 10, "row_h": 1, "y": 0.5}}
    }},
    {{
      "type": "richtext",
      "runs": [
        {{"text": "Key Point:", "bold": true, "font_family": "Arial", "font_size": 20, "color": "#E0301E"}},
        {{"text": "\\n• Bullet point 1\\n• Bullet point 2", "font_family": "Georgia", "font_size": 18, "color": "#2D2D2D"}}
      ],
      "style": {{
        "font_family": "Georgia",
        "font_size": 18,
        "color": "#2D2D2D",
        "fill": "#CCCCCC",
        "align": "left",
        "valign": "top",
        "border_color": "#CCCCCC",
        "border_width": 0
      }},
      "grid": {{"col": 1, "span": 6, "row_h": 6, "y": 2}}
    }},
    {{
      "type": "image",
      "src": "https://images.unsplash.com/photo-...",
      "alt": "Descriptive text",
      "grid": {{"col": 8, "span": 5, "row_h": 5, "y": 2.5}}
    }}
  ]
}}

────────────────────────────────────────────────────────────────────────────
PATTERN 3: DATA TABLE (Structured information)
────────────────────────────────────────────────────────────────────────────

{{
  "components": [
    {{
      "type": "text",
      "text_type": "h2",
      "value": "Data Overview",
      "style": {{
        "font_family": "Arial",
        "font_size": 28,
        "bold": true,
        "color": "#000000",
        "fill": "#FFFFFF",
        "align": "left",
        "valign": "top",
        "border_color": "#FFFFFF",
        "border_width": 0
      }},
      "grid": {{"col": 1, "span": 10, "row_h": 1, "y": 0.5}}
    }},
    {{
      "type": "table",
      "content": {{
        "columns": ["Metric", "Value", "Status"],
        "rows": [
          ["Revenue", "$500K", "On Track"],
          ["Growth", "15%", "Exceeded"]
        ]
      }},
      "style": {{
        "font_family": "Georgia",
        "font_size": 16,
        "color": "#2D2D2D",
        "fill": "#CCCCCC",
        "border_color": "#E0301E",
        "border_width": 2,
        "align": "left",
        "valign": "top"
      }},
      "grid": {{"col": 1, "span": 7, "row_h": 5, "y": 2}}
    }}
  ]
}}

────────────────────────────────────────────────────────────────────────────
PATTERN 4: TWO-COLUMN COMPARISON (Side-by-side content)
────────────────────────────────────────────────────────────────────────────

{{
  "components": [
    {{
      "type": "text",
      "text_type": "h2",
      "value": "Comparison Title",
      "style": {{
        "font_family": "Arial",
        "font_size": 28,
        "bold": true,
        "color": "#000000",
        "fill": "#FFFFFF",
        "align": "left",
        "valign": "top",
        "border_color": "#FFFFFF",
        "border_width": 0
      }},
      "grid": {{"col": 1, "span": 10, "row_h": 1, "y": 0.5}}
    }},
    {{
      "type": "richtext",
      "runs": [
        {{"text": "Left Column\\n", "bold": true, "font_family": "Arial", "font_size": 20, "color": "#E0301E"}},
        {{"text": "• Point 1\\n• Point 2", "font_family": "Georgia", "font_size": 18, "color": "#2D2D2D"}}
      ],
      "style": {{
        "font_family": "Georgia",
        "font_size": 18,
        "color": "#2D2D2D",
        "fill": "#CCCCCC",
        "align": "left",
        "valign": "top",
        "border_color": "#CCCCCC",
        "border_width": 0
      }},
      "grid": {{"col": 1, "span": 5, "row_h": 6, "y": 2}}
    }},
    {{
      "type": "richtext",
      "runs": [
        {{"text": "Right Column\\n", "bold": true, "font_family": "Arial", "font_size": 20, "color": "#E0301E"}},
        {{"text": "• Point A\\n• Point B", "font_family": "Georgia", "font_size": 18, "color": "#2D2D2D"}}
      ],
      "style": {{
        "font_family": "Georgia",
        "font_size": 18,
        "color": "#2D2D2D",
        "fill": "#CCCCCC",
        "align": "left",
        "valign": "top",
        "border_color": "#CCCCCC",
        "border_width": 0
      }},
      "grid": {{"col": 7, "span": 5, "row_h": 6, "y": 2}}
    }}
  ]
}}

────────────────────────────────────────────────────────────────────────────
MANDATORY LAYOUT RULES:
────────────────────────────────────────────────────────────────────────────

1. ⚠️ MANDATORY FOOTERS ON EVERY SLIDE:
   ALL slides MUST include these TWO footer components as the LAST two components:
   
   A) Presentation Title Footer (bottom center):
   {{
     "type": "richtext",
     "runs": [{{"text": "YOUR_PRESENTATION_TITLE", "bold": false, "font_size": 10.5, "font_family": "Arial", "color": "#2D2D2D"}}],
     "box": {{"x": 112, "y": 682, "w": 925, "h": 16, "unit": "px"}},
     "style": {{"align": "left", "font_family": "Arial", "font_size": 10.5, "color": "#2D2D2D"}}
   }}
   
   B) PwC Branding Footer (bottom left):
   {{
     "type": "richtext",
     "runs": [{{"text": "PwC", "bold": true, "font_size": 12, "font_family": "Arial", "color": "#000000"}}],
     "box": {{"x": 42, "y": 682, "w": 60, "h": 20, "unit": "px"}},
     "style": {{"align": "left", "font_family": "Arial", "font_size": 12, "color": "#000000"}}
   }}

2. ALWAYS use grid layout (not box) for content components
3. ALWAYS include complete style objects with:
   - font_family (Georgia for titles/body, Arial for h2/captions)
   - font_size (44 for titles, 28 for h2, 18 for body)
   - bold (true for titles/h2, false for body)
   - color (#FFFFFF for title text, #000000 for h2, #2D2D2D for body)
   - fill (#E0301E for titles, #FFFFFF for h2, #CCCCCC for body)
   - align (left for most content)
   - valign (middle for titles, top for content)
   - border_color and border_width

4. COLOR PALETTE (MANDATORY):
   - Title backgrounds: #E0301E (PwC Orange)
   - Title text: #FFFFFF (White)
   - Body backgrounds: #CCCCCC (Light Grey)
   - Body text: #2D2D2D (Web Black)
   - H2 text: #000000 (Black)
   - Accent: #E0301E (PwC Orange for bold text)

5. FONT RULES (STRICT):
   - Titles: Georgia, 44pt, Bold
   - H2: Arial, 28pt, Bold
   - Body: Georgia, 18pt, Regular
   - Captions: Arial, 14-16pt, Regular
   - NEVER use italic

6. SPACING RULES:
   - Leave 1 column gap between adjacent elements
   - Title at y: 0.5-1, row_h: 1-2
   - Content starts at y: 2-3
   - Images: columns 7-12 typically

══════════════════════════════════════════════════════════════════════════════
FOLLOW THESE PATTERNS EXACTLY. DO NOT DEVIATE FROM THESE LAYOUTS.
YOUR OUTPUT MUST MATCH THESE STRUCTURES WITH YOUR CONTENT.
══════════════════════════════════════════════════════════════════════════════
"""

def get_pwc_layout_guidance() -> str:
    """Get PwC layout patterns for LLM prompt"""
    return PWC_LAYOUT_PATTERNS

