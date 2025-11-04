# myAgent/services/QueryService.py
import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from django.conf import settings
from myAgent.agents.queryAgent import QueryAgent

logger = logging.getLogger(__name__)

class QueryService:
    """
    Service for handling document queries.
    """
    
    def __init__(self):
        self.query_agent = QueryAgent()
        logger.info("✅ QueryService initialized")
    
    def query_document(
        self,
        job_id: str,
        query: str,
        top_k: int = 5,
        similarity_threshold: float = 0.3,
        include_sources: bool = True
    ) -> Dict[str, Any]:
        """
        Query a processed document.
        
        Args:
            job_id: The job ID of the processed document
            query: The user's query
            top_k: Number of similar chunks to retrieve
            similarity_threshold: Minimum similarity score (0-1)
            include_sources: Whether to include source information
            
        Returns:
            Dictionary with query results
        """
        try:
            # Load the processed document chunks
            processed_dir = Path(settings.MEDIA_ROOT) / "processed"
            chunks_path = processed_dir / f"{job_id}_chunks.json"
            
            # Try to load chunks from chunks.json file
            if not chunks_path.exists():
                logger.warning(f"Chunks file not found at {chunks_path}, checking for alternative formats")
                return {
                    "success": False,
                    "error": f"Document not found or not processed yet. Expected file: {chunks_path}",
                    "debug": {
                        "path": str(chunks_path),
                        "exists": chunks_path.exists(),
                        "files_in_processed_dir": [str(f.name) for f in processed_dir.glob('*')] if processed_dir.exists() else "Directory not found"
                    }
                }
            
            with open(chunks_path, 'r', encoding='utf-8') as f:
                raw_chunks = json.load(f)
            
            # Convert chunks to the format expected by QueryAgent
            # The chunks.json might have different formats, so we normalize them
            chunks = []
            for i, chunk in enumerate(raw_chunks):
                if isinstance(chunk, dict):
                    # Check if it's already in the correct format
                    if 'heading_buffer' in chunk and 'content_buffer' in chunk:
                        chunks.append(chunk)
                    elif 'content' in chunk:
                        # Convert from chunks.json format to reconstruction format
                        chunks.append({
                            'heading_buffer': [chunk.get('title', f'Page {chunk.get("page_number", i+1)}')],
                            'content_buffer': [chunk.get('content', '')],
                            'metadata': chunk.get('metadata', {})
                        })
                    elif 'text' in chunk:
                        # Convert from OCR page format
                        chunks.append({
                            'heading_buffer': [f'Page {chunk.get("page_number", i+1)}'],
                            'content_buffer': [chunk.get('text', '')],
                            'metadata': {
                                'page_number': chunk.get('page_number', i+1),
                                'confidence': chunk.get('confidence', 0)
                            }
                        })
            
            if not chunks:
                return {
                    "success": False,
                    "error": "No valid chunks found in the processed document"
                }
            
            # Query the document
            result = self.query_agent.query_document(
                query=query,
                chunks=chunks,
                top_k=top_k,
                similarity_threshold=similarity_threshold,
                include_sources=include_sources
            )
            
            return {
                "success": True,
                "result": result
            }
            
        except Exception as e:
            logger.error(f"Error querying document: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }

# Create a singleton instance
query_service = QueryService()
