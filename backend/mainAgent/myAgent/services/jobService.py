import logging
from datetime import datetime
from django.conf import settings
import os
import json

logger = logging.getLogger(__name__)

class JobService:
    """
    Service to manage job status and logs for PDF processing
    """
    LOGS_DIR = os.path.join(settings.MEDIA_ROOT, 'job_logs')
    
    def __init__(self):
        # Create logs directory if it doesn't exist
        os.makedirs(self.LOGS_DIR, exist_ok=True)
    
    def _get_job_path(self, job_id):
        """Get path to job's log file"""
        return os.path.join(self.LOGS_DIR, f"{job_id}.json")
    
    def create_job(self, job_id, initial_status="pending"):
        """Initialize a new job with status and timestamp"""
        job_data = {
            'id': job_id,
            'status': initial_status,
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat(),
            'progress': 0,
            'logs': [],
            'result': None,
            'error': None
        }
        
        job_path = self._get_job_path(job_id)
        with open(job_path, 'w') as f:
            json.dump(job_data, f, indent=2)
        
        return job_data
    
    def update_job_status(self, job_id, status, progress=None, log_message=None, result=None, error=None):
        """Update job status and add log message if provided"""
        job_path = self._get_job_path(job_id)
        
        try:
            # Read existing job data
            if os.path.exists(job_path):
                with open(job_path, 'r') as f:
                    job_data = json.load(f)
            else:
                job_data = self.create_job(job_id, status)
            
            # Update fields
            job_data['status'] = status
            job_data['updated_at'] = datetime.utcnow().isoformat()
            
            if progress is not None:
                job_data['progress'] = min(100, max(0, progress))  # Ensure 0-100 range
            
            if log_message:
                log_entry = {
                    'timestamp': datetime.utcnow().isoformat(),
                    'message': log_message,
                    'level': 'info'
                }
                job_data['logs'].append(log_entry)
            
            if result is not None:
                job_data['result'] = result
            
            if error is not None:
                job_data['error'] = str(error)
            
            # Save updated data
            with open(job_path, 'w') as f:
                json.dump(job_data, f, indent=2)
            
            return job_data
            
        except Exception as e:
            logger.error(f"Error updating job {job_id}: {str(e)}")
            raise
    
    def get_job_status(self, job_id):
        """Get current job status and progress"""
        job_path = self._get_job_path(job_id)
        
        if not os.path.exists(job_path):
            return None
        
        with open(job_path, 'r') as f:
            return json.load(f)
    
    def get_job_logs(self, job_id):
        """Get detailed logs for a job"""
        job_data = self.get_job_status(job_id)
        if not job_data:
            return None
        
        return {
            'job_id': job_id,
            'logs': job_data.get('logs', []),
            'status': job_data.get('status'),
            'progress': job_data.get('progress', 0)
        }

# Global instance
job_service = JobService()
