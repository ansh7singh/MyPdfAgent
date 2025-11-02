// src/components/FileUpload.jsx
import React, { useCallback } from 'react';
import { Upload, X, FileText } from 'lucide-react';

const FileUpload = ({ onFileUpload }) => {
  const [selectedFile, setSelectedFile] = React.useState(null);
  const [error, setError] = React.useState('');

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file && file.type === 'application/pdf') {
      setSelectedFile(file);
      setError('');
    } else {
      setError('Please select a valid PDF file');
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (selectedFile) {
      onFileUpload(selectedFile);
    }
  };

  return (
    <div className="space-y-4">
      <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center">
        <input
          type="file"
          id="file-upload"
          accept="application/pdf"
          onChange={handleFileChange}
          className="hidden"
        />
        <label
          htmlFor="file-upload"
          className="cursor-pointer flex flex-col items-center"
        >
          <Upload className="h-10 w-10 text-gray-400 mb-3" />
          <p className="text-sm text-gray-600">
            {selectedFile 
              ? selectedFile.name 
              : 'Click to select a PDF file or drag and drop it here'}
          </p>
          <p className="mt-1 text-xs text-gray-500">
            {selectedFile 
              ? `${(selectedFile.size / 1024 / 1024).toFixed(2)} MB` 
              : 'Supports: PDF (Max: 50MB)'}
          </p>
        </label>
      </div>
      
      {error && (
        <div className="text-sm text-red-600 bg-red-50 p-3 rounded-md">
          {error}
        </div>
      )}

      {selectedFile && (
        <button
          onClick={handleSubmit}
          className="w-full bg-indigo-600 text-white py-2 px-4 rounded-md hover:bg-indigo-700 transition-colors"
        >
          Upload and Process
        </button>
      )}
    </div>
  );
};

export default FileUpload;