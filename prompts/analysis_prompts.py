SYSTEM_ANALYSIS_PROMPT = """
You are an expert Brand Strategist and NLP Content Analyst. 
Your task is to analyze the provided sample brand text and build a comprehensive Brand Voice Profile.

Return your response strictly as a JSON object with the following key structure:
{
  "brand_tone": ["list", "of", "3-5", "tone", "keywords"],
  "vocabulary_style": "description of vocabulary used (e.g., technical, casual, punchy, authoritative)",
  "sentence_structure": "analysis of sentence length, rhythm, and punctuation usage",
  "emotional_appeal": "primary emotional reaction or vibe targeted by the brand",
  "formatting_preferences": "use of emojis, capitalization, bullet points, or line breaks",
  "do_list": ["3 key rules to follow when writing for this brand"],
  "dont_list": ["3 key things to avoid when writing for this brand"]
}
"""

def get_voice_analysis_prompt(sample_text: str, nlp_metrics: dict) -> str:
    """
    Constructs the complete prompt payload for brand voice analysis.
    """
    prompt = f"""
{SYSTEM_ANALYSIS_PROMPT}

Sample Brand Text:
\"\"\"
{sample_text}
\"\"\"

Extracted NLP Metrics:
- Total Word Count: {nlp_metrics.get('total_words', 0)}
- Unique Words: {nlp_metrics.get('unique_words', 0)}
- Top Frequency Keywords: {', '.join([k[0] for k in nlp_metrics.get('top_keywords', [])])}
- Average Word Length: {nlp_metrics.get('avg_word_length', 0)}

Analyze the text and output the JSON profile:
"""
    return prompt