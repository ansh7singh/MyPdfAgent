import os
import logging
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union, Any
from fpdf import FPDF
from datetime import datetime
from PyPDF2 import PdfMerger

# Add DejaVu font path (commonly available on Linux/Unix systems)
DEJAVU_FONT_PATH = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
DEFAULT_FONT = 'DejaVu'  # Will fall back to Arial if DejaVu not available

logger = logging.getLogger(__name__)

class PDFAgent:
    """
    PDF Agent for generating well-formatted PDF documents with TOC and structured content
    """
    def __init__(self, output_dir: str = 'output'):
        """
        Initialize the PDF Agent
        
        Args:
            output_dir: Directory to save generated PDFs
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Default styles
        self.styles = {
            'title': {'size': 24, 'style': 'B'},
            'h1': {'size': 18, 'style': 'B'},
            'h2': {'size': 16, 'style': 'B'},
            'h3': {'size': 14, 'style': 'B'},
            'normal': {'size': 12, 'style': ''},
            'small': {'size': 10, 'style': ''},
            'footer': {'size': 8, 'style': 'I'}
        }
        
        # Initialize font paths
        self.font_available = False
        self._init_fonts()
    
    def _init_fonts(self):
        """Initialize Unicode-compatible fonts."""
        try:
            # Try to add DejaVu font if available
            if os.path.exists(DEJAVU_FONT_PATH):
                self.font_available = True
                self.default_font = 'DejaVu'
                return
                
            # Fall back to Arial (supports many Unicode characters on Windows/macOS)
            self.font_available = True
            self.default_font = 'Arial'
            
        except Exception as e:
            logger.warning(f"Could not initialize Unicode fonts: {e}")
            self.font_available = False
            self.default_font = 'Helvetica'
    
    def _clean_text(self, text: str) -> str:
        """Clean text by removing or replacing problematic characters."""
        if not text or not isinstance(text, str):
            return ""
            
        # Replace common problematic characters
        replacements = {
            '•': '-',      # Bullet point to dash
            '→': '->',     # Right arrow
            '–': '-',      # En dash
            '—': '--',     # Em dash
            '“': '"',      # Left double quote
            '”': '"',      # Right double quote
            '‘': "'",      # Left single quote
            '’': "'",      # Right single quote
            '…': '...',    # Ellipsis
            '–': '-',      # Another type of dash
            '—': '--'      # Another type of em dash
        }
        
        # First, replace known problematic characters
        for old, new in replacements.items():
            text = text.replace(old, new)
            
        # Then remove any remaining non-printable characters
        cleaned_text = []
        for char in text:
            if char.isprintable() or char.isspace():
                # Replace any remaining non-ASCII characters with a safe alternative
                if ord(char) > 127:  # Non-ASCII
                    cleaned_text.append('?')
                else:
                    cleaned_text.append(char)
        
        return ''.join(cleaned_text).strip()
        
    def _set_font(self, pdf, style_name='normal'):
        """Set font with fallback to default if Unicode font not available."""
        style = self.styles.get(style_name, self.styles['normal'])
        
        if self.font_available:
            pdf.set_font(self.default_font, style['style'], style['size'])
        else:
            # Fallback to basic font
            pdf.set_font('Arial', style['style'], style['size'])
    
    def _add_page_number(self, pdf: FPDF):
        """Add page number to the bottom of each page"""
        pdf.set_y(-15)
        self._set_font(pdf, 'footer')
        pdf.cell(0, 10, f'Page {pdf.page_no()}', 0, 0, 'C')
    
    def _add_header(self, pdf: FPDF, title: str):
        """Add a header to each page"""
        self._set_font(pdf, 'h3')
        pdf.cell(0, 10, title, 0, 1, 'L')
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(10)
    
    def _add_toc(self, pdf: FPDF, toc: List[Dict[str, Any]]):
        """Add a table of contents"""
        pdf.add_page()
        self._add_header(pdf, 'Table of Contents')
        
        self._set_font(pdf, 'h1')
        pdf.cell(0, 10, 'Table of Contents', 0, 1, 'C')
        pdf.ln(10)
        
        for item in toc:
            # Add dots between title and page number
            title = item.get('title', 'Untitled Section')
            page_num = str(item.get('page', ''))
            
            # Set indentation based on level
            indent = (item.get('level', 1) - 1) * 10
            pdf.set_x(10 + indent)
            
            # Add title and page number
            pdf.cell(0, 10, title, 0, 0, 'L')
            
            # Add dotted line
            pdf.set_x(180 - indent)
            pdf.cell(0, 10, page_num, 0, 1, 'R')
        
        pdf.add_page()
    
    def _add_section(self, pdf: FPDF, section: Dict[str, Any]):
        """Add a section to the PDF"""
        # Clean and prepare content
        title = self._clean_text(section.get('title', 'Untitled Section'))
        content = self._clean_text(section.get('content', ''))
        
        # Add section title
        level = section.get('level', 1)
        style = self.styles[f'h{min(level, 3)}']
        
        self._set_font(pdf, f'h{min(level, 3)}')
        pdf.cell(0, 10, title, 0, 1, 'L')
        pdf.ln(5)
        
        # Add section content
        self._set_font(pdf, 'normal')
        pdf.multi_cell(0, 8, content)
        pdf.ln(10)
    
    def generate_pdf(
        self,
        content: Union[str, List[Dict[str, Any]]],
        title: str = "Document",
        author: str = "PDF Agent",
        add_toc: bool = True,
        output_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate a PDF document from structured content
        
        Args:
            content: Either a string of content or a list of sections
            title: Document title
            author: Document author
            add_toc: Whether to include a table of contents
            output_path: Path to save the PDF (default: auto-generated)
            
        Returns:
            Dictionary with the path to the generated PDF and metadata
        """
        try:
            # Initialize PDF
            pdf = FPDF()
            pdf.set_auto_page_break(auto=True, margin=15)
            
            # Clean title and author
            clean_title = self._clean_text(title)
            clean_author = self._clean_text(author)
            
            # Set document metadata
            pdf.set_title(clean_title)
            pdf.set_author(clean_author)
            
            # Add cover page
            pdf.add_page()
            self._set_font(pdf, 'title')
            pdf.cell(0, 100, '', 0, 1, 'C')  # Add some space
            pdf.cell(0, 20, clean_title, 0, 1, 'C')
            self._set_font(pdf, 'normal')
            pdf.cell(0, 10, f'Generated on {datetime.now().strftime("%Y-%m-%d")}', 0, 1, 'C')
            
            # Process content
            if isinstance(content, str):
                # Simple text content
                pdf.add_page()
                self._add_header(pdf, clean_title)
                self._set_font(pdf, 'normal')
                pdf.multi_cell(0, 10, self._clean_text(content))
            else:
                # Structured content with sections
                if add_toc and len(content) > 1:
                    self._add_toc(pdf, content)
                
                for section in content:
                    if pdf.will_page_break(20):
                        pdf.add_page()
                    self._add_section(pdf, section)
            
            # Generate output path if not provided
            if not output_path:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{title.replace(' ', '_')}_{timestamp}.pdf"
                output_path = str(self.output_dir / filename)
            
            # Ensure the directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Save the PDF
            pdf.output(output_path)
            
            return {
                'success': True,
                'file_path': output_path,
                'page_count': pdf.page_no(),
                'sections': len(content) if isinstance(content, list) else 1
            }
            
        except Exception as e:
            logger.error(f"Error generating PDF: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def merge_pdfs(self, file_paths: List[str], output_path: str = None) -> Dict[str, Any]:
        """
        Merge multiple PDF files into a single PDF
        
        Args:
            file_paths: List of paths to PDF files to merge
            output_path: Path to save the merged PDF (default: auto-generated)
            
        Returns:
            Dictionary with the path to the merged PDF and metadata
        """
        try:
            if not file_paths:
                return {'success': False, 'error': 'No files to merge'}
            
            # Generate output path if not provided
            if not output_path:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_path = str(self.output_dir / f"merged_{timestamp}.pdf")
            
            # Ensure the output directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Merge PDFs
            merger = PdfMerger()
            
            for pdf_path in file_paths:
                if not os.path.exists(pdf_path):
                    logger.warning(f"File not found: {pdf_path}")
                    continue
                merger.append(pdf_path)
            
            # Save the merged PDF
            merger.write(output_path)
            merger.close()
            
            return {
                'success': True,
                'file_path': output_path,
                'merged_files': len(file_paths)
            }
            
        except Exception as e:
            logger.error(f"Error merging PDFs: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }