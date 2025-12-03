"""
Dynamic Prompt Builder with PwC Layout Patterns
"""

from schemas.prompt import LLM_PROMPT
from schemas.pwc_layout_patterns import get_pwc_layout_guidance


def build_prompt_with_templates(user_input: str) -> str:
    """
    Build LLM prompt with PwC layout patterns
    
    Args:
        user_input: User's presentation request
    
    Returns:
        Complete prompt with layout guidance
    """
    
    # Get PwC layout patterns
    layout_guidance = get_pwc_layout_guidance()
    
    # Insert layout patterns into the prompt
    # Find insertion point - right after the template selection section
    prompt_parts = LLM_PROMPT.split("══════════════════════════════════════════════════════════════════════════════")
    
    if len(prompt_parts) >= 3:
        # Insert after "TEMPLATE SELECTION SYSTEM" section, before "PwC BRANDING GUIDELINES"
        enhanced_prompt = (
            prompt_parts[0] +
            "══════════════════════════════════════════════════════════════════════════════" +
            prompt_parts[1] +
            "\n\n" +
            layout_guidance +
            "\n\n══════════════════════════════════════════════════════════════════════════════" +
            "══════════════════════════════════════════════════════════════════════════════".join(prompt_parts[2:])
        )
    else:
        # Fallback: prepend before the prompt
        enhanced_prompt = layout_guidance + "\n\n" + LLM_PROMPT
    
    # Add user input
    final_prompt = enhanced_prompt.format(input_information=user_input)
    
    return final_prompt


# For backward compatibility
def get_prompt(user_input: str) -> str:
    """Legacy function name"""
    return build_prompt_with_templates(user_input)

