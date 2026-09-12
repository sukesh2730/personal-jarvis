"""
Vector storage and semantic search for code chunks.

This module manages ChromaDB vector storage, generates embeddings locally,
and performs semantic search to find relevant code chunks.
"""

from dataclasses import dataclass
from typing import List, Optional
import logging
import chromadb
from sentence_transformers import SentenceTransformer
from indexer import CodeChunk

# Configure logging
logger = logging.getLogger(__name__)


@dataclass
class SearchResult:
    """Result from semantic search with similarity score."""
    content: str          # Code chunk content
    file_path: str       # Source file path
    start_line: int      # Starting line number (1-indexed)
    end_line: int        # Ending line number (1-indexed)
    language: str        # Programming language
    similarity_score: float  # Cosine similarity (0-1)


class CodeMemory:
    """Manages vector storage and semantic search for code chunks."""
    
    def __init__(self, persist_directory: str = "./chroma_db"):
        """
        Initialize or connect to ChromaDB collection.
        
        Args:
            persist_directory: Directory to store ChromaDB data
        """
        # Initialize ChromaDB persistent client
        self.client = chromadb.PersistentClient(path=persist_directory)
        
        # Get or create collection with cosine distance metric
        self.collection = self.client.get_or_create_collection(
            name="code_memory",
            metadata={"hnsw:space": "cosine"}
        )
        
        # Load sentence-transformers model for local embeddings
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
    
    def add_chunks(self, chunks: List[CodeChunk], file_path: str = None) -> int:
        """
        Add or update code chunks in vector store.
        
        Args:
            chunks: List of CodeChunk objects to store
            file_path: If provided, delete existing chunks for this file first
            
        Returns:
            Number of chunks successfully stored
        """
        if not chunks:
            return 0
        
        # Delete existing chunks for this file if file_path provided
        if file_path:
            try:
                self.collection.delete(where={"file_path": file_path})
            except Exception as e:
                logger.warning(f"Failed to delete existing chunks for {file_path}: {e}")
        
        # Process chunks in batches of 100
        batch_size = 100
        total_stored = 0
        
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i + batch_size]
            
            # Generate chunk IDs
            ids = [f"{chunk.file_path}::{chunk.start_line}-{chunk.end_line}" 
                   for chunk in batch]
            
            # Extract content for embeddings
            documents = [chunk.content for chunk in batch]
            
            # Generate embeddings using sentence-transformers
            embeddings = self.model.encode(documents, show_progress_bar=False)
            
            # Prepare metadata
            metadatas = [{
                "file_path": chunk.file_path,
                "start_line": chunk.start_line,
                "end_line": chunk.end_line,
                "language": chunk.language
            } for chunk in batch]
            
            # Store in ChromaDB
            try:
                self.collection.add(
                    ids=ids,
                    documents=documents,
                    embeddings=embeddings.tolist(),
                    metadatas=metadatas
                )
                total_stored += len(batch)
            except Exception as e:
                logger.error(f"Failed to store batch starting at index {i}: {e}")
        
        # Log completion
        logger.info(f"Stored {total_stored} chunks in vector database")
        
        return total_stored
    
    def search(self, query: str, top_k: int = 3) -> List[SearchResult]:
        """
        Semantic search for relevant code chunks.
        
        Args:
            query: Natural language search query
            top_k: Number of results to return (default: 3)
            
        Returns:
            List of SearchResult objects ordered by similarity score (descending)
        """
        # Generate query embedding
        query_embedding = self.model.encode([query], show_progress_bar=False)[0]
        
        # Query ChromaDB collection
        results = self.collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=top_k
        )
        
        # Handle empty results
        if not results['ids'] or not results['ids'][0]:
            logger.info("Found 0 relevant code chunks (similarity > 0.3)")
            return []
        
        # Convert results to SearchResult objects
        search_results = []
        for i in range(len(results['ids'][0])):
            # Extract data from ChromaDB results
            content = results['documents'][0][i]
            metadata = results['metadatas'][0][i]
            distance = results['distances'][0][i]
            
            # Convert distance to similarity score (cosine: similarity = 1 - distance)
            similarity_score = 1.0 - distance
            
            # Filter by similarity threshold
            if similarity_score > 0.3:
                search_results.append(SearchResult(
                    content=content,
                    file_path=metadata['file_path'],
                    start_line=metadata['start_line'],
                    end_line=metadata['end_line'],
                    language=metadata['language'],
                    similarity_score=similarity_score
                ))
        
        # Sort by similarity score descending (already sorted by ChromaDB, but ensure)
        search_results.sort(key=lambda x: x.similarity_score, reverse=True)
        
        # Log results count
        logger.info(f"Found {len(search_results)} relevant code chunks (similarity > 0.3)")
        
        return search_results
