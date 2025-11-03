import os
import logging
import uuid
from pathlib import Path
from typing import Dict, List, Any
from django.conf import settings
import PyPDF2
from io import BytesIO

from ..agents.ocrAgent import OCRAgent
from ..agents.pdfAgent import PDFAgent
from ..agents.reconstructionAgent import ReconstructionAgent, DocumentChunk

logger = logging.getLogger(__name__)


class UploadService:
    def __init__(self):
        """Initialize all agents and directories."""
        try:
            self.ocr_agent = OCRAgent()
            self.pdf_agent = PDFAgent()
            self.reconstruction_agent = ReconstructionAgent()  # Uses default llama3 model

            self.upload_dir = Path(settings.MEDIA_ROOT) / "uploads"
            self.output_dir = Path(settings.MEDIA_ROOT) / "processed"
            self.upload_dir.mkdir(parents=True, exist_ok=True)
            self.output_dir.mkdir(parents=True, exist_ok=True)

            logger.info("✅ UploadService initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize UploadService: {str(e)}", exc_info=True)
            raise
    def _extract_text_from_pdf(self, file_path):
        """Extract text from a PDF file."""
        text = ""
        try:
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                for page in reader.pages:
                    text += page.extract_text() + "\n"
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {str(e)}")
            raise
        return text
    def _chunk_text(self, text, chunk_size=1000, overlap=200):
        """Split text into overlapping chunks."""
        chunks = []
        start = 0
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end].strip()
            if chunk:  # Only add non-empty chunks
                chunks.append({
                    "text": chunk,
                    "start": start,
                    "end": end
                })
            start = end - overlap  # Overlap chunks
        return chunks

    def upload_file(self, uploaded_file, job_id: str = None) -> Dict[str, Any]:
        """Main entry point for upload and processing."""
        job_id = job_id or str(uuid.uuid4())
        try:
            file_path = self._save_uploaded_file(uploaded_file, job_id)
            logger.info(f"📄 File uploaded successfully: {file_path}")

            # Process through full pipeline
            result = self._process_file(file_path, job_id)
            return {"success": True, "job_id": job_id, "file_path": str(file_path), "result": result}

        except Exception as e:
            logger.error(f"Error processing file: {str(e)}", exc_info=True)
            return {"success": False, "job_id": job_id, "error": str(e)}

    # ----------------------------------------------------------------
    def _save_uploaded_file(self, uploaded_file, job_id: str) -> Path:
        """Save uploaded file to /uploads directory."""
        try:
            file_ext = Path(uploaded_file.name).suffix.lower()
            if file_ext not in [".pdf", ".jpg", ".jpeg", ".png"]:
                raise ValueError("Unsupported file format. Please upload PDF or image file.")

            file_path = self.upload_dir / f"{job_id}{file_ext}"
            with open(file_path, "wb+") as destination:
                for chunk in uploaded_file.chunks():
                    destination.write(chunk)
            return file_path

        except Exception as e:
            logger.error(f"Error saving uploaded file: {str(e)}", exc_info=True)
            raise

    # ----------------------------------------------------------------
    def _process_file(self, file_path: Path, job_id: str) -> Dict[str, Any]:
        try:
            # Step 1: OCR extraction
            logger.info("🔍 Running document analysis...")
            ocr_result = self.ocr_agent.extract_pages(Path(file_path))

            if not ocr_result.get("success"):
                error_msg = ocr_result.get("error", "Unknown error during document analysis")
                logger.error(f"Document analysis failed: {error_msg}")
                raise ValueError(f"Document analysis failed: {error_msg}")

            pages = ocr_result.get("pages", [])
            if not pages:
                raise ValueError("No pages found in the document")

            # Filter out empty pages for processing, but keep them in the result
            non_empty_pages = [p for p in pages if not p.get('is_empty', False)]
            
            if not non_empty_pages:
                raise ValueError("Document contains no readable content (all pages are empty or could not be processed)")

            # Get text from non-empty pages
            combined_text = " ".join([page.get("text", "") for page in non_empty_pages if page.get("text")])
            
            if not combined_text.strip():
                raise ValueError("No readable text found in the document")

            # Rest of your processing...
            logger.info("🧩 Creating text chunks for reconstruction...")
            text_chunks = self.reconstruction_agent.create_chunks_from_text(
                text=combined_text, chunk_size=800, overlap=100
            )
            logger.info(f"✅ Created {len(text_chunks)} text chunks")

            # Convert to DocumentChunk objects
            document_chunks = [
                DocumentChunk(
                    chunk_id=f"chunk_{i}",
                    content_buffer=[chunk],
                    source_file=str(file_path),
                    metadata={
                        "chunk_index": i,
                        "original_page_numbers": [p['page_number'] for p in non_empty_pages if chunk in p.get('text', '')]
                    }
                )
                for i, chunk in enumerate(text_chunks)
            ]

        # Rest of your processing...
            logger.info(f"✅ Created {len(document_chunks)} document chunks for LLM reconstruction")

            # Step 3: Run LLM reconstruction
            logger.info("🧠 Running LLM reconstruction process...")
            reconstruction_result = self.reconstruction_agent.process_document(document_chunks)
            reconstructed_doc = reconstruction_result.get("reconstructed_doc", {})
            chunks_out = reconstructed_doc.get("chunks", [])

            logger.info(f"✅ Reconstruction complete with {len(chunks_out)} valid chunks")

            # Step 4: Generate reconstructed PDF
            logger.info("🖨️ Generating final PDF file...")
            pdf_result = self._generate_pdf(chunks_out, job_id, pages) 

            # Step 5: Create summary
            summary = self._generate_summary(chunks_out)
            
            # Step 6: Save chunks to JSON file for querying
            chunks_file_path = self.output_dir / f"{job_id}_chunks.json"
            try:
                # Convert DocumentChunk objects to serializable dictionaries
                serializable_chunks = []
                for chunk in chunks_out:
                    if hasattr(chunk, 'to_dict'):  # If it's a DocumentChunk object
                        serializable_chunks.append(chunk.to_dict())
                    elif isinstance(chunk, dict):  # If it's already a dictionary
                        serializable_chunks.append(chunk)
                
                # Save to JSON file
                with open(chunks_file_path, 'w', encoding='utf-8') as f:
                    import json
                    json.dump(serializable_chunks, f, ensure_ascii=False, indent=2)
                logger.info(f"✅ Saved {len(serializable_chunks)} chunks to {chunks_file_path}")
            except Exception as e:
                logger.error(f"Error saving chunks to JSON: {str(e)}", exc_info=True)
                # Don't fail the whole process if we can't save the chunks

            return {
                "ocr_result": ocr_result,
                "reconstruction_result": reconstruction_result,
                "pdf_result": pdf_result,
                "summary": summary,
                "chunks_saved": chunks_file_path.name,
                "chunks_count": len(chunks_out)
            }

        except Exception as e:
            logger.error(f"Error processing file {file_path}: {str(e)}", exc_info=True)
            raise

    # ----------------------------------------------------------------
    def _generate_pdf(self, chunks: List[Dict[str, Any]], job_id: str, all_pages: List[dict]) -> Dict[str, Any]:
        """Generate PDF from reconstructed content, preserving empty pages."""
        try:
            if not chunks:
                raise ValueError("No content available to generate PDF")

            # Reconstruct the document with original page structure
            final_pages = []
            
            # For now, just create one page with all content since we don't have page mapping
            # in the reconstructed chunks
            content_parts = []
            
            for chunk in chunks:
                if isinstance(chunk, dict):
                    # Handle dictionary chunks
                    if 'content_buffer' in chunk and isinstance(chunk['content_buffer'], list):
                        content = '\n'.join([str(item) for item in chunk['content_buffer'] if item])
                        if 'heading_buffer' in chunk and chunk['heading_buffer']:
                            content = f"{' '.join(chunk['heading_buffer'])}\n{content}"
                        content_parts.append(content)
            
            if not content_parts:
                raise ValueError("No valid content found in chunks")
                
            # Create a single content page with all chunks
            final_pages.append({
                'type': 'content',
                'page_number': 1,
                'title': "Reconstructed Document",
                'content': "\n\n".join(content_parts),
                'level': 1
            })

            # Generate PDF
            output_path = self.output_dir / f"{job_id}_reconstructed.pdf"
            result = self.pdf_agent.generate_pdf(
                content=final_pages,
                output_path=str(output_path),
                title="Reconstructed Document"
            )

            if not result.get("success"):
                raise Exception(result.get("error", "PDF generation failed"))

            return {
                "success": True,
                "file_path": str(output_path),
                "page_count": len(final_pages),
                "empty_pages": 0
            }

        except Exception as e:
            logger.error(f"Error generating PDF: {str(e)}", exc_info=True)
            return {"success": False, "error": str(e)}

    # ----------------------------------------------------------------
    def _generate_summary(self, chunks: List[Dict[str, Any]]) -> str:
        """Generate a short summary from reconstructed content."""
        try:
            if not chunks:
                return "No content available for summary"

            # Take the first few reconstructed sections
            text = " ".join([" ".join(chunk.get("content_buffer", [])) for chunk in chunks[:5]])
            if not text.strip():
                return "No meaningful content to summarize"

            # Simple rule-based summary (can later replace with LLM)
            short_summary = text[:1500]
            return short_summary.strip()

        except Exception as e:
            logger.error(f"Error generating summary: {str(e)}", exc_info=True)
            return "Summary generation failed"

    def _save_uploaded_file(self, uploaded_file, job_id: str) -> Path:
        """Save the uploaded file to the upload directory."""
        try:
            file_extension = os.path.splitext(uploaded_file.name)[1].lower()
            if file_extension != '.pdf':
                raise ValueError("Only PDF files are supported")
                
            filename = f"{job_id}{file_extension}"
            file_path = self.upload_dir / filename
            
            # Save the file in chunks to handle large files
            with open(file_path, 'wb+') as destination:
                for chunk in uploaded_file.chunks():
                    destination.write(chunk)
                    
            logger.info(f"File saved to {file_path}")
            return file_path
            
        except Exception as e:
            logger.error(f"Error saving file: {str(e)}", exc_info=True)
            raise
