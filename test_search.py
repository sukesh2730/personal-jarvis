"""Test script for search method implementation."""

import os
import tempfile
import shutil
from memory import CodeMemory, SearchResult
from indexer import CodeChunk

def test_search():
    """Test search method with sample data."""
    # Create temporary directory for ChromaDB
    temp_dir = tempfile.mkdtemp()
    
    try:
        # Initialize CodeMemory
        memory = CodeMemory(persist_directory=temp_dir)
        
        # Create sample chunks with different content
        chunks = [
            CodeChunk(
                content="def authenticate_user(username, password):\n    # Verify user credentials\n    return check_credentials(username, password)",
                file_path="auth.py",
                start_line=1,
                end_line=3,
                language="python",
                token_count=25
            ),
            CodeChunk(
                content="def calculate_sum(a, b):\n    # Add two numbers\n    return a + b",
                file_path="math_utils.py",
                start_line=1,
                end_line=3,
                language="python",
                token_count=15
            ),
            CodeChunk(
                content="class User:\n    def __init__(self, username):\n        self.username = username",
                file_path="models.py",
                start_line=1,
                end_line=3,
                language="python",
                token_count=20
            )
        ]
        
        # Store chunks
        print("Setting up test data...")
        count = memory.add_chunks(chunks)
        print(f"✓ Stored {count} chunks\n")
        
        # Test 1: Search with relevant query (should find authentication code)
        print("Test 1: Searching for 'user authentication'...")
        results = memory.search("user authentication", top_k=3)
        print(f"✓ Found {len(results)} results")
        assert len(results) > 0, "Should find at least one result"
        assert isinstance(results[0], SearchResult), "Should return SearchResult objects"
        assert results[0].similarity_score > 0.3, f"Similarity should be > 0.3, got {results[0].similarity_score}"
        # Check that results are sorted descending
        for i in range(len(results) - 1):
            assert results[i].similarity_score >= results[i+1].similarity_score, "Results should be sorted by similarity descending"
        print(f"  Top result: {results[0].file_path} (similarity: {results[0].similarity_score:.3f})")
        
        # Test 2: Search with top_k parameter
        print("\nTest 2: Searching with top_k=1...")
        results = memory.search("calculate numbers", top_k=1)
        print(f"✓ Found {len(results)} results (expected max 1)")
        assert len(results) <= 1, f"Should return at most 1 result, got {len(results)}"
        if results:
            print(f"  Result: {results[0].file_path} (similarity: {results[0].similarity_score:.3f})")
        
        # Test 3: Default top_k (should be 3)
        print("\nTest 3: Searching with default top_k...")
        results = memory.search("python code")
        print(f"✓ Found {len(results)} results (default top_k=3)")
        assert len(results) <= 3, f"Should return at most 3 results with default, got {len(results)}"
        
        # Test 4: Search with irrelevant query (should filter by threshold)
        print("\nTest 4: Searching with irrelevant query...")
        results = memory.search("quantum physics theory", top_k=3)
        print(f"✓ Found {len(results)} results (low similarity filtered)")
        # All results should have similarity > 0.3 if any are returned
        for result in results:
            assert result.similarity_score > 0.3, f"All results should have similarity > 0.3, got {result.similarity_score}"
        
        # Test 5: Verify SearchResult structure
        print("\nTest 5: Verifying SearchResult structure...")
        results = memory.search("user", top_k=2)
        if results:
            result = results[0]
            assert hasattr(result, 'content'), "Should have content field"
            assert hasattr(result, 'file_path'), "Should have file_path field"
            assert hasattr(result, 'start_line'), "Should have start_line field"
            assert hasattr(result, 'end_line'), "Should have end_line field"
            assert hasattr(result, 'language'), "Should have language field"
            assert hasattr(result, 'similarity_score'), "Should have similarity_score field"
            assert result.start_line >= 1, "start_line should be >= 1"
            assert result.end_line >= result.start_line, "end_line should be >= start_line"
            print(f"✓ SearchResult structure is correct")
            print(f"  File: {result.file_path}")
            print(f"  Lines: {result.start_line}-{result.end_line}")
            print(f"  Language: {result.language}")
            print(f"  Similarity: {result.similarity_score:.3f}")
        
        # Test 6: Empty collection search
        print("\nTest 6: Searching empty collection...")
        memory_empty = CodeMemory(persist_directory=tempfile.mkdtemp())
        results = memory_empty.search("anything", top_k=3)
        print(f"✓ Empty collection returned {len(results)} results (expected 0)")
        assert len(results) == 0, "Empty collection should return empty results"
        
        print("\n✅ All tests passed!")
        
    finally:
        # Clean up temporary directory
        shutil.rmtree(temp_dir, ignore_errors=True)

if __name__ == "__main__":
    test_search()
