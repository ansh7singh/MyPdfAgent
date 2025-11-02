import axios from 'axios';

// Use environment variable or default to local development
const API_BASE = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE,
  timeout: 600000, // 10 minutes timeout for large files
  headers: {
    'Accept': 'application/json',
    'Content-Type': 'application/json',
  },
});

// Request interceptor for adding auth token if needed
api.interceptors.request.use(
  (config) => {
    // Add auth token if available
    const token = localStorage.getItem('authToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for handling common errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      // Handle specific status codes
      switch (error.response.status) {
        case 401:
          // Handle unauthorized
          console.error('Unauthorized access');
          break;
        case 404:
          console.error('Resource not found');
          break;
        case 500:
          console.error('Server error');
          break;
        default:
          console.error('Request failed with status:', error.response.status);
      }
    } else if (error.request) {
      // The request was made but no response was received
      console.error('No response received:', error.request);
    } else {
      // Something happened in setting up the request
      console.error('Request error:', error.message);
    }
    return Promise.reject(error);
  }
);

/**
 * Upload a PDF file for processing
 * @param {File} file - The PDF file to upload
 * @param {Object} options - Additional options
 * @param {Function} onUploadProgress - Progress callback
 * @returns {Promise<Object>} - Upload response
 */
export const uploadPDF = async (file, options = {}, onUploadProgress = null) => {
  const formData = new FormData();
  formData.append('file', file);
  
  // Add any additional options to the form data
  if (options) {
    Object.entries(options).forEach(([key, value]) => {
      formData.append(key, value);
    });
  }
  
  const config = {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
    onUploadProgress: (progressEvent) => {
      if (onUploadProgress && progressEvent.lengthComputable) {
        const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
        onUploadProgress(percentCompleted);
      }
    },
  };
  
  const response = await api.post('/agent/upload', formData, config);
  return response.data;
};

/**
 * Get the status of a processing job
 * @param {string} jobId - The ID of the job to check
 * @returns {Promise<Object>} - Job status and results
 */
export const getJobStatus = async (jobId) => {
  const response = await api.get(`/agent/job/${jobId}/status/`);
  return response.data;
};

/**
 * Download the processed PDF
 * @param {string} jobId - The ID of the job
 * @param {string} filename - Optional custom filename
 * @returns {Promise<void>}
 */
export const downloadResult = async (jobId, filename = 'reconstructed_document.pdf') => {
  try {
    const response = await api.get(`/agent/job/${jobId}/download/`, {
      responseType: 'blob',
    });
    
    // Create blob with explicit PDF type
    const blob = new Blob([response.data], { type: 'application/pdf' });
    
    // Create download link
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    
    // Add to body, click, and cleanup
    document.body.appendChild(link);
    link.click();
    
    // Cleanup after a short delay
    setTimeout(() => {
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    }, 100);
    
    return true;
  } catch (error) {
    console.error('Download failed:', error);
    throw error;
  }
};

/**
 * Get processing logs for a job
 * @param {string} jobId - The ID of the job
 * @returns {Promise<Array>} - Array of log entries
 */
export const getProcessingLogs = async (jobId) => {
  const response = await api.get(`/agent/job/${jobId}/logs/`);
  return response.data.logs || [];
};

/**
 * Get document analysis results
 * @param {string} jobId - The ID of the job
 * @returns {Promise<Object>} - Document analysis data
 */
export const getDocumentAnalysis = async (jobId) => {
  const response = await api.get(`/agent/job/${jobId}/analysis/`);
  return response.data;
};

/**
 * Cancel a running job
 * @param {string} jobId - The ID of the job to cancel
 * @returns {Promise<Object>} - Cancellation response
 */
export const cancelJob = async (jobId) => {
  const response = await api.post(`/agent/job/${jobId}/cancel/`);
  return response.data;
};

/**
 * Delete a job and its associated data
 * @param {string} jobId - The ID of the job to delete
 * @returns {Promise<Object>} - Deletion response
 */
export const deleteJob = async (jobId) => {
  const response = await api.delete(`/agent/job/${jobId}/`);
  return response.data;
};

export default api;
