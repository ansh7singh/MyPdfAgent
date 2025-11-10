// src/components/FileUpload.jsx
import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { motion } from 'framer-motion';
import { 
  Upload, 
  X, 
  FileText, 
  Sparkles, 
  Brain, 
  FileCheck, 
  Shield, 
  Zap,
  ArrowRight,
  CheckCircle2
} from 'lucide-react';

const FileUpload = ({ onUpload }) => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [error, setError] = useState('');
  const [isDragging, setIsDragging] = useState(false);

  const onDrop = useCallback((acceptedFiles, rejectedFiles) => {
    setIsDragging(false);
    
    if (rejectedFiles.length > 0) {
      setError('Please select a valid PDF file (Max: 50MB)');
      setSelectedFile(null);
      return;
    }

    const file = acceptedFiles[0];
    if (file && file.type === 'application/pdf') {
      if (file.size > 50 * 1024 * 1024) {
        setError('File size exceeds 50MB limit');
        setSelectedFile(null);
        return;
      }
      setSelectedFile(file);
      setError('');
    } else {
      setError('Please select a valid PDF file');
      setSelectedFile(null);
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf']
    },
    maxSize: 50 * 1024 * 1024,
    multiple: false,
    onDragEnter: () => setIsDragging(true),
    onDragLeave: () => setIsDragging(false),
  });

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file && file.type === 'application/pdf') {
      if (file.size > 50 * 1024 * 1024) {
        setError('File size exceeds 50MB limit');
        setSelectedFile(null);
        return;
      }
      setSelectedFile(file);
      setError('');
    } else {
      setError('Please select a valid PDF file');
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (selectedFile) {
      onUpload(selectedFile);
    }
  };

  const removeFile = () => {
    setSelectedFile(null);
    setError('');
  };

  const features = [
    {
      icon: Brain,
      title: 'AI-Powered Ordering',
      description: 'Uses semantic embeddings + LLM to determine correct page order',
      color: 'from-purple-500 to-pink-500'
    },
    {
      icon: FileCheck,
      title: 'OCR Text Extraction',
      description: 'Extracts text from both digital and scanned PDF pages',
      color: 'from-blue-500 to-cyan-500'
    },
    {
      icon: Zap,
      title: 'Physical Reordering',
      description: 'Actually reorders PDF pages, not just text reconstruction',
      color: 'from-orange-500 to-red-500'
    },
    {
      icon: Shield,
      title: '100% Local Processing',
      description: 'Complete privacy - documents never leave your machine',
      color: 'from-green-500 to-emerald-500'
    }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-purple-50 py-12 px-4">
      <div className="max-w-6xl mx-auto">
        {/* Header Section */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="text-center mb-12"
        >
          <div className="flex items-center justify-center gap-3 mb-4">
            <div className="p-3 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-2xl shadow-lg">
              <Sparkles className="h-8 w-8 text-white" />
            </div>
            <h1 className="text-5xl font-bold bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent">
              PDF Reconstruction Agent
            </h1>
          </div>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            Automatically reorder jumbled PDF pages using AI-powered semantic analysis and intelligent page ordering
          </p>
        </motion.div>

        <div className="grid lg:grid-cols-3 gap-8">
          {/* Features Section */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
            className="lg:col-span-1 space-y-4"
          >
            <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center gap-2">
              <Sparkles className="h-6 w-6 text-indigo-600" />
              Key Features
            </h2>
            {features.map((feature, index) => {
              const Icon = feature.icon;
              return (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.4, delay: 0.3 + index * 0.1 }}
                  className="bg-white rounded-xl p-5 shadow-md border border-gray-100 hover:shadow-lg transition-all duration-300 hover:-translate-y-1"
                >
                  <div className={`w-12 h-12 rounded-lg bg-gradient-to-br ${feature.color} flex items-center justify-center mb-3 shadow-md`}>
                    <Icon className="h-6 w-6 text-white" />
                  </div>
                  <h3 className="font-semibold text-gray-900 mb-1">{feature.title}</h3>
                  <p className="text-sm text-gray-600 leading-relaxed">{feature.description}</p>
                </motion.div>
              );
            })}
          </motion.div>

          {/* Upload Section */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5, delay: 0.3 }}
            className="lg:col-span-2"
          >
            <div className="bg-white rounded-2xl shadow-xl border border-gray-100 p-8">
              <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center gap-2">
                <Upload className="h-6 w-6 text-indigo-600" />
                Upload Your PDF
              </h2>

              {/* Dropzone */}
              <div
                {...getRootProps()}
                className={`
                  relative border-2 border-dashed rounded-xl p-12 text-center cursor-pointer
                  transition-all duration-300
                  ${isDragActive || isDragging
                    ? 'border-indigo-500 bg-indigo-50 scale-105'
                    : selectedFile
                    ? 'border-green-400 bg-green-50'
                    : 'border-gray-300 bg-gray-50 hover:border-indigo-400 hover:bg-indigo-50'
                  }
                `}
              >
                <input {...getInputProps()} onChange={handleFileChange} />
                
                {selectedFile ? (
                  <motion.div
                    initial={{ scale: 0.9, opacity: 0 }}
                    animate={{ scale: 1, opacity: 1 }}
                    className="space-y-4"
                  >
                    <div className="flex items-center justify-center">
                      <div className="p-4 bg-green-100 rounded-full">
                        <CheckCircle2 className="h-12 w-12 text-green-600" />
                      </div>
                    </div>
                    <div>
                      <FileText className="h-8 w-8 text-gray-700 mx-auto mb-2" />
                      <p className="text-lg font-semibold text-gray-900 mb-1">
                        {selectedFile.name}
                      </p>
                      <p className="text-sm text-gray-600">
                        {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
                      </p>
                    </div>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        removeFile();
                      }}
                      className="inline-flex items-center gap-2 text-sm text-red-600 hover:text-red-700 font-medium"
                    >
                      <X className="h-4 w-4" />
                      Remove file
                    </button>
                  </motion.div>
                ) : (
                  <div className="space-y-4">
                    <div className="flex items-center justify-center">
                      <div className={`p-4 rounded-full transition-colors ${
                        isDragActive || isDragging ? 'bg-indigo-100' : 'bg-gray-100'
                      }`}>
                        <Upload className={`h-12 w-12 transition-colors ${
                          isDragActive || isDragging ? 'text-indigo-600' : 'text-gray-400'
                        }`} />
                      </div>
                    </div>
                    <div>
                      <p className="text-lg font-semibold text-gray-900 mb-2">
                        {isDragActive || isDragging
                          ? 'Drop your PDF here'
                          : 'Drag & drop your PDF here'}
                      </p>
                      <p className="text-sm text-gray-600 mb-4">
                        or click to browse files
                      </p>
                      <div className="flex items-center justify-center gap-2 text-xs text-gray-500">
                        <FileText className="h-4 w-4" />
                        <span>PDF files only • Max 50MB</span>
                      </div>
                    </div>
                  </div>
                )}
              </div>

              {/* Error Message */}
              {error && (
                <motion.div
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg text-sm text-red-700 flex items-start gap-2"
                >
                  <X className="h-5 w-5 text-red-600 flex-shrink-0 mt-0.5" />
                  <span>{error}</span>
                </motion.div>
              )}

              {/* Upload Button */}
              {selectedFile && (
                <motion.button
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  onClick={handleSubmit}
                  className="w-full mt-6 bg-gradient-to-r from-indigo-600 to-purple-600 text-white py-4 px-6 rounded-xl font-semibold hover:from-indigo-700 hover:to-purple-700 transition-all shadow-lg hover:shadow-xl flex items-center justify-center gap-2 group"
                >
                  <Sparkles className="h-5 w-5 group-hover:rotate-12 transition-transform" />
                  <span>Start Processing</span>
                  <ArrowRight className="h-5 w-5 group-hover:translate-x-1 transition-transform" />
                </motion.button>
              )}

              {/* Info Box */}
              <div className="mt-6 p-4 bg-indigo-50 border border-indigo-200 rounded-lg">
                <p className="text-sm text-indigo-900">
                  <strong>How it works:</strong> Upload your PDF and our AI will automatically extract text, 
                  determine the correct page order using semantic analysis, and physically reorder the pages 
                  to create a properly structured document.
                </p>
              </div>
            </div>
          </motion.div>
        </div>
      </div>
    </div>
  );
};

export default FileUpload;