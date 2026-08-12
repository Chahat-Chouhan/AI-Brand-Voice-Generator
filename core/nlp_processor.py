import re
import pandas as pd
from collections import Counter
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS

def clean_text(text: str) -> str:
    """
    Cleans raw input text by removing unwanted special characters, extra whitespace,
    and normalizing formatting.
    """
    if not text or not isinstance(text, str):
        return ""
    
    # Remove extra spaces and line breaks
    text = re.sub(r'\s+', ' ', text)
    # Remove non-printable characters while preserving standard punctuation
    text = re.sub(r'[^\x00-\x7F]+', '', text)
    
    return text.strip()

def extract_vocabulary_metrics(text: str, top_n: int = 10) -> dict:
    """
    Analyzes brand text to compute key vocabulary stats: word count, top keywords,
    and average word length.
    """
    cleaned = clean_text(text).lower()
    # Extract alphanumeric words
    words = re.findall(r'\b[a-z]{3,}\b', cleaned)
    
    # Filter out common stop-words
    filtered_words = [w for w in words if w not in ENGLISH_STOP_WORDS]
    
    total_words = len(words)
    unique_words = len(set(words))
    word_freq = Counter(filtered_words).most_common(top_n)
    
    avg_word_len = sum(len(w) for w in words) / total_words if total_words > 0 else 0
    
    return {
        "total_words": total_words,
        "unique_words": unique_words,
        "top_keywords": word_freq,
        "avg_word_length": round(avg_word_len, 2)
    }

def process_brand_samples(samples: list) -> dict:
    """
    Processes multiple text samples provided by the user into a single clean prompt payload
    and aggregated metrics.
    """
    cleaned_samples = [clean_text(sample) for sample in samples if clean_text(sample)]
    combined_text = " ".join(cleaned_samples)
    
    metrics = extract_vocabulary_metrics(combined_text)
    
    return {
        "cleaned_combined_text": combined_text,
        "sample_count": len(cleaned_samples),
        "metrics": metrics
    }

if __name__ == "__main__":
    # Test NLP module locally
    sample_data = [
        "Revolutionize your workflow with our ultra-fast AI tools! Simple, smart, scalable.",
        "Engineered for modern teams who demand excellence and lightning speed."
    ]
    result = process_brand_samples(sample_data)
    print("NLP Processing Success! Sample Output:")
    print(result)