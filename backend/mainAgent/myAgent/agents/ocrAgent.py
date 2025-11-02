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
    def extract_pages(self , pdf_path:Path)->dict:
        """
        Extract text from all pages in PDF
        
        Args:
            pdf_path: Full path to PDF file
        
        Returns:
            {
                'success': True/False,
                'pages': [
                    {
                        'page_number': 1,
                        'text': 'extracted text...',
                        'confidence': 0.95,
                        'method': 'pdfplumber' or 'ocr'
                    },
                    ...
                ],
                'error': None or error message
            }
        """
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

                for page_num,page in enumerate(pdf.pages,start=1):
                    text = page.extract_text()
                    if text:
                        pages_data.append({
                            'page_number': page_num,
                            'text': text.strip(),
                            'confidence': 0.95,  # High confidence for digital text
                            'method': 'pdfplumber'
                        })
                        logger.debug(f"Page {page_num}: Extracted {len(text)} chars (pdfplumber)")
                    else:
                        logger.info(f"Page {page_num}: No text found (pdfplumber)")
                        pages_data.append({
                            'page_number': page_num,
                            'text': '',
                            'confidence': 0.0,
                            'method': 'pdfplumber'
                        })
                logger.info(f"Successfully extracted text from {len(pages_data)} pages")
            
            return {
                'success': True,
                'pages': pages_data,
                'error': None
            }
        except Exception as e:
            logger.error(f"Error extracting text from {pdf_path}: {str(e)}")
            return {
                'success': False,
                'pages': [],
                'error': str(e)
            }
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
        
