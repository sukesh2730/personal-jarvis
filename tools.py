"""File operations for ROME JARVIS - read, write, run, list, explain."""
import os
import subprocess
import sys
from pathlib import Path
from rich.console import Console

console = Console()

def read_file(filepath):
    """Read and display a file."""
    path = Path(filepath)
    if not path.exists():
        console.print(f"[red]Error: File not found: {filepath}[/red]")
        return None
    if path.stat().st_size > 500000:
        console.print(f"[yellow]Warning: File too large (>500KB): {filepath}[/yellow]")
        return None
    content = path.read_text(encoding='utf-8')
    console.print(f"\n[cyan][File: {filepath}][/cyan]")
    console.print(content)
    return content

def write_file(filepath, content):
    """Write content to a file."""
    path = Path(filepath)
    if path.exists():
        response = console.input("[yellow]File exists. Overwrite? (y/n):[/yellow] ")
        if response.lower() != 'y':
            console.print("[dim]Cancelled.[/dim]")
            return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding='utf-8')
    console.print(f"[green][Saved] {filepath}[/green]")
    return True

def run_file(filepath):
    """Execute a Python file and show output."""
    path = Path(filepath)
    if not path.exists():
        console.print(f"[red]Error: File not found: {filepath}[/red]")
        return None
    if path.suffix != '.py':
        console.print(f"[red]Error: Not a Python file: {filepath}[/red]")
        return None
    result = subprocess.run([sys.executable, str(path)], capture_output=True, text=True, timeout=30)
    if result.stdout:
        console.print("\n[cyan][Output][/cyan]")
        console.print(result.stdout)
    if result.stderr:
        console.print("\n[red][Error][/red]")
        console.print(result.stderr)
    return result.stdout

def list_files(dirpath="."):
    """List files in a directory."""
    path = Path(dirpath)
    if not path.exists():
        console.print(f"[red]Error: Directory not found: {dirpath}[/red]")
        return []
    skip_dirs = {'__pycache__', '.git', 'node_modules', 'venv', '.venv', 'chroma_db'}
    files = []
    console.print(f"\n[cyan]{dirpath}/[/cyan]")
    for item in sorted(path.rglob('*')):
        if any(skip in item.parts for skip in skip_dirs):
            continue
        if item.name == '.env':
            continue
        rel = item.relative_to(path)
        if len(rel.parts) > 2:
            continue
        if item.is_file():
            console.print(f"  {rel}")
            files.append(str(item))
    return files

def explain_file(filepath, ask_fn):
    """Read a file and ask AI to explain it."""
    content = read_file(filepath)
    if content is None:
        return
    prompt = f"""Explain this code clearly.
Point out what it does, key functions,
and any issues you notice.

File: {filepath}

{content}"""
    console.print("\n[cyan][AI Explanation][/cyan]")
    response = ask_fn(prompt)
    console.print(response)
    return response
