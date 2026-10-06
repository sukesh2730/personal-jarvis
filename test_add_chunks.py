"""Test script for add_chunks method implementation."""

import os
import tempfile
import shutil
from memory import CodeMemory
from indexer import CodeChunk

def test_add_chunks():
    """Test add_chunks method with sample data."""
    # Create temporary directory for ChromaDB
    temp_dir = tempfile.mkdtemp()
    
    try:
        # Initialize CodeMemory
        memory = CodeMemory(persist_directory=temp_dir)
        
        # Create sample chunks
        chunks = [
            CodeChunk(
                content="def hello():\n    print('Hello, World!')",
                file_path="test.py",
                start_line=1,
                end_line=2,
                language="python",
                token_count=15
            ),
            CodeChunk(
                content="def goodbye():\n    print('Goodbye!')",
                file_path="test.py",
                start_line=4,
                end_line=5,
                language="python",
                token_count=12
            )
        ]
        
        # Test 1: Add chunks without file_path
        print("Test 1: Adding chunks without file_path parameter...")
        count = memory.add_chunks(chunks)
        print(f"✓ Stored {count} chunks (expected 2)")
        assert count == 2, f"Expected 2, got {count}"
        
        # Test 2: Add chunks with file_path (should replace existing)
        print("\nTest 2: Adding chunks with file_path parameter (replacement)...")
        new_chunks = [
            CodeChunk(
                content="def greet(name):\n    print(f'Hello, {name}!')",
                file_path="test.py",
                start_line=1,
                end_line=2,
                language="python",
                token_count=18
            )
        ]
        count = memory.add_chunks(new_chunks, file_path="test.py")
        print(f"✓ Replaced and stored {count} chunks (expected 1)")
        assert count == 1, f"Expected 1, got {count}"
        
        # Test 3: Add empty list
        print("\nTest 3: Adding empty list...")
        count = memory.add_chunks([])
        print(f"✓ Stored {count} chunks (expected 0)")
        assert count == 0, f"Expected 0, got {count}"
        
        # Test 4: Batch processing with >100 chunks
        print("\nTest 4: Testing batch processing with 150 chunks...")
        large_batch = [
            CodeChunk(
                content=f"# Chunk {i}\ndef func_{i}():\n    pass",
                file_path="large.py",
                start_line=i*3+1,
                end_line=i*3+3,
                language="python",
                token_count=10
            )
            for i in range(150)
        ]
        count = memory.add_chunks(large_batch)
        print(f"✓ Stored {count} chunks in batches (expected 150)")
        assert count == 150, f"Expected 150, got {count}"
        
        print("\n✅ All tests passed!")
        
    finally:
        # Clean up temporary directory
        shutil.rmtree(temp_dir, ignore_errors=True)

if __name__ == "__main__":
    test_add_chunks()
