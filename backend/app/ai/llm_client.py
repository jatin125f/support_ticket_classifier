import os
import logging
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

_client = None


def get_genai_client():
    """
    Get or lazily initialize the Google GenAI client.
    Returns None if GEMINI_API_KEY is not configured or google-genai is unavailable.
    """
    global _client
    if _client is not None:
        return _client

    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key:
        logger.warning("GEMINI_API_KEY is not set. Gemini fallback will return safe defaults.")
        return None

    try:
        from google import genai
        _client = genai.Client(api_key=api_key)
        return _client
    except Exception as e:
        logger.error(f"Failed to initialize Gemini GenAI client: {e}")
        return None


def generate_gemini_response(prompt: str, model_name: str = "gemini-2.5-flash") -> Optional[str]:
    """
    Call Gemini LLM with safety handling and error catching.
    """
    client = get_genai_client()
    if client is None:
        return None

    try:
        response = client.models.generate_content(
            model=model_name,
            contents=prompt
        )
        if response and response.text:
            return response.text.strip()
        return None
    except Exception as e:
        logger.warning(f"Gemini API call failed: {e}")
        return None
