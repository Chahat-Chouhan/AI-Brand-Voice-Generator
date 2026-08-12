def get_content_generation_prompt(
    content_type: str,
    topic: str,
    brand_profile: dict,
    formality_slider: int = 5,
    humor_slider: int = 5,
    urgency_slider: int = 5
) -> str:
    """
    Constructs a compound prompt that enforces brand voice rules along with customized tone sliders.
    """
    do_rules = "\n".join([f"- {rule}" for rule in brand_profile.get("do_list", [])])
    dont_rules = "\n".join([f"- {rule}" for rule in brand_profile.get("dont_list", [])])
    tones = ", ".join(brand_profile.get("brand_tone", ["professional"]))

    prompt = f"""
You are a senior copywriter writing marketing copy for a brand.

BRAND VOICE PROFILE:
- Core Tones: {tones}
- Vocabulary Style: {brand_profile.get('vocabulary_style', 'Standard')}
- Sentence Structure: {brand_profile.get('sentence_structure', 'Standard')}
- Emotional Appeal: {brand_profile.get('emotional_appeal', 'Engaging')}
- Formatting Style: {brand_profile.get('formatting_preferences', 'Standard')}

STRICT RULES TO FOLLOW:
{do_rules}

THINGS TO STRICTLY AVOID:
{dont_rules}

TONE ADJUSTMENT PARAMETERS (1 to 10 scale):
- Formality Level: {formality_slider}/10
- Humor/Playfulness: {humor_slider}/10
- Urgency/Call-to-Action Intensity: {urgency_slider}/10

TASK DETAILS:
- Content Type to Create: {content_type}
- Subject / Topic: {topic}

Write high-quality, creative, brand-consistent output directly for the target format:
"""
    return prompt