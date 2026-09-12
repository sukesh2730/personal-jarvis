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
    import google.generativeai as genai
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
            return response.choices[0].message.content
        else:
            raise Exception("Groq API key missing or SDK not installed")
    except Exception as e:
        print(f"Groq limited, switching to Gemini... ({str(e)})")
    
    # Level 2: Try Gemini API
    try:
        print("Using Gemini API...")
        gemini_key = os.getenv("GEMINI_API_KEY")
        if gemini_key and genai:
            genai.configure(api_key=gemini_key)
            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(
                prompt,
                generation_config={"max_output_tokens": 2000}
            )
            return response.text
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
            return response.choices[0].message.content
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
            return response.choices[0].message.content
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
