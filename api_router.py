"""
API Router Module for ROME JARVIS

This module provides a multi-level fallback system for LLM API calls.
It attempts to use Groq, Gemini, Together.ai, and Mistral APIs in order,
falling back to the next provider if rate limits or errors are encountered.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Import API clients
try:
    from groq import Groq
except ImportError:
    Groq = None

try:
    from google import genai
except ImportError:
    genai = None

try:
    from together import Together
except ImportError:
    Together = None

try:
    from mistralai import Mistral
except ImportError:
    Mistral = None


# Token usage tracking
_usage_log = []


def validate_keys():
    """
    Validate API keys on startup.
    
    Returns:
        list: Names of valid/available APIs
    """
    valid_apis = []
    invalid_values = [None, "", "your_groq_key_here", "your_gemini_key_here", 
                     "your_together_key_here", "your_mistral_key_here"]
    
    groq_key = os.getenv("GROQ_API_KEY")
    if groq_key not in invalid_values and Groq:
        valid_apis.append("Groq")
    
    gemini_key = os.getenv("GEMINI_API_KEY")
    if gemini_key not in invalid_values and genai:
        valid_apis.append("Gemini")
    
    together_key = os.getenv("TOGETHER_API_KEY")
    if together_key not in invalid_values and Together:
        valid_apis.append("Together.ai")
    
    mistral_key = os.getenv("MISTRAL_API_KEY")
    if mistral_key not in invalid_values and Mistral:
        valid_apis.append("Mistral")
    
    return valid_apis


def get_stats():
    """
    Get usage statistics for current session.
    
    Returns:
        str: Formatted statistics string
    """
    if not _usage_log:
        return "No queries made this session yet."
    
    total_calls = len(_usage_log)
    total_tokens = sum(entry["tokens"] for entry in _usage_log)
    
    # Provider breakdown
    providers = {}
    for entry in _usage_log:
        provider = entry["provider"]
        providers[provider] = providers.get(provider, 0) + 1
    
    provider_breakdown = ", ".join([f"{p}: {count}" for p, count in providers.items()])
    
    return (f"Session Stats:\n"
            f"  Total queries: {total_calls}\n"
            f"  Estimated tokens: ~{int(total_tokens):,}\n"
            f"  Provider breakdown: {provider_breakdown}")


def get_completion(prompt):
    """
    Get AI completion with 4-level fallback system.
    
    Tries APIs in order: Groq -> Gemini -> Together.ai -> Mistral
    Falls back to next provider if rate limits or errors occur.
    
    Args:
        prompt (str): The user's prompt to send to the LLM
        
    Returns:
        str: The AI's response as a plain string, or an error message if all APIs fail
    """
    
    # Estimate tokens for tracking
    estimated_tokens = len(prompt.split()) * 1.3
    used_provider = None
    
    # Level 1: Try Groq API
    try:
        print("Using Groq API...")
        groq_key = os.getenv("GROQ_API_KEY")
        if groq_key and Groq:
            client = Groq(api_key=groq_key)
            response = client.chat.completions.create(
                model="llama-3.1-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=2000
            )
            used_provider = "Groq"
            result = response.choices[0].message.content
            _usage_log.append({"provider": used_provider, "tokens": estimated_tokens})
            return result
        else:
            raise Exception("Groq API key missing or SDK not installed")
    except Exception as e:
        print(f"Groq limited, switching to Gemini... ({str(e)})")
    
    # Level 2: Try Gemini API
    try:
        print("Using Gemini API...")
        gemini_key = os.getenv("GEMINI_API_KEY")
        if gemini_key and genai:
            client = genai.Client(api_key=gemini_key)
            response = client.models.generate_content(
                model="gemini-2.0-flash-exp",
                contents=prompt,
                config={"max_output_tokens": 2000}
            )
            used_provider = "Gemini"
            result = response.text
            _usage_log.append({"provider": used_provider, "tokens": estimated_tokens})
            return result
        else:
            raise Exception("Gemini API key missing or SDK not installed")
    except Exception as e:
        print(f"Gemini limited, switching to Together.ai... ({str(e)})")
    
    # Level 3: Try Together.ai API
    try:
        print("Using Together.ai API...")
        together_key = os.getenv("TOGETHER_API_KEY")
        if together_key and Together:
            client = Together(api_key=together_key)
            response = client.chat.completions.create(
                model="Qwen/Qwen2.5-Coder-32B-Instruct",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=2000
            )
            used_provider = "Together.ai"
            result = response.choices[0].message.content
            _usage_log.append({"provider": used_provider, "tokens": estimated_tokens})
            return result
        else:
            raise Exception("Together.ai API key missing or SDK not installed")
    except Exception as e:
        print(f"Together.ai limited, switching to Mistral... ({str(e)})")
    
    # Level 4: Try Mistral API
    try:
        print("Using Mistral API...")
        mistral_key = os.getenv("MISTRAL_API_KEY")
        if mistral_key and Mistral:
            client = Mistral(api_key=mistral_key)
            response = client.chat.complete(
                model="codestral-latest",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=2000
            )
            used_provider = "Mistral"
            result = response.choices[0].message.content
            _usage_log.append({"provider": used_provider, "tokens": estimated_tokens})
            return result
        else:
            raise Exception("Mistral API key missing or SDK not installed")
    except Exception as e:
        print(f"Mistral failed: {str(e)}")
    
    # All APIs failed - return error message
    return (
        "Error: All API providers are currently unavailable or rate-limited. "
        "Please wait a few minutes and try again. "
        "Make sure all API keys are correctly set in your .env file."
    )
