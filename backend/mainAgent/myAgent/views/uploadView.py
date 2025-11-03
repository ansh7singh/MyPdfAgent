import logging
from pathlib import Path
from rest_framework import views
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.http import HttpResponse, FileResponse

from rest_framework.decorators import api_view
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from django.http import FileResponse, Http404, JsonResponse
import json
import os
import uuid
from django.conf import settings

from myAgent.services.uploadSrv import UploadService
from myAgent.services.jobService import job_service

log = logging.getLogger(__name__)

@api_view(['POST'])
@csrf_exempt
def uploadFileview(request):
    try:
        if 'file' not in request.FILES:
            return Response({
                'success': False,
                'error': 'No file provided in the request'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        uploaded_file = request.FILES['file']
        srv = UploadService()
        result = srv.upload_file(uploaded_file)
        
        if result.get('success'):
            # Add empty page information to the response
            pages = result.get('result', {}).get('ocr_result', {}).get('pages', [])
            empty_pages = [p['page_number'] for p in pages if p.get('is_empty', False)]
            if empty_pages:
                result['empty_pages'] = empty_pages
                result['warning'] = f'Document contains {len(empty_pages)} empty page(s)'
        
        return Response(result)
        
    except Exception as e:
        log.error(f"Error in uploadFileview: {str(e)}", exc_info=True)
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@csrf_exempt
def download_pdf_view(request, filename):
    """
    Download a generated PDF file
    
    Args:
        request: Django request object
        filename: Name of the file to download (must end with .pdf)
        
    Returns:
        FileResponse with the PDF or error response
    """
    try:
        # Clean and validate filename
        filename = filename.strip()
        if not filename.lower().endswith('.pdf'):
            raise ValueError("Invalid file type. Only PDF files are supported.")
            
        # Ensure we're not trying to access files outside the processed directory
        if '..' in filename or filename.startswith('/'):
            raise ValueError("Invalid filename")
            
        # Build the full path
        pdf_path = Path(settings.MEDIA_ROOT) / 'processed' / filename
        pdf_path = pdf_path.resolve()  # Get absolute path
        
        # Double-check we're still in the allowed directory
        processed_dir = Path(settings.MEDIA_ROOT) / 'processed'
        if not pdf_path.is_relative_to(processed_dir):
            raise ValueError("Invalid file path")
            
        log.info(f"📂 Attempting to serve PDF: {pdf_path}")
        
        # Check if file exists and is a file
        if not pdf_path.is_file():
            log.error(f"PDF not found: {pdf_path}")
            raise Http404(f"The requested PDF does not exist: {filename}")

        # Use FileResponse to stream the file
        response = FileResponse(
            open(pdf_path, 'rb'),
            content_type='application/pdf',
            as_attachment=True
        )
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        response['Content-Length'] = os.path.getsize(pdf_path)
        
        log.info(f"✅ Successfully served PDF: {filename} ({os.path.getsize(pdf_path)} bytes)")
        return response

    except Http404 as e:
        log.error(str(e))
        return Response({
            'response': 'error',
            'error_msg': 'File not found',
            'error_code': 404,
            'error_dtl': str(e)
        }, status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        log.error(f"Error downloading PDF {filename}: {str(e)}")
        return Response({
            'response': 'error',
            'error_msg': 'Failed to download PDF',
            'error_code': 500,
            'error_dtl': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@csrf_exempt
def job_status_view(request, job_id):
    """
    Get the status and progress of a job
    """
    try:
        job_data = job_service.get_job_status(job_id)
        if not job_data:
            return Response({
                'response': 'error',
                'error_msg': 'Job not found',
                'error_code': 404
            }, status=status.HTTP_404_NOT_FOUND)
        
        return Response({
            'response': 'success',
            'data': {
                'job_id': job_id,
                'status': job_data.get('status'),
                'progress': job_data.get('progress', 0),
                'created_at': job_data.get('created_at'),
                'updated_at': job_data.get('updated_at'),
                'has_result': job_data.get('result') is not None,
                'has_error': job_data.get('error') is not None
            }
        })
        
    except Exception as e:
        log.error(f"Error getting job status {job_id}: {str(e)}")
        return Response({
            'response': 'error',
            'error_msg': 'Failed to get job status',
            'error_code': 500,
            'error_dtl': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@csrf_exempt
def job_logs_view(request, job_id):
    """
    Get detailed logs for a job
    """
    try:
        logs_data = job_service.get_job_logs(job_id)
        if not logs_data:
            return Response({
                'response': 'error',
                'error_msg': 'Job not found',
                'error_code': 404
            }, status=status.HTTP_404_NOT_FOUND)
        
        return Response({
            'response': 'success',
            'data': logs_data
        })
        
    except Exception as e:
        log.error(f"Error getting job logs {job_id}: {str(e)}")
        return Response({
            'response': 'error',
            'error_msg': 'Failed to get job logs',
            'error_code': 500,
            'error_dtl': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        