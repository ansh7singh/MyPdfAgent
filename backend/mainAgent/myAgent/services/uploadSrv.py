import os
import logging
import uuid
from pathlib import Path
from typing import Dict, List, Any
from django.conf import settings

from ..agents.ocrAgent import OCRAgent
from ..agents.pdfAgent import PDFAgent
from ..agents.pageOrderingAgent import PageOrderingAgent
# Note: ReconstructionAgent removed - not needed for page reordering pipeline

logger = logging.getLogger(__name__)


class UploadService:
    def __init__(self):
        """Initialize all agents and directories."""
        try:
            self.ocr_agent = OCRAgent()
            self.pdf_agent = PDFAgent()
            self.page_ordering_agent = PageOrderingAgent()  # For determining correct page order
            # ReconstructionAgent removed - not needed for page reordering pipeline

            self.upload_dir = Path(settings.MEDIA_ROOT) / "uploads"
            self.output_dir = Path(settings.MEDIA_ROOT) / "processed"
            self.upload_dir.mkdir(parents=True, exist_ok=True)
            self.output_dir.mkdir(parents=True, exist_ok=True)

            logger.info("✅ UploadService initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize UploadService: {str(e)}", exc_info=True)
            raise
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
        """
        Process a jumbled PDF file through the complete reconstruction pipeline.
        
        Pipeline Steps:
        1. OCR Extraction - Extract text from each page
        2. Page Ordering - Determine correct page order using AI (embeddings + LLM)
        3. Physical Reordering - Physically reorder PDF pages
        4. Optional: Save metadata for querying
        """
        try:
            logger.info(f"🚀 Starting file processing for job_id: {job_id}")
            # Step 1: OCR extraction - Extract text from each page
            logger.info("🔍 Step 1: Extracting text from PDF pages...")
            ocr_result = self.ocr_agent.extract_pages(Path(file_path))

            if not ocr_result.get("success"):
                error_msg = ocr_result.get("error", "Unknown error during document analysis")
                logger.error(f"Document analysis failed: {error_msg}")
                raise ValueError(f"Document analysis failed: {error_msg}")

            pages = ocr_result.get("pages", [])
            if not pages:
                raise ValueError("No pages found in the document")

            logger.info(f"✅ Extracted text from {len(pages)} pages")

            # Step 2: Determine correct page order using PageOrderingAgent
            logger.info("🧠 Step 2: Determining correct page order using AI...")
            ordering_result = self.page_ordering_agent.determine_page_order(
                pages=pages,
                original_pdf_path=str(file_path)
            )

            if not ordering_result.get("success"):
                error_msg = ordering_result.get("error", "Failed to determine page order")
                logger.error(f"Page ordering failed: {error_msg}")
                raise ValueError(f"Page ordering failed: {error_msg}")

            ordered_pages = ordering_result.get("ordered_pages", pages)
            page_order = ordering_result.get("page_order", [p['page_number'] for p in pages])
            confidence_scores = ordering_result.get("confidence_scores", [])
            reasoning = ordering_result.get("reasoning", "Ordering completed")
            original_order = ordering_result.get("original_order", [p['page_number'] for p in pages])

            logger.info(f"✅ Page order determined: {page_order}")
            logger.info(f"   Original order: {original_order}")
            logger.info(f"   Reasoning: {reasoning[:200]}...")

            # Step 3: Physically reorder PDF pages
            logger.info("📄 Step 3: Physically reordering PDF pages...")
            
            # Convert page_order (which contains page numbers) to 1-based page numbers for PDF reordering
            # page_order is already in the format we need (1-based page numbers in desired order)
            reorder_result = self.pdf_agent.reorder_pdf_pages(
                input_pdf_path=str(file_path),
                page_order=page_order,  # List of page numbers in correct order
                output_path=str(self.output_dir / f"{job_id}_reordered.pdf"),
                ordered_pages=ordered_pages,  # Pass ordered pages for TOC generation
                add_toc=True  # Enable TOC generation
            )

            if not reorder_result.get("success"):
                error_msg = reorder_result.get("error", "Failed to reorder PDF pages")
                logger.error(f"PDF reordering failed: {error_msg}")
                raise ValueError(f"PDF reordering failed: {error_msg}")

            reordered_pdf_path = reorder_result.get("file_path")
            logger.info(f"✅ PDF pages reordered successfully: {reordered_pdf_path}")

            # Step 4: Save page metadata for querying (optional)
            logger.info("💾 Step 4: Saving page metadata for querying...")
            
            # Convert numpy types to Python native types for JSON serialization
            def convert_to_native(obj):
                """Convert numpy types to Python native types."""
                import numpy as np
                if isinstance(obj, np.integer):
                    return int(obj)
                elif isinstance(obj, np.floating):
                    return float(obj)
                elif isinstance(obj, np.ndarray):
                    return obj.tolist()
                elif isinstance(obj, dict):
                    return {key: convert_to_native(value) for key, value in obj.items()}
                elif isinstance(obj, list):
                    return [convert_to_native(item) for item in obj]
                return obj
            
            # Convert confidence_scores to Python floats
            confidence_scores_python = [float(score) for score in confidence_scores]
            
            metadata = {
                "job_id": job_id,
                "original_file": str(file_path),
                "reordered_file": reordered_pdf_path,
                "original_order": original_order,
                "reordered_order": page_order,
                "confidence_scores": confidence_scores_python,
                "reasoning": reasoning,
                "pages": [
                    {
                        "page_number": p.get('page_number'),
                        "original_index": p.get('original_index', p.get('page_number') - 1),
                        "text": p.get('text', '')[:500],  # First 500 chars for preview
                        "is_empty": p.get('is_empty', False),
                        "confidence": float(confidence_scores_python[i]) if i < len(confidence_scores_python) else 0.5
                    }
                    for i, p in enumerate(ordered_pages)
                ]
            }
            
            # Convert any remaining numpy types in metadata
            metadata = convert_to_native(metadata)

            metadata_file_path = self.output_dir / f"{job_id}_metadata.json"
            try:
                import json
                with open(metadata_file_path, 'w', encoding='utf-8') as f:
                    json.dump(metadata, f, ensure_ascii=False, indent=2)
                logger.info(f"✅ Saved metadata to {metadata_file_path}")
            except Exception as e:
                logger.error(f"Error saving metadata: {str(e)}", exc_info=True)
                # Don't fail the whole process if we can't save metadata

            # Step 5: Create summary
            summary = self._generate_page_ordering_summary(
                original_order=original_order,
                reordered_order=page_order,
                confidence_scores=confidence_scores_python,
                reasoning=reasoning
            )

            return {
                "success": True,
                "ocr_result": ocr_result,
                "ordering_result": {
                    "success": True,
                    "original_order": original_order,
                    "reordered_order": page_order,
                    "confidence_scores": confidence_scores,
                    "reasoning": reasoning,
                    "average_confidence": sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.0
                },
                "pdf_result": reorder_result,
                "summary": summary,
                "metadata_file": metadata_file_path.name if metadata_file_path.exists() else None,
                "reordered_pdf_filename": Path(reordered_pdf_path).name
            }

        except ValueError as e:
            # These are expected errors with clear messages
            logger.error(f"ValueError in processing file {file_path}: {str(e)}", exc_info=True)
            raise
        except Exception as e:
            # Unexpected errors - log full traceback
            error_msg = f"Unexpected error processing file {file_path}: {str(e)}"
            logger.error(error_msg, exc_info=True)
            # Re-raise with more context
            raise Exception(f"Processing failed: {str(e)}. Check server logs for details.")

    # ----------------------------------------------------------------
    def _generate_page_ordering_summary(
        self,
        original_order: List[int],
        reordered_order: List[int],
        confidence_scores: List[float],
        reasoning: str
    ) -> str:
        """Generate a summary of the page ordering process."""
        try:
            if not original_order or not reordered_order:
                return "Page ordering completed"
            
            # Check if order changed
            order_changed = original_order != reordered_order
            
            if not order_changed:
                summary = "✅ Pages were already in correct order. No reordering needed."
            else:
                avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.0
                summary = (
                    f"✅ Pages reordered successfully.\n"
                    f"   Original order: {original_order}\n"
                    f"   New order: {reordered_order}\n"
                    f"   Average confidence: {avg_confidence:.2%}\n"
                    f"   Reasoning: {reasoning[:200]}..."
                )
            
            return summary

        except Exception as e:
            logger.error(f"Error generating summary: {str(e)}", exc_info=True)
            return "Page ordering completed"
