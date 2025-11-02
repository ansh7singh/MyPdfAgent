import logging
from rest_framework import views
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

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
    """
    Handle file upload and processing
    """
    try:
        # Check if file is in the request
        if 'file' not in request.FILES:
            return Response({
                'success': False,
                'error': 'No file provided in the request'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        uploaded_file = request.FILES['file']
        srv = UploadService()
        result = srv.upload_file(uploaded_file)  # Pass the file object directly
        return Response(result)
        
    except Exception as e:
        log.error(f"Error in uploadFileview: {str(e)}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@csrf_exempt
def queryDocumentsView(request):
    """
    Handle document queries using LLM
    Expected JSON: {"question": "Your question here"}
    """
    try:
        data = json.loads(request.body)
        question = data.get('question', '').strip()
        
        if not question:
            return Response({
                'response': 'error',
                'error_msg': 'Question is required',
                'error_code': 400,
                'error_dtl': ''
            }, status=status.HTTP_400_BAD_REQUEST)
            
        srv = uploadSrv()
        result = srv.query_documents(question)
        return Response(result)
        
    except json.JSONDecodeError:
        return Response({
            'response': 'error',
            'error_msg': 'Invalid JSON format',
            'error_code': 400,
            'error_dtl': 'The request body must be a valid JSON object with a "question" field.'
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        log.error(f"Error in queryDocumentsView: {str(e)}")
        return Response({
            'response': 'error',
            'error_msg': 'An error occurred while processing your request',
            'error_code': 500,
            'error_dtl': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@csrf_exempt
def download_pdf_view(request, filename):
    """
    Download a generated PDF file
    """
    try:
        # Get the path to the generated PDF
        pdf_path = os.path.join(settings.MEDIA_ROOT, 'generated_pdfs', filename)
        
        # Check if file exists
        if not os.path.exists(pdf_path):
            raise Http404("The requested PDF does not exist")
        
        # Open the file and create a response
        response = FileResponse(open(pdf_path, 'rb'), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
        
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

        