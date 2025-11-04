# PDF Reconstruction Pipeline Documentation

## Overview

This document describes the complete end-to-end pipeline for reconstructing jumbled PDF documents. The pipeline automatically determines the correct page order using AI (semantic embeddings + LLM reasoning) and physically reorders the PDF pages.

## Pipeline Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    User Upload                          │
│              (Jumbled PDF File)                         │
└──────────────────┬─────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────┐
│              Step 1: OCR Extraction                      │
│  - Extract text from each page                          │
│  - Handle both digital and scanned PDFs                 │
│  - Detect empty pages                                    │
│  - Return: List of pages with text content              │
└──────────────────┬─────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────┐
│         Step 2: Page Ordering (AI-Powered)               │
│  - Create semantic embeddings for each page              │
│  - Calculate transition scores between pages              │
│  - Use LLM to determine logical order                   │
│  - Combine embeddings + LLM results                     │
│  - Return: Correct page order                            │
└──────────────────┬─────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────┐
│         Step 3: Physical PDF Reordering                  │
│  - Read original PDF                                     │
│  - Reorder pages according to determined order           │
│  - Save reordered PDF                                    │
│  - Return: Path to reordered PDF                         │
└──────────────────┬─────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────┐
│         Step 4: Metadata & Response                      │
│  - Save page metadata for querying                        │
│  - Generate summary                                      │
│  - Return response with download URL                     │
└─────────────────────────────────────────────────────────┘
```

## Detailed Component Description

### Step 1: OCR Extraction (`OCRAgent`)

**Purpose**: Extract text from each PDF page

**Process**:
1. Try `pdfplumber` first (fast, for digital PDFs)
2. Fall back to `Tesseract OCR` (for scanned images)
3. Detect empty pages
4. Return structured data with text content for each page

**Output Format**:
```python
{
    'success': True,
    'pages': [
        {
            'page_number': 1,
            'text': 'extracted text...',
            'confidence': 0.95,
            'method': 'pdfplumber' or 'ocr',
            'is_empty': False
        },
        ...
    ]
}
```

### Step 2: Page Ordering (`PageOrderingAgent`)

**Purpose**: Determine correct page order using hybrid AI approach

**Process**:

1. **Semantic Embeddings**:
   - Create embeddings for each page text using Sentence Transformers
   - Calculate similarity matrix between all pages
   - Use `all-MiniLM-L6-v2` model (~80MB, fast and accurate)

2. **Transition Scores**:
   - Calculate how well each page flows into the next
   - Combine semantic similarity (60%) + flow patterns (40%)
   - Flow patterns detect: "Article I → Article II", "Introduction → Methodology", etc.

3. **LLM Reasoning**:
   - Use Ollama (Llama3) to understand document structure
   - Analyze page content for logical flow
   - Identify title pages, table of contents, sections
   - Returns ordered page indices

4. **Hybrid Combination**:
   - Combines LLM ordering with embedding-based scores
   - Falls back to embedding-only if LLM fails
   - Uses greedy path-finding algorithm for optimal ordering

**Output Format**:
```python
{
    'success': True,
    'ordered_pages': [...],  # Pages in correct order
    'page_order': [3, 1, 2, 4],  # Page numbers in correct order (1-based)
    'confidence_scores': [0.9, 0.85, 0.92, 0.88],
    'reasoning': 'LLM explanation...',
    'original_order': [1, 2, 3, 4]
}
```

**Key Features**:
- Title page detection (e.g., "LOAN AGREEMENT BETWEEN...")
- Section hierarchy understanding (Article I, II, III...)
- Confidence scoring for each ordering decision
- Fallback mechanisms for robustness

### Step 3: Physical PDF Reordering (`PDFAgent`)

**Purpose**: Physically reorder PDF pages

**Process**:
1. Read original PDF using PyPDF2
2. Validate page order (ensure all pages included, no duplicates)
3. Create new PDF with pages in correct order
4. Save reordered PDF to `processed/` directory

**Output Format**:
```python
{
    'success': True,
    'file_path': '/path/to/reordered.pdf',
    'page_count': 4,
    'original_order': [1, 2, 3, 4],
    'new_order': [3, 1, 2, 4]
}
```

### Step 4: Metadata & Response

**Purpose**: Save metadata and return response

**Process**:
1. Save page metadata to JSON file for querying
2. Generate summary of ordering process
3. Return response with download URL

**Metadata Format**:
```json
{
    "job_id": "uuid",
    "original_file": "/path/to/original.pdf",
    "reordered_file": "/path/to/reordered.pdf",
    "original_order": [1, 2, 3, 4],
    "reordered_order": [3, 1, 2, 4],
    "confidence_scores": [0.9, 0.85, 0.92, 0.88],
    "reasoning": "LLM explanation...",
    "pages": [...]
}
```

## Implementation Details

### File: `uploadSrv.py`

**Class**: `UploadService`

**Key Methods**:

1. **`upload_file(uploaded_file, job_id)`**:
   - Main entry point
   - Saves uploaded file
   - Calls `_process_file()` to run pipeline

2. **`_process_file(file_path, job_id)`**:
   - Orchestrates the complete pipeline
   - Steps:
     1. OCR extraction
     2. Page ordering
     3. Physical reordering
     4. Metadata saving
     5. Summary generation

### Integration Points

1. **OCR Agent** (`OCRAgent`):
   - Called via `self.ocr_agent.extract_pages()`
   - Returns pages with extracted text

2. **Page Ordering Agent** (`PageOrderingAgent`):
   - Called via `self.page_ordering_agent.determine_page_order()`
   - Returns correct page order with confidence scores

3. **PDF Agent** (`PDFAgent`):
   - Called via `self.pdf_agent.reorder_pdf_pages()`
   - Physically reorders PDF pages

## API Response Format

**Success Response**:
```json
{
    "status": "success",
    "success": true,
    "job_id": "uuid",
    "file_path": "/path/to/uploaded/file.pdf",
    "result": {
        "success": true,
        "ocr_result": {...},
        "ordering_result": {
            "success": true,
            "original_order": [1, 2, 3, 4],
            "reordered_order": [3, 1, 2, 4],
            "confidence_scores": [0.9, 0.85, 0.92, 0.88],
            "reasoning": "LLM explanation...",
            "average_confidence": 0.8875
        },
        "pdf_result": {
            "success": true,
            "file_path": "/path/to/reordered.pdf",
            "page_count": 4
        },
        "summary": "Pages reordered successfully...",
        "metadata_file": "uuid_metadata.json",
        "reordered_pdf_filename": "uuid_reordered.pdf"
    },
    "download_url": "/agent/download/uuid_reordered.pdf"
}
```

**Error Response**:
```json
{
    "status": "error",
    "success": false,
    "error": "Error message"
}
```

## Error Handling

The pipeline includes comprehensive error handling at each step:

1. **OCR Extraction Failures**:
   - Returns error if document analysis fails
   - Handles empty documents gracefully
   - Logs errors for debugging

2. **Page Ordering Failures**:
   - Falls back to embedding-only ordering if LLM fails
   - Returns original order if ordering fails completely
   - Logs errors with full context

3. **PDF Reordering Failures**:
   - Validates page order before processing
   - Returns detailed error messages
   - Preserves original file on failure

## Performance Considerations

1. **Embedding Generation**:
   - Fast: ~80MB model, processes pages quickly
   - Cached when possible

2. **LLM Processing**:
   - Uses local Ollama (no network latency)
   - Processes page summaries (not full text)
   - Time: ~2-3 seconds for 25-page PDF

3. **PDF Processing**:
   - Fast: Direct page reordering
   - Preserves formatting and content

**Total Processing Time**: ~2-3 minutes for a typical 25-page PDF

## Usage Example

```python
from myAgent.services.uploadSrv import UploadService

# Initialize service
service = UploadService()

# Process a jumbled PDF
result = service.upload_file(uploaded_file)

if result.get('success'):
    # Access results
    ordering_result = result['result']['ordering_result']
    pdf_path = result['result']['pdf_result']['file_path']
    download_url = result['download_url']
    
    print(f"Original order: {ordering_result['original_order']}")
    print(f"Reordered: {ordering_result['reordered_order']}")
    print(f"Confidence: {ordering_result['average_confidence']:.2%}")
    print(f"Download: {download_url}")
```

## Testing

To test the pipeline:

1. **Upload a jumbled PDF** via the API endpoint `/agent/upload/`
2. **Check the response** for ordering results
3. **Download the reordered PDF** from `/agent/download/<filename>`
4. **Verify the order** matches the expected logical flow

## Future Enhancements

1. **Real-time Processing Updates**: WebSocket for live progress
2. **Batch Processing**: Process multiple PDFs at once
3. **Manual Override**: Allow users to manually adjust page order
4. **Multi-language Support**: OCR for multiple languages
5. **Export Options**: Word, Markdown, HTML formats
6. **History**: Save processed documents and queries
7. **Fine-tuning**: Domain-specific model fine-tuning

## Dependencies

- **OCR**: `pdfplumber`, `pytesseract`, `pdf2image`
- **AI**: `sentence-transformers`, `ollama` (via OpenAI client)
- **PDF**: `PyPDF2`
- **Backend**: Django, Django REST Framework

## Conclusion

This pipeline successfully reconstructs jumbled PDF documents using a hybrid AI approach that combines semantic embeddings with LLM reasoning. The system is production-ready and handles edge cases gracefully while providing detailed feedback to users.

