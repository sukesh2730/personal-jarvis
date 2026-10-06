"""
PR Description Generator for JARVIS - Phase 3
Generates markdown PR descriptions from git diffs using LLM analysis.
"""
from git import Repo, InvalidGitRepositoryError
from typing import Optional
import os


def generate_pr_description(branch_from: Optional[str] = None, 
                           branch_to: str = "main",
                           api_router=None) -> str:
    """
    Generate markdown PR description from git diff.
    
    Args:
        branch_from: Source branch (default: current branch)
        branch_to: Target branch (default: "main")
        api_router: API router function for LLM analysis
        
    Returns:
        Markdown PR description
    """
    try:
        # Initialize repo
        repo = Repo(".", search_parent_directories=True)
        
        # Get current branch if not specified
        if not branch_from:
            branch_from = repo.active_branch.name
        
        # Get diff between branches
        try:
            diff = repo.git.diff(f"{branch_to}...{branch_from}")
        except Exception:
            return f"Error: Could not compare '{branch_from}' with '{branch_to}'. Check if branches exist."
        
        if not diff:
            return f"No changes detected between '{branch_to}' and '{branch_from}', sir."
        
        # Get changed files with stats
        try:
            diff_stats = repo.git.diff(f"{branch_to}...{branch_from}", "--stat")
        except Exception:
            diff_stats = "Stats unavailable"
        
        # Build prompt for LLM
        prompt = f"""Analyze this git diff and generate a professional pull request description.

Source branch: {branch_from}
Target branch: {branch_to}

Diff statistics:
{diff_stats}

Diff content (first 3000 chars):
{diff[:3000]}

Generate a markdown PR description with these sections:
1. Summary: Brief overview of changes
2. Changes Made: Bullet list of key changes
3. Files Modified: List of files with brief descriptions
4. Breaking Changes: Any breaking changes (or "None")
5. Testing Notes: Suggested testing approach

Keep it concise and professional."""
        
        # Get LLM analysis if available
        if api_router:
            try:
                from api_router import get_completion
                description = get_completion(prompt)
            except Exception as e:
                description = f"# Pull Request: {branch_from} → {branch_to}\n\nError generating description: {e}"
        else:
            # Fallback: basic template
            description = f"""# Pull Request: {branch_from} → {branch_to}

## Summary
Changes from {branch_from} to merge into {branch_to}.

## Changes Made
See diff for details.

## Files Modified
{diff_stats}

## Breaking Changes
Review diff for potential breaking changes.

## Testing Notes
Test all modified functionality."""
        
        return description
    
    except InvalidGitRepositoryError:
        return "Not a git repository, sir. Cannot generate PR description."
    except Exception as e:
        return f"Error generating PR description: {str(e)}"


def save_pr_description(description: str, filename: str = "./pr_description.md") -> str:
    """
    Save PR description to file.
    
    Args:
        description: Markdown description text
        filename: Output filename (default: ./pr_description.md)
        
    Returns:
        Path to saved file
    """
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(description)
        return os.path.abspath(filename)
    except Exception as e:
        raise Exception(f"Failed to save PR description: {e}")


def get_pr_template() -> str:
    """
    Get basic PR description template.
    
    Returns:
        Markdown template
    """
    return """# Pull Request: [Feature Name]

## Summary
Brief overview of what this PR does.

## Changes Made
- Change 1
- Change 2
- Change 3

## Files Modified
- `file1.py` - Description
- `file2.js` - Description

## Breaking Changes
None

## Testing Notes
- Test case 1
- Test case 2

## Related Issues
Closes #[issue number]
"""
