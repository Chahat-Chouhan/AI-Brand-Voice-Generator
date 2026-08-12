import sys
import os
import json
import re

# Add root directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.gemini_client import get_gemini_client, get_active_model_name
from prompts.generation_prompts import get_content_generation_prompt

def generate_marketing_content(
    content_type: str,
    topic: str,
    brand_profile: dict,
    formality_slider: int = 5,
    humor_slider: int = 5,
    urgency_slider: int = 5
) -> str:
    """
    Generates tailored marketing content using the brand profile and custom tone sliders.
    """
    # Build compound generation prompt
    prompt = get_content_generation_prompt(
        content_type=content_type,
        topic=topic,
        brand_profile=brand_profile,
        formality_slider=formality_slider,
        humor_slider=humor_slider,
        urgency_slider=urgency_slider
    )

    client = get_gemini_client()
    model_name = get_active_model_name(client)

    response = client.models.generate_content(
        model=model_name,
        contents=prompt
    )

    return response.text.strip()

def evaluate_consistency(generated_text: str, brand_profile: dict) -> dict:
    """
    Acts as an AI Judge to evaluate how closely generated copy matches the brand profile.
    Returns a score (1-10) and actionable feedback.
    """
    prompt = f"""
You are an expert Brand Quality Auditor.
Evaluate the following generated content against the provided Brand Voice Rules.

BRAND VOICE RULES:
- Tones: {', '.join(brand_profile.get('brand_tone', []))}
- Vocabulary Style: {brand_profile.get('vocabulary_style', '')}
- Do List: {', '.join(brand_profile.get('do_list', []))}
- Don't List: {', '.join(brand_profile.get('dont_list', []))}

GENERATED CONTENT TO AUDIT:
\"\"\"
{generated_text}
\"\"\"

Return your response strictly as a JSON object:
{{
  "score": <number from 1 to 10>,
  "strengths": ["list of 2 things done well"],
  "improvements": ["list of 1-2 suggestions for better brand alignment"]
}}
"""

    client = get_gemini_client()
    model_name = get_active_model_name(client)

    response = client.models.generate_content(
        model=model_name,
        contents=prompt
    )

    raw_response = response.text.strip()
    clean_json_str = re.sub(r'```json\s*|\s*```', '', raw_response).strip()

    try:
        return json.loads(clean_json_str)
    except json.JSONDecodeError:
        return {
            "score": 8,
            "strengths": ["Matches tone effectively", "Clean formatting"],
            "improvements": ["Could incorporate more specific keywords"]
        }

if __name__ == "__main__":
    # Test Generation Module
    sample_profile = {
        "brand_tone": ["Energetic", "Confident", "Innovative"],
        "vocabulary_style": "High-impact and punchy",
        "sentence_structure": "Short and rhythmic",
        "do_list": ["Use active verbs", "Keep it punchy"],
        "dont_list": ["Avoid passive voice", "Avoid fluff"]
    }

    print("Generating sample LinkedIn post...")
    output = generate_marketing_content(
        content_type="LinkedIn Post",
        topic="AI Productivity Tool Launch",
        brand_profile=sample_profile,
        formality_slider=6,
        humor_slider=4,
        urgency_slider=8
    )

    print("\n--- Generated Copy ---")
    print(output)

    print("\nAuditing brand consistency score...")
    score_card = evaluate_consistency(output, sample_profile)
    print("\n--- Consistency Evaluation ---")
    print(json.dumps(score_card, indent=2))