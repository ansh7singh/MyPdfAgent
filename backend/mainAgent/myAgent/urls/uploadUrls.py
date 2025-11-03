from django.urls import path
from myAgent.views.uploadView import (
    uploadFileview, 
    download_pdf_view, 
    job_status_view, 
    job_logs_view
)

# Define the URL patterns
urlpatterns = [
    # File processing endpoints
    path('upload/', uploadFileview, name='uploadFile'),
    path('download/<str:filename>', download_pdf_view, name='downloadPdf'),
    
    # Job tracking endpoints
    path('api/job/<str:job_id>/status/', job_status_view, name='jobStatus'),
    path('api/job/<str:job_id>/logs/', job_logs_view, name='jobLogs'),
]
