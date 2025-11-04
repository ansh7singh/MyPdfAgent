# agents/document_processor.py

import re
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)

@dataclass
class DocumentSection:
    """Represents a logical section in the document."""
    title: str
    content: str
    level: int = 1
    page_number: int = 1
    section_type: str = "content"
    confidence: float = 1.0
    metadata: dict = None

    def __post_init__(self):
        self.metadata = self.metadata or {}

class DocumentProcessor:
    def __init__(self):
        self.min_heading_length = 3
        self.max_heading_length = 100
        self.heading_patterns = [
            # Level 1: Main titles
            (r'^(?:[A-Z][A-Z0-9\s]+\s*[:\-–—]?|Chapter\s+\d+[:.]?|Part\s+[IVXLCDM]+[:.]?)\s*$', 1),
            # Level 2: Major sections
            (r'^(?:\d+\.\s+[A-Z][^\n]+|Section\s+\d+[.:]|I\.[A-Z]\.|Appendix\s+[A-Z0-9]+\s*:?)$', 2),
            # Level 3: Subsections
            (r'^(?:\d+\.\d+\.\s+[A-Z]|•\s+[A-Z]|-\s+[A-Z])', 3),
        ]
        
    def is_heading(self, text: str) -> Tuple[bool, int]:
        """Check if text is a heading and return its level."""
        text = text.strip()
        if not (self.min_heading_length <= len(text) <= self.max_heading_length):
            return False, 0
            
        for pattern, level in self.heading_patterns:
            if re.match(pattern, text):
                return True, level
        return False, 0
        
    def process_document(self, pages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Process the entire document with cross-page analysis."""
        document_text = []
        page_offsets = [0]  # Starting positions of each page in the full text
        
        # Combine all pages into a single document with page markers
        for i, page in enumerate(pages, 1):
            if not page.get('is_empty', False) and page.get('text'):
                page_text = f"\n\n--- PAGE {i} ---\n{page['text']}\n"
                document_text.append(page_text)
                page_offsets.append(page_offsets[-1] + len(page_text))
        
        full_text = "".join(document_text)
        
        # Split into paragraphs while preserving page boundaries
        paragraphs = []
        current_page = 1
        for i, para in enumerate(full_text.split('\n\n')):
            para = para.strip()
            if not para:
                continue
                
            # Update current page based on page markers
            if para.startswith('--- PAGE '):
                current_page = int(para.split()[2])
                continue
                
            paragraphs.append({
                'text': para,
                'page': current_page,
                'is_heading': False,
                'level': 0,
                'section_type': 'content'
            })
        
        # Identify headings and their hierarchy
        sections = self._identify_sections(paragraphs)
        
        # Group content under headings
        structured_content = self._structure_content(sections)
        
        return {
            'success': True,
            'sections': structured_content,
            'page_count': len([p for p in pages if not p.get('is_empty', False)])
        }
    
    def _identify_sections(self, paragraphs: List[Dict]) -> List[Dict]:
        """Identify document sections and their hierarchy."""
        sections = []
        current_section = None
        
        for para in paragraphs:
            text = para['text']
            is_heading, level = self.is_heading(text)
            
            if is_heading:
                if current_section:
                    sections.append(current_section)
                current_section = {
                    'title': text,
                    'level': level,
                    'page': para['page'],
                    'content': [],
                    'section_type': self._determine_section_type(text)
                }
            elif current_section:
                current_section['content'].append(text)
            else:
                # Content before any heading
                sections.append({
                    'title': f"Introduction (Page {para['page']})",
                    'level': 1,
                    'page': para['page'],
                    'content': [text],
                    'section_type': 'introduction'
                })
        
        if current_section:
            sections.append(current_section)
            
        return sections
    
    def _structure_content(self, sections: List[Dict]) -> List[Dict]:
        """Organize content into a hierarchical structure."""
        structured = []
        current_level = 1
        
        for i, section in enumerate(sections):
            # Adjust levels to maintain hierarchy
            if i > 0:
                if section['level'] > current_level + 1:
                    section['level'] = current_level + 1
                current_level = section['level']
            
            structured.append({
                'title': section['title'],
                'content': '\n\n'.join(section['content']),
                'level': section['level'],
                'page': section['page'],
                'section_type': section['section_type']
            })
        
        return structured
    
    def _determine_section_type(self, heading: str) -> str:
        """Determine the type of section based on heading text."""
        heading_lower = heading.lower()
        
        section_types = {
            'abstract': ['abstract', 'summary'],
            'introduction': ['introduction', 'background'],
            'methodology': ['method', 'approach', 'experiment'],
            'results': ['result', 'finding', 'analysis'],
            'discussion': ['discussion', 'analysis', 'evaluation'],
            'conclusion': ['conclusion', 'summary', 'final'],
            'references': ['reference', 'bibliography', 'citation'],
            'appendix': ['appendix', 'attachment'],
            'toc': ['table of contents', 'contents']
        }
        
        for section_type, keywords in section_types.items():
            if any(keyword in heading_lower for keyword in keywords):
                return section_type
                
        return 'content'
