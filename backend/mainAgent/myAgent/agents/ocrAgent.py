"""
OCR Agent
Extracts text from PDF pages using multiple methods

Responsibilities:
- Handle digital PDFs (with embedded text)
- Handle scanned PDFs (OCR with Tesseract)
- Automatically detect which method to use
- Clean and return extracted text
"""
import logging
from os import path
import pytesseract
from pdf2image import convert_from_path
import pdfplumber
from typing import Dict, List
from pathlib import Path

logger = logging.getLogger(__name__)

class OCRAgent:
    """
    Agent for extracting text from PDF pages
    
    Simple Explanation:
    - Some PDFs have text already (digital PDFs)
    - Some PDFs are scanned images (need OCR)
    - This agent handles both automatically
    
    Methods Used:
    1. pdfplumber - Fast, for digital PDFs
    2. Tesseract OCR - Slower, for scanned images
    """
    def extract_pages(self, pdf_path: Path) -> dict:
        try:
            logger.info(f"Starting text extraction from: {pdf_path}")
            if not Path(pdf_path).exists():
                logger.error(f"File not found: {pdf_path}")
                return {
                    'success': False,
                    'pages': [],
                    'error': f"File not found: {pdf_path}"
                }
            
            pages_data = []
            with pdfplumber.open(pdf_path) as pdf:
                total_pages = len(pdf.pages)
                logger.info(f"PDF has {total_pages} pages")

                for page_num in range(1, total_pages + 1):
                    try:
                        page = pdf.pages[page_num - 1]
                        
                        # Check if page is empty
                        if self._is_page_empty(page):
                            pages_data.append({
                                'page_number': page_num,
                                'text': '',
                                'confidence': 1.0,
                                'method': 'empty',
                                'is_empty': True
                            })
                            logger.info(f"Page {page_num}: Detected empty page")
                            continue
                            
                        # Try pdfplumber first
                        text = page.extract_text()
                        
                        if text and len(text.strip()) > 0:
                            pages_data.append({
                                'page_number': page_num,
                                'text': text.strip(),
                                'confidence': 0.95,
                                'method': 'pdfplumber',
                                'is_empty': False
                            })
                        else:
                            # Fall back to OCR
                            ocr_result = self.extract_with_ocr(pdf_path, page_num)
                            if ocr_result['success'] and ocr_result['page']['text'].strip():
                                ocr_result['page']['is_empty'] = False
                                pages_data.append(ocr_result['page'])
                            else:
                                pages_data.append({
                                    'page_number': page_num,
                                    'text': '',
                                    'confidence': 0.0,
                                    'method': 'failed',
                                    'is_empty': True,
                                    'error': 'No text could be extracted'
                                })
                                
                    except Exception as e:
                        logger.error(f"Error processing page {page_num}: {str(e)}")
                        pages_data.append({
                            'page_number': page_num,
                            'text': '',
                            'confidence': 0.0,
                            'method': 'error',
                            'is_empty': True,
                            'error': str(e)
                        })
                
                # Check if we have any content at all
                if not any(not page.get('is_empty', True) for page in pages_data):
                    return {
                        'success': False,
                        'pages': pages_data,
                        'error': 'Document appears to be empty or could not be processed'
                    }
                
                return {
                    'success': True,
                    'pages': pages_data,
                    'error': None
                }
                
        except Exception as e:
            logger.error(f"Error extracting text from {pdf_path}: {str(e)}", exc_info=True)
            return {
                'success': False,
                'pages': [],
                'error': str(e)
            }

    def _is_page_empty(self, page) -> bool:
        """
        Check if a PDF page is empty or contains only whitespace/empty graphics.
        
        Args:
            page: pdfplumber page object
            
        Returns:
            bool: True if page is considered empty
        """
        try:
            # Check for text
            text = page.extract_text()
            if text and text.strip():
                return False
                
            # Check for non-white graphics
            if page.images:
                return False
                
            # Check for vector graphics
            if page.curves or page.lines or page.rects or page.rect_edges:
                return False
                
            return True
            
        except Exception as e:
            logger.warning(f"Error checking if page is empty: {str(e)}")
            return False
    def extract_from_single_page(self , pdf_path:Path , page_num:int)->dict:
        """
        Extract text from single page in PDF
        
        Args:
            pdf_path: Full path to PDF file
            page_num: Page number to extract from
        
        Returns:
            {
                'success': True/False,
                'page': {
                    'page_number': 1,
                    'text': 'extracted text...',
                    'confidence': 0.95,
                    'method': 'pdfplumber' or 'ocr'
                },
                'error': None or error message
            }
       
        """
        try:
            logger.info(f"Starting text extraction from: {pdf_path}")
            with pdfplumber.open(pdf_path) as pdf:
                if page_number < 1 or page_number > len(pdf.pages):
                    return {
                        'success': False,
                        'error': f'Invalid page number: {page_number}',
                        'text': ''
                    }
                page = pdf.pages[page_number - 1]
                text = page.extract_text()
                if text:
                    return {
                        'success': True,
                        'page': {
                            'page_number': page_number,
                            'text': text.strip(),
                            'confidence': 0.95,
                            'method': 'pdfplumber'
                        },
                        'error': None
                    }
                else:
                    return {
                        'success': False,
                        'page': {
                            'page_number': page_number,
                            'text': '',
                            'confidence': 0.0,
                            'method': 'pdfplumber'
                        },
                        'error': 'No text found'
                    }
        except Exception as e:
                logger.error(f"Error extracting text from {pdf_path}: {str(e)}")
                return {
                    'success': False,
                    'page': {
                        'page_number': page_number,
                        'text': '',
                        'confidence': 0.0,
                        'method': 'pdfplumber'
                    },
                    'error': str(e)
                }
    def extract_with_ocr(self, pdf_path: Path, page_num: int):
        """
        Extract text using Tesseract OCR
        
        Simple Explanation:
        - Converts PDF page to image
        - Runs OCR on the image
        - Returns extracted text
        
        Use Case: Scanned documents, images of text
        """
        try:
            logger.info(f"Starting OCR extraction from: {pdf_path}")
            images = convert_from_path(pdf_path, first_page=page_num, last_page=page_num, dpi=300)
            if not images:
                return {
                    'success': False,
                    'page': {
                        'page_number': page_num,
                        'text': '',
                        'confidence': 0.0,
                        'method': 'ocr'
                    },
                    'error': 'No image found'
                }
            image = images[0]
            ocr_data = pytesseract.image_to_data(
                image, 
                output_type=pytesseract.Output.DICT,
                lang='eng'  # English language
            )
            text = pytesseract.image_to_string(image,output_type=pytesseract.Output.STRING,lang='eng')
            if text:
                return {
                    'success': True,
                    'page': {
                        'page_number': page_num,
                        'text': text.strip(),
                        'confidence': 0.95,
                        'method': 'ocr'
                    },
                    'error': None
                }
            else:
                return {
                    'success': False,
                    'page': {
                        'page_number': page_num,
                        'text': '',
                        'confidence': 0.0,
                        'method': 'ocr'
                    },
                    'error': 'No text found'
                }
        except Exception as e:
            logger.error(f"Error extracting text from {pdf_path}: {str(e)}")
            return {
                'success': False,
                'page': {
                    'page_number': page_num,
                    'text': '',
                    'confidence': 0.0,
                    'method': 'ocr'
                },
                'error': str(e)
            }
    def detect_page_type(self, pdf_path: Path, page_num: int)->str:
        """
        Detect type of page in PDF
        
        Args:
            pdf_path: Full path to PDF file
            page_num: Page number to detect type of
        
        Returns:
            'digital' or 'scanned' or 'unknown'
        """
        try:
            logger.info(f"Detecting page type from: {pdf_path}")
            
            with pdfplumber.open(pdf_path) as pdf:
                page = pdf.pages[page_number - 1]
                text = page.extract_text()
                
                if not text or len(text.strip()) < 50:
                    return 'scanned'
                elif len(text.strip()) > 500:
                    return 'digital'
                else:
                    return 'mixed'
                    
        except Exception as e:
            logger.error(f"Error detecting page type: {str(e)}")
            return 'unknown'
        
