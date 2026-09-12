"""Codebase indexer for ROME JARVIS - scans directories, extracts code files, and prepares metadata."""

import os
import logging
from dataclasses import dataclass
from typing import List
import tiktoken

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
encoder = tiktoken.get_encoding("cl100k_base")

EXTENSION_TO_LANGUAGE = {
    '.py': 'python', '.js': 'javascript', '.ts': 'typescript', '.java': 'java',
    '.cpp': 'cpp', '.c': 'c', '.h': 'c', '.hpp': 'cpp', '.cs': 'csharp',
    '.go': 'go', '.rs': 'rust', '.rb': 'ruby', '.php': 'php', '.swift': 'swift'
}

IGNORE_DIRECTORIES = {
    'node_modules', '.git', '__pycache__', 'venv', '.venv', 'env',
    'dist', 'build', 'target', '.next', '.nuxt'
}

@dataclass
class CodeChunk:
    """Represents a chunk of source code with metadata."""
    content: str
    file_path: str
    start_line: int
    end_line: int
    language: str
    token_count: int


def is_code_file(file_path: str) -> bool:
    """Check if file has a supported code extension."""
    return os.path.splitext(file_path)[1] in EXTENSION_TO_LANGUAGE


def discover_code_files(project_path: str) -> List[str]:
    """Recursively discover all code files, skipping ignored directories."""
    if not os.path.exists(project_path):
        raise ValueError(f"Project path does not exist: {project_path}")
    
    code_files = []
    for root, dirs, files in os.walk(project_path):
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRECTORIES]
        code_files.extend(os.path.join(root, f) for f in files if is_code_file(os.path.join(root, f)))
    return code_files

def read_file_content(file_path: str) -> str:
    """Read file content with UTF-8 encoding, fallback to latin-1."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except UnicodeDecodeError:
        try:
            with open(file_path, 'r', encoding='latin-1') as f:
                return f.read()
        except Exception as e:
            logger.warning(f"Failed to read {file_path}: {e}")
            return None
    except Exception as e:
        logger.warning(f"Failed to read {file_path}: {e}")
        return None


def count_tokens(text: str) -> int:
    """Count tokens in text using tiktoken cl100k_base encoding."""
    return len(encoder.encode(text))

def chunk_file_content(content: str, file_path: str, language: str) -> List[CodeChunk]:
    """Split file into chunks by token count (~500 tokens each)."""
    lines = content.split('\n')
    total_tokens = count_tokens(content)
    
    # Single chunk for small files
    if total_tokens <= 500:
        return [CodeChunk(content, file_path, 1, len(lines), language, total_tokens)]
    
    # Split large files into chunks
    chunks, current_lines, current_tokens, start_line = [], [], 0, 1
    
    for i, line in enumerate(lines, start=1):
        line_tokens = count_tokens(line + '\n' if i < len(lines) else line)
        
        if current_tokens + line_tokens > 500 and current_lines:
            chunks.append(CodeChunk('\n'.join(current_lines), file_path, start_line, i-1, language, current_tokens))
            current_lines, current_tokens, start_line = [line], line_tokens, i
        else:
            current_lines.append(line)
            current_tokens += line_tokens
    
    # Add final chunk
    if current_lines:
        chunks.append(CodeChunk('\n'.join(current_lines), file_path, start_line, len(lines), language, current_tokens))
    
    return chunks

def scan_codebase(project_path: str) -> List[CodeChunk]:
    """
    Recursively scan project directory and extract code chunks.
    
    Args:
        project_path: Root directory to scan
        
    Returns:
        List of CodeChunk objects with metadata
        
    Raises:
        ValueError: If project_path doesn't exist
    """
    if not os.path.exists(project_path):
        raise ValueError(f"Project path does not exist: {project_path}")
    
    code_files = discover_code_files(project_path)
    all_chunks, file_count = [], 0
    
    for file_path in code_files:
        content = read_file_content(file_path)
        if content is None:
            continue
        
        file_ext = os.path.splitext(file_path)[1]
        language = EXTENSION_TO_LANGUAGE.get(file_ext, 'unknown')
        
        try:
            relative_path = os.path.relpath(file_path, project_path)
        except ValueError:
            relative_path = file_path
        
        chunks = chunk_file_content(content, relative_path, language)
        all_chunks.extend(chunks)
        
        file_count += 1
        if file_count % 10 == 0:
            logger.info(f"Indexed {file_count} files...")
    
    logger.info(f"Scan complete: {file_count} files, {len(all_chunks)} chunks")
    return all_chunks