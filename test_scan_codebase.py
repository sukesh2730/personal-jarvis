"""Test scan_codebase function from indexer.py"""

import os
import tempfile
import shutil
from indexer import scan_codebase, CodeChunk

def test_scan_codebase_basic():
    """Test that scan_codebase correctly scans a simple project."""
    # Create temporary project directory
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a simple Python file
        test_file = os.path.join(temp_dir, "test.py")
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write("def hello():\n    print('Hello, World!')\n")
        
        # Scan the codebase
        chunks = scan_codebase(temp_dir)
        
        # Verify results
        assert len(chunks) > 0, "Should find at least one chunk"
        assert isinstance(chunks[0], CodeChunk), "Should return CodeChunk objects"
        assert chunks[0].language == 'python', "Should detect Python language"
        assert "hello" in chunks[0].content, "Should contain the function code"
        print(f"✓ Basic scan test passed: Found {len(chunks)} chunk(s)")

def test_scan_codebase_invalid_path():
    """Test that scan_codebase raises ValueError for invalid path."""
    try:
        scan_codebase("/nonexistent/path/that/does/not/exist")
        assert False, "Should raise ValueError for invalid path"
    except ValueError as e:
        assert "does not exist" in str(e)
        print("✓ Invalid path test passed: Correctly raises ValueError")

def test_scan_codebase_with_ignored_dirs():
    """Test that scan_codebase ignores directories like node_modules."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a Python file in main directory
        main_file = os.path.join(temp_dir, "main.py")
        with open(main_file, 'w', encoding='utf-8') as f:
            f.write("print('main')\n")
        
        # Create node_modules directory with a file (should be ignored)
        node_modules = os.path.join(temp_dir, "node_modules")
        os.makedirs(node_modules)
        ignored_file = os.path.join(node_modules, "ignored.js")
        with open(ignored_file, 'w', encoding='utf-8') as f:
            f.write("console.log('ignored');\n")
        
        # Scan the codebase
        chunks = scan_codebase(temp_dir)
        
        # Verify node_modules was ignored
        for chunk in chunks:
            assert "node_modules" not in chunk.file_path, "Should not include node_modules files"
        print(f"✓ Ignore directories test passed: Found {len(chunks)} chunk(s), node_modules ignored")

def test_scan_codebase_multiple_files():
    """Test scanning multiple files with progress logging."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create 15 small Python files to trigger progress logging
        for i in range(15):
            file_path = os.path.join(temp_dir, f"file{i}.py")
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(f"def func{i}():\n    return {i}\n")
        
        # Scan the codebase (should log progress at 10 files)
        chunks = scan_codebase(temp_dir)
        
        # Verify all files were processed
        assert len(chunks) >= 15, f"Should find at least 15 chunks, found {len(chunks)}"
        print(f"✓ Multiple files test passed: Found {len(chunks)} chunk(s) from 15 files")

if __name__ == "__main__":
    print("Testing scan_codebase function...\n")
    test_scan_codebase_basic()
    test_scan_codebase_invalid_path()
    test_scan_codebase_with_ignored_dirs()
    test_scan_codebase_multiple_files()
    print("\n✓ All tests passed!")
