"""
Emotional Response Modifier for JARVIS - Phase 4
Detects user emotion and adjusts JARVIS tone accordingly.
"""
from typing import Literal


# Emotion keywords for detection
FRUSTRATED_KEYWORDS = [
    "damn", "frustrated", "frustrating", "annoying", "annoyed",
    "not working", "doesn't work", "won't work", "hate", "broken",
    "stupid", "failing", "fail", "error", "bug", "crash", "issue"
]

EXCITED_KEYWORDS = [
    "awesome", "amazing", "love it", "great", "fantastic",
    "perfect", "excellent", "brilliant", "wonderful", "incredible",
    "cool", "nice", "thanks", "thank you", "appreciate"
]

# Emotion-specific system prompt modifications
EMOTION_PROMPTS = {
    "frustrated": """
The user seems frustrated with a technical issue. Adjust your tone:
- Be sympathetic and understanding
- Offer clear, actionable steps
- Break down complex solutions into simple parts
- Acknowledge the difficulty
- Stay calm and solution-focused
""",
    "excited": """
The user is excited about something positive. Match their enthusiasm:
- Share in their excitement appropriately
- Maintain your formal tone but be warmer
- Encourage their progress
- Be supportive and positive
""",
    "neutral": ""  # No modification for neutral tone
}


def detect_emotion(user_input: str) -> Literal["frustrated", "excited", "neutral"]:
    """
    Detect user emotional state from input.
    
    Args:
        user_input: User's message text
        
    Returns:
        "frustrated", "excited", or "neutral"
    """
    if not user_input:
        return "neutral"
    
    user_lower = user_input.lower()
    
    # Check for frustration keywords
    frustrated_count = sum(1 for keyword in FRUSTRATED_KEYWORDS if keyword in user_lower)
    
    # Check for excitement keywords
    excited_count = sum(1 for keyword in EXCITED_KEYWORDS if keyword in user_lower)
    
    # Determine emotion based on keyword counts
    # Require at least 2 keywords to avoid false positives
    if frustrated_count >= 2:
        return "frustrated"
    elif excited_count >= 2:
        return "excited"
    elif frustrated_count > excited_count and frustrated_count > 0:
        return "frustrated"
    elif excited_count > frustrated_count and excited_count > 0:
        return "excited"
    else:
        return "neutral"


def modify_system_prompt(base_prompt: str, emotion: Literal["frustrated", "excited", "neutral"]) -> str:
    """
    Prepend emotion-specific instructions to system prompt.
    
    Args:
        base_prompt: Original system prompt
        emotion: Detected emotion
        
    Returns:
        Modified system prompt
    """
    emotion_instruction = EMOTION_PROMPTS.get(emotion, "")
    
    if emotion_instruction:
        return emotion_instruction + "\n\n" + base_prompt
    else:
        return base_prompt


def get_emotion_indicator(emotion: Literal["frustrated", "excited", "neutral"]) -> str:
    """
    Get a visual indicator for the emotion (for debugging/logging).
    
    Args:
        emotion: Detected emotion
        
    Returns:
        Emoji or text indicator
    """
    indicators = {
        "frustrated": "😤",
        "excited": "😃",
        "neutral": "😐"
    }
    return indicators.get(emotion, "")
