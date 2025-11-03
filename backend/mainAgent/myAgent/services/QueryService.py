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
            processed_path = processed_dir / f"{job_id}_chunks.json"
            
            # Debug: Print the path being checked
            print(f"Looking for chunks at: {processed_path}")
            print(f"Directory contents: {list(processed_dir.glob('*'))}")
            
            if not processed_path.exists():
                return {
                    "success": False,
                    "error": f"Document not found or not processed yet. Expected file: {processed_path}",
                    "debug": {
                        "path": str(processed_path),
                        "exists": processed_path.exists(),
                        "files_in_processed_dir": [str(f) for f in processed_dir.glob('*')] if processed_dir.exists() else "Directory not found"
                    }
                }
            
            with open(processed_path, 'r') as f:
                chunks = json.load(f)
            
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