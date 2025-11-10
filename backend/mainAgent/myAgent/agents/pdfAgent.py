import os
import logging
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union, Any
from fpdf import FPDF
from datetime import datetime
from PyPDF2 import PdfMerger, PdfReader, PdfWriter
import tempfile

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
    
    def _detect_headings(self, pages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Detect headings and sections from ordered pages to generate TOC.
        
        Args:
            pages: List of page dictionaries with 'text' and 'page_number'
            
        Returns:
            List of TOC entries with title, level, and page number
        """
        toc_entries = []
        heading_patterns = [
            # Level 1: Main titles (LOAN AGREEMENT, ARTICLE I, etc.)
            (r'^(?:LOAN AGREEMENT|ARTICLE\s+[IVXLCDM]+|PART\s+[IVXLCDM]+|CHAPTER\s+\d+|SECTION\s+\d+)[\s:\.]*(.+)?$', 1),
            # Level 2: Major sections (DEFINITIONS, TERMS AND CONDITIONS, etc.)
            (r'^(?:DEFINITIONS|TERMS|CONDITIONS|GENERAL|SPECIFIC|APPENDIX|SCHEDULE)[\s:\.]*(.+)?$', 1),
            (r'^([A-Z][A-Z\s]{3,50}?)[\s:\.]+$', 2),  # All caps headings
            # Level 3: Subsections (numbered items)
            (r'^\d+[\.\)]\s+([A-Z][^\n]{5,80})$', 3),
            (r'^[a-z]\)\s+([A-Z][^\n]{5,80})$', 3),
        ]
        
        for idx, page in enumerate(pages):
            text = page.get('text', '')
            # Use position in reordered PDF (1-based), not original page number
            page_position = idx + 1
            
            if not text:
                continue
                
            lines = text.split('\n')
            for line in lines[:20]:  # Check first 20 lines of each page
                line = line.strip()
                if len(line) < 5 or len(line) > 100:
                    continue
                    
                # Check each pattern
                for pattern, level in heading_patterns:
                    match = re.match(pattern, line, re.IGNORECASE)
                    if match:
                        title = match.group(1).strip() if match.groups() and match.group(1) else line.strip()
                        # Clean up title
                        title = re.sub(r'\s+', ' ', title)
                        if len(title) > 80:
                            title = title[:77] + '...'
                        
                        # Avoid duplicates
                        if not any(entry['title'].lower() == title.lower() and entry['page'] == page_position 
                                  for entry in toc_entries):
                            toc_entries.append({
                                'title': title,
                                'level': level,
                                'page': page_position  # Position in reordered PDF
                            })
                        break
        
        return toc_entries
    
    def _create_toc_pdf(self, toc_entries: List[Dict[str, Any]], output_path: str) -> bool:
        """
        Create a PDF page with table of contents.
        
        Args:
            toc_entries: List of TOC entries
            output_path: Path to save the TOC PDF
            
        Returns:
            True if successful, False otherwise
        """
        try:
            pdf = FPDF()
            pdf.set_auto_page_break(auto=True, margin=15)
            pdf.add_page()
            
            # Title
            self._set_font(pdf, 'title')
            pdf.cell(0, 20, 'Table of Contents', 0, 1, 'C')
            pdf.ln(10)
            
            # TOC entries
            self._set_font(pdf, 'normal')
            for entry in toc_entries:
                title = self._clean_text(entry.get('title', 'Untitled'))
                page_num = entry.get('page', 1)
                level = entry.get('level', 1)
                
                # Adjust page number: TOC is page 1, so content pages start at page 2
                # The page_num from entry is the position in reordered content (1-based)
                # We need to add 1 because TOC page comes before it
                adjusted_page_num = page_num + 1
                
                # Indentation based on level
                indent = (level - 1) * 10
                pdf.set_x(10 + indent)
                
                # Title
                title_width = 160 - indent
                pdf.cell(title_width, 8, title, 0, 0, 'L')
                
                # Page number
                pdf.set_x(170)
                pdf.cell(20, 8, str(adjusted_page_num), 0, 1, 'R')
                pdf.ln(2)
            
            # Save
            pdf.output(output_path)
            return True
        except Exception as e:
            logger.error(f"Error creating TOC PDF: {e}", exc_info=True)
            return False
    
    def reorder_pdf_pages(
        self,
        input_pdf_path: str,
        page_order: List[int],
        output_path: Optional[str] = None,
        ordered_pages: Optional[List[Dict[str, Any]]] = None,
        add_toc: bool = True
    ) -> Dict[str, Any]:
        """
        Reorder pages in a PDF file according to the specified order.
        
        Args:
            input_pdf_path: Path to the input PDF file
            page_order: List of page numbers (1-based) in the desired order
                       Example: [3, 1, 2] means page 3 comes first, then page 1, then page 2
            output_path: Path to save the reordered PDF (default: auto-generated)
            ordered_pages: Optional list of page dictionaries with text for TOC generation
            add_toc: Whether to add a table of contents page
            
        Returns:
            Dictionary with:
                - success: Whether reordering succeeded
                - file_path: Path to the reordered PDF
                - page_count: Number of pages in the reordered PDF
                - original_order: Original page order
                - new_order: New page order
                - toc_entries: List of TOC entries if TOC was generated
        """
        try:
            if not os.path.exists(input_pdf_path):
                return {
                    'success': False,
                    'error': f'Input PDF not found: {input_pdf_path}'
                }
            
            # Read the input PDF
            reader = PdfReader(input_pdf_path)
            total_pages = len(reader.pages)
            
            # Validate page order
            if not page_order:
                return {
                    'success': False,
                    'error': 'Page order is empty'
                }
            
            # Validate that all page numbers are valid (1-based)
            if not all(1 <= page_num <= total_pages for page_num in page_order):
                return {
                    'success': False,
                    'error': f'Invalid page numbers in order. PDF has {total_pages} pages, but order contains pages outside this range.'
                }
            
            # Validate that all pages are included
            if len(set(page_order)) != total_pages:
                return {
                    'success': False,
                    'error': f'Page order must include all {total_pages} pages exactly once'
                }
            
            # Create a writer to build the reordered PDF
            writer = PdfWriter()
            
            # Add pages in the specified order (convert to 0-based indexing)
            for page_num in page_order:
                page_index = page_num - 1  # Convert to 0-based
                writer.add_page(reader.pages[page_index])
            
            # Generate output path if not provided
            if not output_path:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                base_name = os.path.splitext(os.path.basename(input_pdf_path))[0]
                output_path = str(self.output_dir / f"{base_name}_reordered_{timestamp}.pdf")
            
            # Ensure the output directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Write the reordered PDF temporarily
            temp_output = output_path + '.temp'
            with open(temp_output, 'wb') as output_file:
                writer.write(output_file)
            
            # Generate and add TOC if requested and ordered_pages provided
            toc_entries = []
            if add_toc and ordered_pages:
                try:
                    logger.info("📑 Generating table of contents...")
                    toc_entries = self._detect_headings(ordered_pages)
                    
                    if toc_entries:
                        # Create TOC PDF page
                        toc_pdf_path = temp_output + '_toc.pdf'
                        if self._create_toc_pdf(toc_entries, toc_pdf_path):
                            # Merge TOC page with reordered PDF
                            merger = PdfMerger()
                            merger.append(toc_pdf_path)  # TOC first
                            merger.append(temp_output)    # Then reordered pages
                            merger.write(output_path)
                            merger.close()
                            
                            # Clean up temp files
                            os.remove(temp_output)
                            os.remove(toc_pdf_path)
                            
                            logger.info(f"✅ Added TOC with {len(toc_entries)} entries")
                        else:
                            # TOC generation failed, use reordered PDF without TOC
                            os.rename(temp_output, output_path)
                            logger.warning("⚠️  TOC generation failed, proceeding without TOC")
                    else:
                        # No headings detected, use reordered PDF without TOC
                        os.rename(temp_output, output_path)
                        logger.info("ℹ️  No headings detected, proceeding without TOC")
                except Exception as e:
                    logger.warning(f"⚠️  Error adding TOC: {e}, proceeding without TOC")
                    # Use reordered PDF without TOC
                    if os.path.exists(temp_output):
                        os.rename(temp_output, output_path)
            else:
                # No TOC requested, just rename temp file
                os.rename(temp_output, output_path)
            
            logger.info(f"✅ Successfully reordered PDF: {input_pdf_path} -> {output_path}")
            logger.info(f"   Original order: {list(range(1, total_pages + 1))}")
            logger.info(f"   New order: {page_order}")
            
            return {
                'success': True,
                'file_path': output_path,
                'page_count': total_pages + (1 if toc_entries else 0),  # +1 for TOC page
                'original_order': list(range(1, total_pages + 1)),
                'new_order': page_order,
                'toc_entries': toc_entries if toc_entries else None
            }
            
        except Exception as e:
            logger.error(f"Error reordering PDF pages: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }
