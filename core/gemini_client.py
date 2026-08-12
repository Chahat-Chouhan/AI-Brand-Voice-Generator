import os
from dotenv import load_dotenv
from google import genai

# Load environment variables from .env file
load_dotenv()

def get_gemini_client():
    """
    Initializes and returns the Google Gemini API client.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY is missing. Please set it in your .env file.")
    
    # Initialize client using the official google-genai SDK
    client = genai.Client(api_key=api_key)
    return client

def get_active_model_name(client):
    """
    Dynamically selects an active available model from your key's model list.
    """
    # Priority list of current models
    preferred_models = [
        "gemini-3.6-flash",
        "gemini-3.5-flash",
        "gemini-3.5-flash-lite",
        "gemini-3.1-flash-lite"
    ]
    
    try:
        # Get models supported by your API key
        available_models = [m.name.replace("models/", "") for m in client.models.list()]
        
        # Select first matching preferred model
        for pref in preferred_models:
            if pref in available_models:
                return pref
                
        # Fallback to any model containing 'flash' or 'pro'
        for m in available_models:
            if "flash" in m or "pro" in m:
                return m
                
        return available_models[0] if available_models else "gemini-3.6-flash"
    except Exception:
        return "gemini-3.6-flash"

def test_connection():
    """
    Verifies connection and runs a sample request using the active model.
    """
    try:
        client = get_gemini_client()
        active_model = get_active_model_name(client)
        print(f"Using active model: {active_model}")
        
        response = client.models.generate_content(
            model=active_model,
            contents="Say 'API connection successful!' if you can read this."
        )
        return f"[{active_model}]: {response.text.strip()}"
    except Exception as e:
        return f"Connection failed: {str(e)}"

if __name__ == "__main__":
    print(test_connection())