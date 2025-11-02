import logging
from typing import List, Dict, Any
from .llmAgent import LLMAgent
import json
import re

logger = logging.getLogger(__name__)


class DocumentChunk:
    def __init__(self, chunk_id, content_buffer, source_file, metadata=None):
        self.chunk_id = chunk_id
        self.content_buffer = content_buffer
        self.source_file = source_file
        self.metadata = metadata or {}


class ReconstructionAgent:
    def __init__(self):
        """Initialize Reconstruction Agent using Llama3."""
        # ✅ Fixed: removed deprecated model_provider argument
        self.llm_agent = LLMAgent(model="llama3:latest")
        logger.info("✅ ReconstructionAgent initialized with Llama3 model")

    def create_chunks_from_text(self, text: str, chunk_size: int = 800, overlap: int = 100) -> List[str]:
        """Split text into overlapping chunks for processing."""
        chunks = []
        for i in range(0, len(text), chunk_size - overlap):
            chunk = text[i:i + chunk_size]
            chunks.append(chunk)
        return chunks

    def process_document(self, document_chunks: List[DocumentChunk]) -> Dict[str, Any]:
        """Reconstruct document order logically using Llama3."""
        try:
            all_content = "\n\n".join([c.content_buffer[0] for c in document_chunks])
            logger.info(f"🧠 Processing {len(document_chunks)} chunks with Llama3")

            prompt = (
                "You are an AI document reconstruction assistant.\n"
                "The following text pieces are from a shuffled PDF document.\n"
                "Your job is to reorder them logically and return structured sections.\n"
                "Output format (strictly JSON):\n"
                "{\n"
                "  \"chunks\": [\n"
                "    {\"heading_buffer\": [\"<title or topic>\"], \"content_buffer\": [\"<cleaned text>\"]}\n"
                "  ]\n"
                "}\n\n"
                f"Document text:\n{all_content}"
            )

            # Generate response using the query method
            result = self.llm_agent.query(user_prompt=prompt)
            
            if not result.get("success", False):
                raise ValueError(f"LLM query failed: {result.get('error', 'Unknown error')}")
                
            response = result.get("result", "")

            # Try parsing as JSON safely
            match = re.search(r'\{.*\}', response, re.DOTALL)
            if match:
                clean_json = match.group(0)
                data = json.loads(clean_json)
                chunks = data.get("chunks", [])
            else:
                # fallback: wrap LLM text as a single chunk
                chunks = [{"heading_buffer": ["Reconstructed Document"], "content_buffer": [response]}]

            logger.info(f"✅ LLM reconstructed {len(chunks)} sections")
            return {
                "success": True,
                "reconstructed_doc": {
                    "chunks": chunks,
                    "duplicates": [],
                    "total_chunks": len(chunks),
                    "duplicate_count": 0,
                    "error_count": 0
                },
                "errors": []
            }

        except Exception as e:
            logger.error(f"Error reconstructing document: {e}", exc_info=True)
            return {
                "success": False,
                "reconstructed_doc": {"chunks": []},
                "errors": [str(e)]
            }
