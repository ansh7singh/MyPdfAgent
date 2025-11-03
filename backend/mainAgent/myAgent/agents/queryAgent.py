# agents/queryAgent.py
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path
import json
from sentence_transformers import SentenceTransformer
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

from .llmAgent import LLMAgent

logger = logging.getLogger(__name__)


class QueryAgent:
    """
    Agent for querying processed documents using semantic search and LLM.
    """
    
    def __init__(self, embedding_model: str = "all-MiniLM-L6-v2"):
        """
        Initialize Query Agent with embedding model and LLM.
        
        Args:
            embedding_model: Sentence transformer model for embeddings
        """
        try:
            self.embedding_model = SentenceTransformer(embedding_model)
            self.llm_agent = LLMAgent(model="llama3:latest")
            logger.info(f"✅ QueryAgent initialized with {embedding_model}")
        except Exception as e:
            logger.error(f"Failed to initialize QueryAgent: {e}")
            raise
    
    def create_embeddings(self, texts: List[str]) -> np.ndarray:
        """
        Create embeddings for a list of texts.
        
        Args:
            texts: List of text strings
            
        Returns:
            Numpy array of embeddings
        """
        try:
            embeddings = self.embedding_model.encode(texts)
            logger.info(f"Created embeddings for {len(texts)} texts")
            return embeddings
        except Exception as e:
            logger.error(f"Error creating embeddings: {e}")
            raise
    
    def find_similar_chunks(
        self, 
        query: str, 
        chunks: List[Dict[str, Any]], 
        top_k: int = 5,
        similarity_threshold: float = 0.3
    ) -> List[Dict[str, Any]]:
        """
        Find chunks most similar to the query using semantic search.
        
        Args:
            query: User's query string
            chunks: List of document chunks
            top_k: Number of top results to return
            similarity_threshold: Minimum similarity score (0-1)
            
        Returns:
            List of similar chunks with similarity scores
        """
        try:
            if not chunks:
                logger.warning("No chunks provided for similarity search")
                return []
            
            logger.info(f"Searching among {len(chunks)} chunks for query: '{query}'")
            
            # Extract text from chunks
            chunk_texts = []
            for i, chunk in enumerate(chunks):
                heading = " ".join(chunk.get("heading_buffer", []))
                content = " ".join(chunk.get("content_buffer", []))
                combined = f"{heading} {content}".strip()
                chunk_texts.append(combined)
                logger.debug(f"Chunk {i}: heading='{heading}', content_length={len(content)}")
            
            if not any(chunk_texts):
                logger.warning("All chunks are empty")
                return []
            
            # Create embeddings
            logger.info("Creating query embedding...")
            query_embedding = self.create_embeddings([query])
            
            logger.info("Creating chunk embeddings...")
            chunk_embeddings = self.create_embeddings(chunk_texts)
            
            # Calculate similarities
            logger.info("Calculating cosine similarities...")
            similarities = cosine_similarity(query_embedding, chunk_embeddings)[0]
            
            # Log all similarity scores
            for i, score in enumerate(similarities):
                logger.debug(f"Chunk {i} similarity: {score:.4f}")
            
            # Get top k results above threshold
            similar_indices = np.argsort(similarities)[::-1]
            
            results = []
            for idx in similar_indices:
                score = similarities[idx]
                logger.debug(f"Checking chunk {idx}: score={score:.4f}, threshold={similarity_threshold}")
                
                if score >= similarity_threshold and len(results) < top_k:
                    results.append({
                        "chunk": chunks[idx],
                        "similarity_score": float(score),
                        "chunk_index": int(idx)
                    })
                    logger.info(f"✅ Added chunk {idx} with score {score:.4f}")
            
            logger.info(f"Found {len(results)} similar chunks (threshold: {similarity_threshold})")
            
            # If no results found, lower the threshold and try again
            if not results and similarities.max() > 0.0:
                logger.warning(f"No chunks above threshold {similarity_threshold}, using lower threshold")
                new_threshold = max(0.1, similarities.max() * 0.5)
                logger.info(f"Retrying with threshold: {new_threshold:.4f}")
                
                for idx in similar_indices[:top_k]:
                    score = similarities[idx]
                    if score > 0.0:
                        results.append({
                            "chunk": chunks[idx],
                            "similarity_score": float(score),
                            "chunk_index": int(idx)
                        })
                        logger.info(f"✅ Added chunk {idx} with lowered threshold score {score:.4f}")
            
            return results
            
        except Exception as e:
            logger.error(f"Error finding similar chunks: {e}", exc_info=True)
            return []
    
    def generate_answer(
        self, 
        query: str, 
        context_chunks: List[Dict[str, Any]],
        include_sources: bool = True
    ) -> Dict[str, Any]:
        """
        Generate an answer to the query using LLM with context.
        
        Args:
            query: User's query
            context_chunks: Relevant chunks from similarity search
            include_sources: Whether to include source information
            
        Returns:
            Dictionary with answer and metadata
        """
        try:
            if not context_chunks:
                logger.warning("No context chunks provided for answer generation")
                return {
                    "success": False,
                    "answer": "I couldn't find any relevant information in the document to answer your question.",
                    "sources": [],
                    "confidence": 0.0
                }
            
            logger.info(f"Generating answer with {len(context_chunks)} context chunks")
            
            # Build context from chunks
            context_parts = []
            for i, item in enumerate(context_chunks):
                chunk = item["chunk"]
                heading = " ".join(chunk.get("heading_buffer", []))
                content = " ".join(chunk.get("content_buffer", []))
                
                context_parts.append(
                    f"[Section {i+1}: {heading}]\n{content}\n"
                )
            
            context = "\n".join(context_parts)
            logger.debug(f"Context length: {len(context)} characters")
            
            # Create prompt for LLM
            system_prompt = (
                "You are a helpful AI assistant that answers questions based on provided document context. "
                "Only use information from the context provided. If the context doesn't contain enough "
                "information to answer the question, say so clearly. Be concise and accurate."
            )
            
            user_prompt = (
                f"Context from document:\n{context}\n\n"
                f"Question: {query}\n\n"
                "Please provide a clear, concise answer based only on the context above. "
                "If you reference specific information, mention which section it came from."
            )
            
            logger.info("Querying LLM for answer...")
            # Get LLM response
            result = self.llm_agent.query(
                user_prompt=user_prompt,
                system_prompt=system_prompt
            )
            
            if not result.get("success", False):
                logger.error(f"LLM query failed: {result.get('error')}")
                raise ValueError(f"LLM query failed: {result.get('error', 'Unknown error')}")
            
            answer = result.get("result", "")
            logger.info(f"✅ Generated answer: {answer[:100]}...")
            
            # Calculate confidence based on similarity scores
            avg_similarity = np.mean([item["similarity_score"] for item in context_chunks])
            
            # Prepare sources if requested
            sources = []
            if include_sources:
                for item in context_chunks:
                    chunk = item["chunk"]
                    heading = " ".join(chunk.get("heading_buffer", []))
                    content = " ".join(chunk.get("content_buffer", []))
                    snippet = content[:200] + "..." if len(content) > 200 else content
                    
                    sources.append({
                        "heading": heading,
                        "snippet": snippet,
                        "similarity_score": item["similarity_score"]
                    })
            
            return {
                "success": True,
                "answer": answer,
                "sources": sources,
                "confidence": float(avg_similarity),
                "num_sources": len(context_chunks)
            }
            
        except Exception as e:
            logger.error(f"Error generating answer: {e}", exc_info=True)
            return {
                "success": False,
                "answer": f"Error generating answer: {str(e)}",
                "sources": [],
                "confidence": 0.0
            }
    
    def query_document(
        self,
        query: str,
        chunks: List[Dict[str, Any]],
        top_k: int = 5,
        similarity_threshold: float = 0.2,  # Lowered default threshold
        include_sources: bool = True
    ) -> Dict[str, Any]:
        """
        Complete query pipeline: search + generate answer.
        
        Args:
            query: User's question
            chunks: Document chunks to search
            top_k: Number of similar chunks to retrieve
            similarity_threshold: Minimum similarity score
            include_sources: Whether to include source citations
            
        Returns:
            Dictionary with answer and metadata
        """
        try:
            logger.info(f"Starting query pipeline for: '{query}'")
            logger.info(f"Parameters: top_k={top_k}, threshold={similarity_threshold}")
            
            # Find similar chunks
            similar_chunks = self.find_similar_chunks(
                query=query,
                chunks=chunks,
                top_k=top_k,
                similarity_threshold=similarity_threshold
            )
            
            if not similar_chunks:
                logger.warning("No similar chunks found")
            
            # Generate answer
            result = self.generate_answer(
                query=query,
                context_chunks=similar_chunks,
                include_sources=include_sources
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error in query pipeline: {e}", exc_info=True)
            return {
                "success": False,
                "answer": f"Error processing query: {str(e)}",
                "sources": [],
                "confidence": 0.0
            }