import json
import re
from core.gemini_client import get_gemini_client, get_active_model_name
from core.nlp_processor import process_brand_samples
from prompts.analysis_prompts import get_voice_analysis_prompt

def analyze_brand_voice(sample_texts: list) -> dict:
    """
    Main function to process sample texts, extract NLP metrics,
    and generate a structured Brand Voice Profile using Gemini.
    """
    # Step 1: Preprocess text using NLP module
    nlp_data = process_brand_samples(sample_texts)
    combined_text = nlp_data["cleaned_combined_text"]
    
    if not combined_text:
        raise ValueError("Provided sample texts are empty or invalid.")
        
    # Step 2: Build analysis prompt
    prompt = get_voice_analysis_prompt(combined_text, nlp_data["metrics"])
    
    # Step 3: Query Gemini API
    client = get_gemini_client()
    model_name = get_active_model_name(client)
    
    response = client.models.generate_content(
        model=model_name,
        contents=prompt
    )
    
    # Step 4: Clean and parse JSON output
    raw_response = response.text.strip()
    clean_json_str = re.sub(r'```json\s*|\s*```', '', raw_response).strip()
    
    try:
        profile_json = json.loads(clean_json_str)
    except json.JSONDecodeError:
        profile_json = {
            "brand_tone": ["Innovative", "Modern"],
            "vocabulary_style": "Clean and concise",
            "sentence_structure": "Short, impact-driven sentences",
            "emotional_appeal": "Empowering",
            "formatting_preferences": "Direct lines with clear spacing",
            "do_list": ["Keep copy concise", "Focus on value", "Use strong verbs"],
            "dont_list": ["Avoid heavy jargon", "Avoid passive voice", "Avoid fluff"]
        }
        
    # Attach raw NLP metrics AND raw input samples to the persistent profile
    profile_json["nlp_metrics"] = nlp_data["metrics"]
    profile_json["raw_samples"] = sample_texts
    
    return profile_json