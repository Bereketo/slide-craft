import openai
import json
import traceback
import tempfile
from pathlib import Path
from utils.ppt_generator import render_pptx
from utils.json_validator import  validate_and_fix
from schemas.prompt import LLM_PROMPT
from schemas.dynamic_prompt import build_prompt_with_templates
from fastapi import HTTPException
from fastapi.responses import FileResponse
from core.logger_setup import app_logger as logger
from services.template_integration import TemplateIntegrationService
import os
from dotenv import load_dotenv
from datetime import datetime
load_dotenv()

def load_covers_index():
    """Load the covers index.json file."""
    try:
        covers_index_path = Path("branding/covers/index.json")
        with open(covers_index_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load covers index: {e}")
        return None


def select_best_cover(use_case: str, covers_index: dict) -> dict:
    """
    Use LLM to select the most relevant cover based on the use case description.
    
    Args:
        use_case: The presentation topic/use case
        covers_index: The covers index dictionary
        
    Returns:
        Selected cover dictionary from index
    """
    if not covers_index or not covers_index.get('covers'):
        logger.warning("No covers available, returning None")
        return None
    
    # Create a simplified list of covers for the LLM
    covers_summary = []
    for cover in covers_index['covers']:
        covers_summary.append({
            "id": cover['id'],
            "description": cover['description']
        })
    
    selection_prompt = f"""Based on the following presentation use case, select the MOST relevant cover slide by returning ONLY the cover ID number (just the number, nothing else).

Presentation Use Case:
{use_case}

Available Covers:
{json.dumps(covers_summary, indent=2)}

Return ONLY the ID number of the best matching cover (e.g., 5)."""
    
    try:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a presentation design expert. Select the most relevant cover based on theme, subject, and mood."},
                {"role": "user", "content": selection_prompt}
            ],
            temperature=0.1,
            max_tokens=10
        )
        
        # Extract the cover ID
        cover_id_str = response.choices[0].message.content.strip()
        cover_id = int(cover_id_str)
        
        # Find and return the selected cover
        for cover in covers_index['covers']:
            if cover['id'] == cover_id:
                logger.info(f"Selected cover {cover_id}: {cover['description'][:80]}...")
                return cover
        
        # Fallback to first cover if ID not found
        logger.warning(f"Cover ID {cover_id} not found, using first cover")
        return covers_index['covers'][0]
        
    except Exception as e:
        logger.error(f"Error selecting cover: {e}, using first cover as fallback")
        return covers_index['covers'][0]


def load_and_customize_cover(cover_info: dict, presentation_title: str, author_name: str = None) -> dict:
    """
    Load the cover subtitle JSON and customize it with actual data.
    
    Args:
        cover_info: Cover information from index.json
        presentation_title: The title of the presentation
        author_name: Author name (optional)
        
    Returns:
        Customized cover slide JSON
    """
    try:
        # Load the subtitle JSON
        subtitle_path = Path("branding/covers/subtitles") / cover_info['file']
        with open(subtitle_path, 'r', encoding='utf-8') as f:
            cover_data = json.load(f)
        
        # Path to the full-size cover background image
        cover_image_path = f"branding/covers/images/{cover_info['image']}"
        
        # Get current date
        current_date = datetime.now().strftime("%B %Y")
        
        # Create a full-slide background image component (1280x720 for 16:9)
        background_image_component = {
            "type": "image",
            "src": cover_image_path,
            "alt": f"Cover background {cover_info['id']}",
            "box": {
                "x": 0,
                "y": 0,
                "w": 1280,
                "h": 720,
                "unit": "px"
            },
            "object_fit": "cover"
        }
        
        # First pass: identify and collect component types
        components_list = cover_data['slide']['components']
        author_box_y = None
        
        for idx, component in enumerate(components_list):
            if component['type'] == 'image':
                # Update the logo/small image path
                component['src'] = "branding/covers/logo/pwc_logo.png"
                
            elif component['type'] == 'richtext':
                runs = component.get('runs', [])
                component_text = ''.join(run.get('text', '') for run in runs).lower()
                
                # Title component
                if any(phrase in component_text for phrase in ['presentation title', 'covers library', 'cover ']):
                    component['runs'] = [{
                        "text": presentation_title,
                        "bold": False,
                        "font_size": 48,
                        "font_family": "Georgia"
                    }]
                    logger.info(f"Replaced title with: {presentation_title}")
                
                # Author component  
                elif any(phrase in component_text for phrase in ['presentation by', 'name manually bold']):
                    display_name = author_name if author_name else 'PwC Team'
                    component['runs'] = [
                        {
                            "text": "Presentation by ",
                            "bold": False,
                            "font_size": 14,
                            "font_family": "Arial"
                        },
                        {
                            "text": display_name,
                            "bold": True,
                            "font_size": 14,
                            "font_family": "Arial"
                        }
                    ]
                    if 'box' in component:
                        author_box_y = component['box']['y']
                    logger.info(f"Replaced author with: {display_name} at y={author_box_y}")
                
                # Date component
                elif 'month' in component_text and 'year' in component_text:
                    component['runs'] = [{
                        "text": current_date,
                        "bold": False,
                        "font_size": 14,
                        "font_family": "Arial"
                    }]
                    
                    # Fix overlap: If date has same Y as author, move it down
                    if 'box' in component and author_box_y is not None:
                        if component['box']['y'] == author_box_y:
                            component['box']['y'] = author_box_y + 35
                            logger.info(f"Moved date from y={author_box_y} to y={component['box']['y']}")
                    logger.info(f"Replaced date with: {current_date}")
        
        # Insert the background image as the first component (z-index will place it behind)
        cover_slide = cover_data['slide']
        cover_slide['components'].insert(0, background_image_component)
        
        logger.info(f"Cover slide customized with background image: {cover_image_path}")
        
        # Return the customized slide
        return cover_slide
        
    except Exception as e:
        logger.error(f"Error loading/customizing cover: {e}\n{traceback.format_exc()}")
        return None


async def process_data_to_ppt(request_id,data):
    deck = data
    try:
        schema = json.loads(Path("schemas/ppt-json-schema.json").read_text(encoding="utf-8"))
    except Exception as e:
        logger.error(str(e))
        print(traceback.format_exc())
        raise HTTPException(400,"Failed to load schema")
    with tempfile.NamedTemporaryFile(suffix=".pptx", delete=False) as tmp:
        tmp_path = Path(tmp.name)
    try:
        fixed_deck, _ = validate_and_fix(deck, schema)
        render_pptx(fixed_deck, schema, tmp_path)
        return FileResponse(
            path=tmp_path,
            filename=f"generated_{request_id}.pptx",
            media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation"
        )
    except Exception as e:
        logger.error(f"Error generating PPT: {e}\n{traceback.format_exc()}")
        raise HTTPException(400, f"Failed to generate PPT: {str(e)}")



def extract_presentation_info(user_input: str) -> dict:
    """
    Extract presentation title and use case from user input using LLM.
    
    Args:
        user_input: The user's presentation request
        
    Returns:
        Dictionary with 'title', 'use_case', and optional 'author'
    """
    extraction_prompt = f"""Extract the following information from the user's presentation request and return ONLY a valid JSON object:

1. presentation_title: A concise, professional title for the presentation (max 10 words)
2. use_case: A brief description of the presentation's purpose, theme, and target audience (1-2 sentences)
3. author: The author name if mentioned, otherwise null

User Request:
{user_input}

Return ONLY the JSON object in this exact format:
{{
  "presentation_title": "...",
  "use_case": "...",
  "author": "..." or null
}}"""

    try:
        response = openai.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that extracts structured information from text."},
                {"role": "user", "content": extraction_prompt}
            ],
            temperature=0.1,
            max_tokens=200,
        )
        
        content = response.choices[0].message.content.strip()
        if content.startswith("```"):
            content = content.strip().lstrip("```json").lstrip("```").rstrip("```").strip()
        
        info = json.loads(content)
        logger.info(f"Extracted presentation info: {info}")
        return info
        
    except Exception as e:
        logger.error(f"Error extracting presentation info: {e}")
        # Fallback to basic extraction
        return {
            "presentation_title": "Professional Presentation",
            "use_case": user_input[:200],
            "author": None
        }


def call_llm(response, include_cover: bool = True):
    """
    Calls OpenAI LLM to generate a valid JSON PPT using the LLM_PROMPT and the provided response as input_information.
    Intelligently selects and prepends a cover slide based on the presentation content.
    
    Args:
        response: The user input/information for generating the presentation
        include_cover: Whether to include an intelligent cover page (default: True)
    
    Returns:
        Complete PPT JSON with cover slide prepended
    """
    
    cover_slide = None
    
    # Step 1: Extract presentation info and select cover if enabled
    if include_cover:
        try:
            logger.info("Extracting presentation information for cover selection...")
            pres_info = extract_presentation_info(response)
            
            logger.info("Loading covers index...")
            covers_index = load_covers_index()
            
            if covers_index:
                logger.info("Selecting best cover based on use case...")
                selected_cover = select_best_cover(pres_info['use_case'], covers_index)
                
                if selected_cover:
                    logger.info(f"Customizing cover slide with title: {pres_info['presentation_title']}")
                    cover_slide = load_and_customize_cover(
                        selected_cover,
                        pres_info['presentation_title'],
                        pres_info.get('author')
                    )
                    
                    if cover_slide:
                        logger.info("✓ Cover slide successfully created and customized")
                    else:
                        logger.warning("Failed to customize cover slide")
                else:
                    logger.warning("No cover selected")
            else:
                logger.warning("Covers index not loaded")
                
        except Exception as e:
            logger.error(f"Error in cover selection process: {e}\n{traceback.format_exc()}")
            # Continue without cover if there's an error

    # Step 2: Generate the main presentation content with template examples
    try:
        logger.info("Building prompt with template examples...")
        prompt = build_prompt_with_templates(response)
        logger.info("Generating main presentation slides...")
        completion = openai.chat.completions.create(
            model="gpt-4.1",
            messages=[
                {"role": "system", "content": "You are a helpful assistant for generating PPT JSON presentations."},
                {"role": "user", "content": prompt}
            ],
            # temperature=0.2,
            # max_tokens=4000,
        )
        
        # Print tokens used in the completion call if available
        try:
            usage = getattr(completion, 'usage', None)
            if usage:
                logger.info(f"OpenAI completion token usage: {usage}")
        except Exception as token_exc:
            logger.warning(f"Could not print token usage: {token_exc}")

        # Extract the JSON from response
        content = completion.choices[0].message.content
        if content.strip().startswith("```"):
            content = content.strip().lstrip("```json").lstrip("```").rstrip("```").strip()
        ppt_json = json.loads(content)
        
        # Step 3: Integrate template selections
        try:
            logger.info("Integrating content element templates...")
            template_service = TemplateIntegrationService()
            ppt_json = template_service.integrate_templates(ppt_json)
            logger.info("✓ Template integration complete")
        except Exception as template_error:
            logger.warning(f"Template integration failed, continuing without: {template_error}")
            # Continue without template integration if it fails
        
        # Step 4: Prepend cover slide if available
        if cover_slide and 'slides' in ppt_json:
            logger.info("Prepending cover slide to presentation...")
            ppt_json['slides'].insert(0, cover_slide)
            logger.info(f"✓ Final presentation has {len(ppt_json['slides'])} slides (including cover)")
        elif 'slides' in ppt_json:
            logger.info(f"Presentation generated with {len(ppt_json['slides'])} slides (no cover)")
        
        return ppt_json
        
    except Exception as e:
        logger.error(f"Error calling OpenAI LLM: {e}\n{traceback.format_exc()}")
        raise HTTPException(400, f"Failed to call OpenAI or process its output: {str(e)}")