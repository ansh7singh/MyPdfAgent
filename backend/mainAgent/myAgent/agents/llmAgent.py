from typing import Dict, List, Any, Optional
import os
import json
import logging
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class LLMAgent:
    def __init__(
        self, 
        model: str = "llama3",
        temperature: float = 0.0,
        base_url: str = "http://localhost:11434/v1"
    ):
        """Initialize the LLM agent with configuration.
        
        Args:
            model: The Ollama model name to use (e.g., 'llama3')
            temperature: Controls randomness (0.0 to 1.0)
            base_url: Base URL for the Ollama API
        """
        self.model = model
        self.temperature = temperature
        self.client = OpenAI(base_url=base_url, api_key='ollama')
        logger.info(f"Initialized Ollama with model: {model}")


    def query(
        self,
        user_prompt: str,
        system_prompt: str = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Query the Ollama model with the given prompts.
        
        Args:
            user_prompt: The user's input prompt
            system_prompt: Optional system prompt to set the behavior
            **kwargs: Additional arguments to pass to the model
            
        Returns:
            A dictionary containing the response and metadata
        """
        try:
            return self._query_ollama(user_prompt, system_prompt, **kwargs)
                
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Error querying {self.provider.value} LLM: {error_msg}", exc_info=True)
            return {
                'success': False,
                'error': error_msg,
                'model': self.model,
                'provider': self.provider.value
            }


    def _query_ollama(
        self,
        user_prompt: str,
        system_prompt: str = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Query Ollama model."""
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": user_prompt})

            # Remove duplicate temperature if passed in kwargs
            kwargs.pop("temperature", None)

            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,  # Use class-level one
                **kwargs
            )

            return {
                "success": True,
                "result": response.choices[0].message.content,
                "model": self.model,
                "provider": "ollama"
            }

        except Exception as e:
            logger.error(f"Error querying Ollama model: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "model": self.model,
                "provider": "ollama"
            }



    def _process_response(
        self, 
        answer: str, 
        usage: Any
    ) -> Dict[str, Any]:
        """Process the API response into a standardized format."""
        # Try to parse as JSON if possible
        try:
            answer_json = json.loads(answer)
            if isinstance(answer_json, dict):
                answer = answer_json
        except json.JSONDecodeError:
            pass  # Keep as text if not JSON
            
        return {
            'success': True,
            'answer': answer,
            'model': self.model,
            'provider': self.provider.value,
            'usage': {
                'prompt_tokens': getattr(usage, 'prompt_tokens', 0),
                'completion_tokens': getattr(usage, 'completion_tokens', 0),
                'total_tokens': getattr(usage, 'total_tokens', 0)
            }
        }

    def process_chunk(self, chunk: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a single document chunk through the LLM for reconstruction.
        
        Args:
            chunk: Dictionary containing chunk data including:
                - chunk_id: Unique identifier for the chunk
                - heading_buffer: List of headings
                - content_buffer: List of content lines
                - domain: Document domain (e.g., "banking")
                - source_file: Original filename
                - page_hint: Optional page number
                
        Returns:
            Dictionary with the processed chunk and metadata
        """
        # Prepare the system prompt for reconstruction
        system_prompt = """You are a strict document reconstruction assistant. 
        Preserve all text exactly. Output MUST be valid JSON following the schema. 
        Never add extra text or commentary."""
        
        # Prepare the user prompt with chunk data
        user_prompt = f"""Analyze this document chunk and return a JSON object with:
        - chunk_id: The original chunk ID
        - order_index: Estimated position in document (1 = first)
        - confidence: 0.0-1.0 confidence score
        - reason: Brief justification for the order
        - is_duplicate: Boolean indicating if this is a duplicate
        - duplicate_of: chunk_id of duplicate if applicable
        - section_label: Detected section name if any
        - detected_page_number: Extracted page number if found
        - heading_buffer: Original headings (unchanged)
        - content_buffer: Original content (unchanged)
        
        Chunk data:
        {json.dumps(chunk, indent=2)}"""
        
        # Call the LLM with strict JSON response format
        result = self.query(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=0.1,  # Keep it deterministic
            max_tokens=1000
        )
        
        if not result['success']:
            return {
                'success': False,
                'error': result.get('error', 'Unknown error'),
                'chunk_id': chunk.get('chunk_id', 'unknown')
            }
            
        # Ensure the response has all required fields
        response = result['answer']
        if isinstance(response, str):
            try:
                response = json.loads(response)
            except json.JSONDecodeError:
                return {
                    'success': False,
                    'error': 'Invalid JSON response from LLM',
                    'chunk_id': chunk.get('chunk_id', 'unknown'),
                    'raw_response': response
                }
                
        # Validate required fields
        required_fields = [
            'chunk_id', 'order_index', 'confidence', 'reason',
            'is_duplicate', 'section_label', 'detected_page_number',
            'heading_buffer', 'content_buffer'
        ]
        
        if not all(field in response for field in required_fields):
            return {
                'success': False,
                'error': f'Missing required fields in response: {required_fields}',
                'chunk_id': chunk.get('chunk_id', 'unknown'),
                'response': response
            }
            
        return {
            'success': True,
            'result': response
        }