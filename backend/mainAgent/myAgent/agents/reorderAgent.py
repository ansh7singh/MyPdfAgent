import logging
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import re
import json
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class DocumentSection:
    """Represents a section in the document with its content and metadata"""
    title: str
    content: str
    level: int = 1
    page_number: int = 1
    confidence: float = 1.0

class ReorderAgent:
    def __init__(self, min_section_length: int = 100):
        """
        Initialize the Reorder Agent
        
        Args:
            min_section_length: Minimum length of text to be considered a section
        """
        self.min_section_length = min_section_length
        self.heading_patterns = [
            (r'^#\s+(.+?)\s*$', 1),      # H1: # Title
            (r'^##\s+(.+?)\s*$', 2),     # H2: ## Title
            (r'^###\s+(.+?)\s*$', 3),    # H3: ### Title
            (r'^\d+\.\s+(.+?)\s*$', 2), # Numbered list: 1. Title
            (r'^[A-Z][A-Za-z0-9\s]+[.:]\s*$', 2),  # Title case line ending with : or .
        ]
    
    def detect_sections(self, text: str, page_number: int = 1) -> List[DocumentSection]:
        """
        Split text into logical sections based on headings and structure
        
        Args:
            text: The text to split into sections
            page_number: The page number this text comes from
            
        Returns:
            List of DocumentSection objects
        """
        lines = text.split('\n')
        sections = []
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Check for headings
            heading_found = False
            for pattern, level in self.heading_patterns:
                match = re.match(pattern, line)
                if match:
                    if current_section and len(current_section.content) >= self.min_section_length:
                        sections.append(current_section)
                    
                    title = match.group(1).strip()
                    current_section = DocumentSection(
                        title=title,
                        content=line + '\n',
                        level=level,
                        page_number=page_number,
                        confidence=1.0
                    )
                    heading_found = True
                    break
            
            if not heading_found and current_section:
                current_section.content += line + '\n'
        
        # Add the last section if it exists
        if current_section and len(current_section.content) >= self.min_section_length:
            sections.append(current_section)
        
        return sections
    
    def generate_toc(self, sections: List[DocumentSection]) -> List[Dict[str, Any]]:
        """
        Generate a table of contents from document sections
        
        Args:
            sections: List of DocumentSection objects
            
        Returns:
            List of TOC entries with title, level, and page number
        """
        toc = []
        for i, section in enumerate(sections):
            toc.append({
                'id': f'section-{i+1}',
                'title': section.title,
                'level': section.level,
                'page': section.page_number,
                'confidence': section.confidence
            })
        return toc
    
    def reorder_content(self, text: str, page_number: int = 1) -> Dict[str, Any]:
        """
        Reorder document content and generate TOC
        
        Args:
            text: The text to reorder
            page_number: The page number of the text
            
        Returns:
            Dictionary with reordered content and TOC
        """
        try:
            # Split into sections
            sections = self.detect_sections(text, page_number)
            
            if not sections:
                # If no sections found, treat the whole text as one section
                sections = [DocumentSection(
                    title=f"Page {page_number}",
                    content=text,
                    level=1,
                    page_number=page_number,
                    confidence=0.8
                )]
            
            # Generate TOC
            toc = self.generate_toc(sections)
            
            # Format the reordered content
            reordered_content = '\n\n'.join(
                f"{'#' * section.level} {section.title}\n\n{section.content}"
                for section in sections
            )
            
            return {
                'success': True,
                'toc': toc,
                'section_count': len(sections),
                'reordered_content': reordered_content,
                'sections': [{
                    'title': s.title,
                    'level': s.level,
                    'page': s.page_number,
                    'content_length': len(s.content)
                } for s in sections]
            }
            
        except Exception as e:
            logger.error(f"Error in reorder_content: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'toc': [],
                'section_count': 0,
                'reordered_content': text,
                'sections': []
            }
