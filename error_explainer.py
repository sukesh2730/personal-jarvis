"""
Error Explainer Tool for JARVIS - Phase 3
Analyzes Python tracebacks and generates explanations with fix suggestions.
"""
import re
from typing import Optional


# Common Python exception types and their documentation URLs
EXCEPTION_DOCS = {
    "AttributeError": "https://docs.python.org/3/library/exceptions.html#AttributeError",
    "ImportError": "https://docs.python.org/3/library/exceptions.html#ImportError",
    "ModuleNotFoundError": "https://docs.python.org/3/library/exceptions.html#ModuleNotFoundError",
    "KeyError": "https://docs.python.org/3/library/exceptions.html#KeyError",
    "IndexError": "https://docs.python.org/3/library/exceptions.html#IndexError",
    "TypeError": "https://docs.python.org/3/library/exceptions.html#TypeError",
    "ValueError": "https://docs.python.org/3/library/exceptions.html#ValueError",
    "NameError": "https://docs.python.org/3/library/exceptions.html#NameError",
    "SyntaxError": "https://docs.python.org/3/library/exceptions.html#SyntaxError",
    "IndentationError": "https://docs.python.org/3/library/exceptions.html#IndentationError",
    "ZeroDivisionError": "https://docs.python.org/3/library/exceptions.html#ZeroDivisionError",
    "FileNotFoundError": "https://docs.python.org/3/library/exceptions.html#FileNotFoundError",
    "PermissionError": "https://docs.python.org/3/library/exceptions.html#PermissionError",
    "RuntimeError": "https://docs.python.org/3/library/exceptions.html#RuntimeError",
    "StopIteration": "https://docs.python.org/3/library/exceptions.html#StopIteration",
    "AssertionError": "https://docs.python.org/3/library/exceptions.html#AssertionError",
}


def extract_traceback(source: str) -> Optional[str]:
    """
    Extract Python traceback from text.
    
    Args:
        source: Text containing potential traceback
        
    Returns:
        Extracted traceback or None if not found
    """
    # Look for "Traceback (most recent call last):" pattern
    pattern = r'(Traceback \(most recent call last\):.*?)(?=\n\n|\nTraceback|\Z)'
    match = re.search(pattern, source, re.DOTALL)
    
    if match:
        return match.group(1).strip()
    
    # Alternative: look for just the exception line
    pattern = r'([A-Z]\w+Error|[A-Z]\w+Exception):.*'
    match = re.search(pattern, source)
    if match:
        return match.group(0).strip()
    
    return None


def get_exception_type(traceback: str) -> Optional[str]:
    """
    Extract exception type from traceback.
    
    Args:
        traceback: Traceback text
        
    Returns:
        Exception type (e.g., "AttributeError") or None
    """
    # Look for exception at the end of traceback
    pattern = r'([A-Z]\w+(?:Error|Exception|Warning)):'
    matches = re.findall(pattern, traceback)
    
    if matches:
        return matches[-1]  # Last match is usually the actual exception
    
    return None


def get_doc_link(exception_type: str) -> Optional[str]:
    """
    Get Python docs URL for exception type.
    
    Args:
        exception_type: Exception class name
        
    Returns:
        Documentation URL or None
    """
    return EXCEPTION_DOCS.get(exception_type)


def explain_error(traceback: str, api_router=None) -> str:
    """
    Use LLM to explain error and suggest fixes.
    
    Args:
        traceback: Python traceback text
        api_router: API router function for LLM call
        
    Returns:
        Formatted explanation with fixes and doc links
    """
    if not traceback:
        return "No traceback found, sir. Please provide a Python error message."
    
    # Extract exception type
    exception_type = get_exception_type(traceback)
    doc_link = get_doc_link(exception_type) if exception_type else None
    
    # Build prompt for LLM
    prompt = f"""Analyze this Python error and provide a concise explanation with fix suggestions.

Error traceback:
{traceback}

Please provide:
1. Error Type: What kind of error this is
2. Likely Cause: Why this error occurred
3. Fix Suggestions: 2-3 specific ways to fix it

Keep it concise and actionable."""
    
    # Get explanation from LLM if available
    explanation = ""
    if api_router:
        try:
            from api_router import get_completion
            explanation = get_completion(prompt)
        except:
            explanation = "Could not generate LLM explanation, sir."
    
    # Format output
    lines = []
    lines.append("=" * 60)
    lines.append("ERROR ANALYSIS")
    lines.append("=" * 60)
    lines.append("")
    
    if exception_type:
        lines.append(f"Exception Type: {exception_type}")
        lines.append("")
    
    if explanation:
        lines.append(explanation)
        lines.append("")
    
    if doc_link:
        lines.append(f"Documentation: {doc_link}")
        lines.append("")
    
    lines.append("Traceback:")
    lines.append(traceback)
    lines.append("")
    lines.append("=" * 60)
    
    return "\n".join(lines)


def quick_diagnose(exception_type: str, message: str) -> str:
    """
    Provide quick diagnosis for common errors without LLM.
    
    Args:
        exception_type: Type of exception
        message: Error message
        
    Returns:
        Quick diagnosis string
    """
    diagnoses = {
        "AttributeError": "An object doesn't have the attribute you're trying to access. Check spelling and object type.",
        "ImportError": "Module import failed. Check if module is installed: pip install [module_name]",
        "ModuleNotFoundError": "Module not found. Install it with: pip install [module_name]",
        "KeyError": "Dictionary key doesn't exist. Use .get() method or check if key exists first.",
        "IndexError": "List index out of range. Check list length before accessing.",
        "TypeError": "Wrong type used in operation. Check if types are compatible.",
        "ValueError": "Correct type but inappropriate value. Validate input values.",
        "NameError": "Variable not defined. Check spelling and variable scope.",
        "SyntaxError": "Python syntax is incorrect. Check parentheses, quotes, and colons.",
        "IndentationError": "Indentation is inconsistent. Use 4 spaces per indent level.",
        "ZeroDivisionError": "Division by zero attempted. Add check: if denominator != 0",
        "FileNotFoundError": "File doesn't exist at specified path. Check path and file existence.",
    }
    
    return diagnoses.get(exception_type, "Unexpected error occurred. Check the traceback for details.")
