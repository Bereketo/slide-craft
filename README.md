# PowerPoint JSON Auto-Alignment & FastAPI Integration

## Overview

This project provides an auto-alignment system for PowerPoint presentations generated from JSON data, and includes a FastAPI server for generating `.pptx` files from your JSON input. The system ensures that slide components (text, images, tables, charts, etc.) are automatically positioned on a grid to prevent overlaps and maintain a clean, professional layout.

**NEW: PwC Branding Guidelines Integration** - The system now includes full support for PwC brand standards, including proper font usage (Georgia for headlines/body, Arial for sub-headlines/labels), approved color palette, and strict typography rules (no italics).

---

## PwC Branding Guidelines

This system enforces PwC's official branding guidelines for PowerPoint presentations:

### Typography Hierarchy

| Component Type | Font Family | Size | Weight | Color | Alignment |
|---------------|-------------|------|--------|-------|-----------|
| **Title** | Georgia (serif) | 44pt | Bold | #FFFFFF on #E0301E background | Left |
| **H2/Sub-headline** | Arial (sans-serif) | 28pt | Bold | #000000 | Left |
| **Body Text** | Georgia (serif) | 18pt | Regular | #2D2D2D on #CCCCCC background | Left |
| **Caption/Label** | Arial (sans-serif) | 14-16pt | Regular | #2D2D2D | Left |
| **Data Numbers** | Arial (sans-serif) | 48pt+ | Bold | #E0301E | Center |
| **Quote** | Georgia (serif) | 20pt | Regular | #000000 | Left |

### Font Usage Rules

- **Serif Font (Georgia)**: Use for Headlines, Body text, Quotes, and Data descriptions
  - Replaces ITC Charter for PowerPoint/system applications
- **Sans-serif Font (Arial)**: Use for Sub-headlines, Introductions, Labels, and Data numbers
  - Replaces Helvetica Neue for PowerPoint/system applications
- **Critical Rules**:
  - ✗ **Never use italics** (strict PwC rule)
  - ✗ Don't use Helvetica Neue in headlines
  - ✗ Don't set large data numbers in Georgia
  - ✗ Don't apply letter spacing/tracking to type

### Color Palette

**Primary Colors:**
- **PwC Orange**: `#E0301E` (core brand color)
- **Black**: `#000000` (primary text color)
- **White**: `#FFFFFF` (text on orange backgrounds)
- **Web Black**: `#2D2D2D` (text on light backgrounds)
- **Light Grey**: `#CCCCCC` (body text box backgrounds)

**Color Usage:**
- Text is primarily BLACK or WHITE
- Use PwC Orange for:
  - Title/Header backgrounds
  - Large data numbers (text color)
  - Accent elements
- White text on orange requires **18pt or larger** (accessibility compliance - WCAG AA)

### Slide Design Template

- **Title boxes**: Background `#E0301E`, Text `#FFFFFF`, Font Georgia Bold 44pt
- **Body text boxes**: Background `#CCCCCC`, Text `#2D2D2D`, Font Georgia 18pt
- **Sub-headlines**: No background, Text `#000000`, Font Arial Bold 28pt

### Example Implementation

See `Sample_PwC_Branded.json` for a complete example of a PwC-branded presentation following all guidelines.

**Core Branding Module**: `core/pwc_branding.py` contains all branding constants and validation functions.

---

## FastAPI Server Usage

You can generate PowerPoint files from JSON using the provided FastAPI server.

### Relevant Files

- **`api/v1/ppt_generator.py`**: FastAPI route for processing JSON and generating PPTX.
- **`services/ppt.py`**: Service layer for processing JSON and generating PPTX.
- **`utils/ppt_generator.py`**: Core rendering logic for converting JSON to PPTX.
- **`utils/ppt_generator_main.py`**: Validation and auto-alignment logic.
- **`schemas/ppt-json-schema.json`**: JSON schema for validating your input.
- **`requirements.txt`**: Required dependencies (includes `fastapi`, `python-pptx`, etc.).

### How to Run the Server

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Start the FastAPI server:**
   ```bash
   uvicorn main:app --reload
   ```
   *(If your FastAPI app is not named `app`, adjust accordingly.)*

3. **Send a POST request with your JSON:**
   - Endpoint: `POST /generate-ppt`
   - Body: Your PowerPoint JSON (see schema for structure)

   Example using `curl`:
   ```bash
   curl -X POST "http://localhost:8000/generate-ppt" \
        -H "Content-Type: application/json" \
        --data-binary @your_presentation.json \
        --output output.pptx
   ```

   Or use Swagger UI at [http://localhost:8000/docs](http://localhost:8000/docs) for interactive API usage.

### What Happens Internally

- The server receives your JSON, validates it against `schemas/ppt-json-schema.json`.
- It auto-aligns components to prevent overlaps (see `utils/ppt_generator_main.py`).
- The presentation is rendered to a `.pptx` file using `utils/ppt_generator.py`.
- The generated PowerPoint file is returned as a download.

---

## Main Components

- **`ppt_generator.py`**: script that generates the needed PPT from normalized json.
- **`utils/json_validator.py`**: Core engine for detecting and resolving overlapping components.
- **`services/ppt.py`**: FastAPI service for PPTX generation from JSON.

## Key Features

- **Overlap Detection:** Identifies and resolves overlapping components.
- **Auto-Alignment Strategies:** Choose from `preserve_order`, `compact`, or `balanced`.
- **Grid System Support:** Honors grid, margins, and gutters from your JSON tokens.
- **Validation & Reporting:** Ensures no overlaps remain and reports layout statistics.

---

## Example: Generate PPTX from JSON via FastAPI

1. Prepare your JSON file (see `schemas/ppt-json-schema.json` for structure).
2. Start the FastAPI server as above.
3. POST your JSON to `/generate-ppt` and receive a `.pptx` file.
---