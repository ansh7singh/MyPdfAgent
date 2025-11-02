import os
import logging
import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Optional
import faiss
from sentence_transformers import SentenceTransformer
import pickle

logger = logging.getLogger(__name__)

class EmbeddingsAgent:
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        """
        Initialize the Embeddings Agent
        
        Args:
            model_name: Name of the sentence transformer model to use
        """
        self.model = SentenceTransformer(model_name)
        self.embeddings_index = None
        self.documents = []
        self.index_path = Path('data/embeddings_index.faiss')
        self.documents_path = Path('data/documents.pkl')
        
        # Create data directory if it doesn't exist
        os.makedirs('data', exist_ok=True)
        
    def _load_index(self) -> bool:
        """Load existing FAISS index if available"""
        if self.index_path.exists() and self.documents_path.exists():
            try:
                self.embeddings_index = faiss.read_index(str(self.index_path))
                with open(self.documents_path, 'rb') as f:
                    self.documents = pickle.load(f)
                return True
            except Exception as e:
                logger.error(f"Error loading index: {str(e)}")
                return False
        return False
    
    def _save_index(self):
        """Save the current index and documents to disk"""
        if self.embeddings_index is not None:
            faiss.write_index(self.embeddings_index, str(self.index_path))
            with open(self.documents_path, 'wb') as f:
                pickle.dump(self.documents, f)
    
    def create_embeddings(self, texts: List[str], metadata: List[Dict] = None) -> Dict[str, Any]:
        """
        Create embeddings for a list of texts
        
        Args:
            texts: List of text strings to embed
            metadata: Optional list of metadata dictionaries for each text
            
        Returns:
            Dictionary containing the embeddings and metadata
        """
        try:
            # Generate embeddings
            embeddings = self.model.encode(texts, convert_to_numpy=True, show_progress_bar=True)
            
            # Initialize or update FAISS index
            if self.embeddings_index is None:
                self.embeddings_index = faiss.IndexFlatL2(embeddings.shape[1])
                self.documents = []
            
            # Add to documents with metadata
            if metadata is None:
                metadata = [{} for _ in range(len(texts))]
                
            for text, meta in zip(texts, metadata):
                self.documents.append({
                    'text': text,
                    'metadata': meta
                })
            
            # Add embeddings to index
            self.embeddings_index.add(embeddings)
            
            # Save the updated index
            self._save_index()
            
            return {
                'success': True,
                'count': len(texts),
                'dimension': embeddings.shape[1],
                'total_documents': len(self.documents)
            }
            
        except Exception as e:
            logger.error(f"Error creating embeddings: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def search_similar(self, query: str, k: int = 5) -> List[Dict]:
        """
        Search for similar documents to the query
        
        Args:
            query: The search query string
            k: Number of results to return
            
        Returns:
            List of similar documents with scores
        """
        try:
            if self.embeddings_index is None or len(self.documents) == 0:
                return []
                
            # Encode the query
            query_embedding = self.model.encode([query], convert_to_numpy=True)
            
            # Search the index
            distances, indices = self.embeddings_index.search(query_embedding, k)
            
            # Get the results
            results = []
            for idx, distance in zip(indices[0], distances[0]):
                if idx < len(self.documents):  # Ensure index is valid
                    doc = self.documents[idx]
                    results.append({
                        'text': doc['text'],
                        'metadata': doc.get('metadata', {}),
                        'score': float(distance)
                    })
            
            return results
            
        except Exception as e:
            logger.error(f"Error in similarity search: {str(e)}")
            return []
    
    def get_document_count(self) -> int:
        """Get the total number of documents in the index"""
        return len(self.documents) if self.documents else 0
