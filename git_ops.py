"""
Git Operations Integration for JARVIS - Phase 3
Git command wrapper with safety checks for common operations.
"""
from git import Repo, GitCommandError, InvalidGitRepositoryError
from typing import Optional
import os


class GitOps:
    """Git command automation with safety checks."""
    
    def __init__(self, repo_path: str = "."):
        """
        Initialize GitPython Repo object.
        
        Args:
            repo_path: Path to git repository (default: current directory)
        """
        try:
            self.repo = Repo(repo_path, search_parent_directories=True)
            self.repo_path = self.repo.working_dir
        except InvalidGitRepositoryError:
            raise ValueError("Not a git repository, sir. Please initialize git first.")
    
    def status(self) -> str:
        """
        Get formatted git status.
        
        Returns:
            Formatted status string with branch, staged, unstaged, and untracked files
        """
        try:
            # Get current branch
            branch = self.repo.active_branch.name
            
            # Get file statuses
            changed_files = [item.a_path for item in self.repo.index.diff(None)]
            staged_files = [item.a_path for item in self.repo.index.diff("HEAD")]
            untracked_files = self.repo.untracked_files
            
            # Build status message
            lines = []
            lines.append(f"[Branch: {branch}]")
            lines.append("")
            
            if staged_files:
                lines.append("Staged files:")
                for f in staged_files:
                    lines.append(f"  + {f}")
                lines.append("")
            
            if changed_files:
                lines.append("Unstaged changes:")
                for f in changed_files:
                    lines.append(f"  M {f}")
                lines.append("")
            
            if untracked_files:
                lines.append("Untracked files:")
                for f in untracked_files:
                    lines.append(f"  ? {f}")
                lines.append("")
            
            if not staged_files and not changed_files and not untracked_files:
                lines.append("Working tree clean, sir.")
            
            return "\n".join(lines)
        except Exception as e:
            return f"Error getting status: {str(e)}"
    
    def commit(self, message: str, add_all: bool = True) -> str:
        """
        Stage all and create commit.
        
        Args:
            message: Commit message
            add_all: Whether to stage all changes first (default: True)
            
        Returns:
            Success message or error
        """
        try:
            if not message:
                return "Commit message required, sir."
            
            # Stage all changes if requested
            if add_all:
                self.repo.git.add(A=True)
            
            # Create commit
            commit = self.repo.index.commit(message)
            return f"Committed successfully, sir: {commit.hexsha[:7]} - {message}"
        except Exception as e:
            return f"Commit failed: {str(e)}"
    
    def push(self, remote: str = "origin", force: bool = False) -> str:
        """
        Push current branch with safety check.
        
        Args:
            remote: Remote name (default: "origin")
            force: Force push (blocked for main/master)
            
        Returns:
            Success message or error
        """
        try:
            branch = self.repo.active_branch.name
            
            # Safety check: refuse force push to main/master
            if force and branch in ["main", "master"]:
                return f"Force push to '{branch}' branch refused for safety, sir. This is a destructive operation."
            
            # Warn before pushing to main/master
            if branch in ["main", "master"]:
                return f"About to push to '{branch}' branch. Please confirm this is intentional. Use /git push confirm"
            
            # Perform push
            origin = self.repo.remote(name=remote)
            origin.push(branch)
            return f"Pushed '{branch}' to {remote} successfully, sir."
        except Exception as e:
            return f"Push failed: {str(e)}"
    
    def push_confirm(self, remote: str = "origin") -> str:
        """Push to main/master after confirmation."""
        try:
            branch = self.repo.active_branch.name
            origin = self.repo.remote(name=remote)
            origin.push(branch)
            return f"Pushed '{branch}' to {remote} successfully, sir."
        except Exception as e:
            return f"Push failed: {str(e)}"
    
    def branch(self) -> str:
        """
        List branches with current highlighted.
        
        Returns:
            Formatted branch list
        """
        try:
            current = self.repo.active_branch.name
            branches = [b.name for b in self.repo.branches]
            
            lines = ["Branches:"]
            for b in branches:
                if b == current:
                    lines.append(f"  * {b} (current)")
                else:
                    lines.append(f"    {b}")
            
            return "\n".join(lines)
        except Exception as e:
            return f"Error listing branches: {str(e)}"
    
    def log(self, count: int = 5) -> str:
        """
        Show last N commits.
        
        Args:
            count: Number of commits to show (default: 5)
            
        Returns:
            Formatted commit log
        """
        try:
            commits = list(self.repo.iter_commits(max_count=count))
            
            lines = [f"Last {count} commits:"]
            lines.append("")
            
            for commit in commits:
                hash_short = commit.hexsha[:7]
                author = commit.author.name
                date = commit.committed_datetime.strftime("%Y-%m-%d %H:%M")
                message = commit.message.strip().split('\n')[0]  # First line only
                
                lines.append(f"{hash_short} - {author} - {date}")
                lines.append(f"  {message}")
                lines.append("")
            
            return "\n".join(lines)
        except Exception as e:
            return f"Error getting log: {str(e)}"
    
    def diff(self, cached: bool = False) -> str:
        """
        Show diff of changes.
        
        Args:
            cached: Show staged changes (default: False for unstaged)
            
        Returns:
            Git diff output
        """
        try:
            if cached:
                diff = self.repo.git.diff('--cached')
            else:
                diff = self.repo.git.diff()
            
            if not diff:
                return "No changes to show, sir."
            
            return diff
        except Exception as e:
            return f"Error getting diff: {str(e)}"
    
    def pull(self, remote: str = "origin") -> str:
        """
        Pull from remote.
        
        Args:
            remote: Remote name (default: "origin")
            
        Returns:
            Success message or error
        """
        try:
            branch = self.repo.active_branch.name
            origin = self.repo.remote(name=remote)
            origin.pull(branch)
            return f"Pulled '{branch}' from {remote} successfully, sir."
        except Exception as e:
            return f"Pull failed: {str(e)}"
    
    def create_branch(self, branch_name: str, checkout: bool = True) -> str:
        """
        Create new branch.
        
        Args:
            branch_name: Name for new branch
            checkout: Whether to checkout the new branch (default: True)
            
        Returns:
            Success message or error
        """
        try:
            new_branch = self.repo.create_head(branch_name)
            if checkout:
                new_branch.checkout()
                return f"Created and checked out branch '{branch_name}', sir."
            else:
                return f"Created branch '{branch_name}', sir."
        except Exception as e:
            return f"Branch creation failed: {str(e)}"
    
    def checkout(self, branch_name: str) -> str:
        """
        Checkout existing branch.
        
        Args:
            branch_name: Branch to checkout
            
        Returns:
            Success message or error
        """
        try:
            self.repo.git.checkout(branch_name)
            return f"Checked out branch '{branch_name}', sir."
        except Exception as e:
            return f"Checkout failed: {str(e)}"


def format_git_error(error: str) -> str:
    """
    Format git errors with helpful suggestions.
    
    Args:
        error: Error message
        
    Returns:
        Formatted error with suggestions
    """
    suggestions = {
        "not a git repository": "Initialize git with: git init",
        "nothing to commit": "No changes to commit. Make some changes first.",
        "failed to push": "Try pulling first with: /git pull",
        "refusing to merge": "Resolve merge conflicts manually, sir.",
    }
    
    for key, suggestion in suggestions.items():
        if key.lower() in error.lower():
            return f"{error}\n\nSuggestion: {suggestion}"
    
    return error
