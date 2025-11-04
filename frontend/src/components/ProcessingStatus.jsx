// src/components/ProcessingStatus.jsx
import React, { useEffect, useRef, useState } from 'react';
import { RotateCw, X, AlertCircle, CheckCircle2, Circle } from 'lucide-react';

const ProcessingStatus = ({ jobResult, logs, onCancel, isCancelling }) => {
  const logsEndRef = useRef(null);
  const [currentStep, setCurrentStep] = useState(0);

  const steps = [
    { id: 'upload', label: 'Upload File', icon: CheckCircle2 },
    { id: 'ocr', label: 'Extract Text', icon: RotateCw },
    { id: 'ordering', label: 'Determine Order', icon: RotateCw },
    { id: 'reordering', label: 'Reorder Pages', icon: RotateCw },
    { id: 'complete', label: 'Complete', icon: Circle },
  ];

  useEffect(() => {
    scrollToBottom();
    
    // Determine current step based on logs
    if (logs.some(log => log.message.includes('reordered successfully'))) {
      setCurrentStep(4);
    } else if (logs.some(log => log.message.includes('Physically reordering'))) {
      setCurrentStep(3);
    } else if (logs.some(log => log.message.includes('Determining correct page order'))) {
      setCurrentStep(2);
    } else if (logs.some(log => log.message.includes('Extracting text'))) {
      setCurrentStep(1);
    } else {
      setCurrentStep(0);
    }
  }, [logs]);

  const scrollToBottom = () => {
    logsEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const getStepStatus = (stepIndex) => {
    if (stepIndex < currentStep) return 'completed';
    if (stepIndex === currentStep) return 'active';
    return 'pending';
  };

  const getStepIcon = (stepIndex, Icon) => {
    const status = getStepStatus(stepIndex);
    if (status === 'completed') {
      return <CheckCircle2 className="h-5 w-5 text-green-600" />;
    } else if (status === 'active') {
      return <Icon className="h-5 w-5 text-indigo-600 animate-spin" />;
    } else {
      return <Circle className="h-5 w-5 text-gray-300" />;
    }
  };

  return (
    <div className="space-y-6">
      <div className="text-center">
        <div className="mx-auto flex items-center justify-center h-16 w-16 rounded-full bg-indigo-100 animate-pulse">
          <RotateCw className="h-8 w-8 text-indigo-600 animate-spin" />
        </div>
        <h2 className="mt-4 text-2xl font-bold text-gray-900">Processing Your Document</h2>
        <p className="mt-2 text-gray-600">Reconstructing jumbled PDF pages. This may take a few moments.</p>
      </div>

      {/* Processing Steps */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <h3 className="font-medium text-gray-900 mb-4">Processing Steps</h3>
        <div className="space-y-4">
          {steps.map((step, index) => {
            const status = getStepStatus(index);
            const Icon = step.icon;
            return (
              <div
                key={step.id}
                className={`flex items-center space-x-3 p-3 rounded-lg transition-colors ${
                  status === 'active' ? 'bg-indigo-50 border border-indigo-200' : 
                  status === 'completed' ? 'bg-green-50 border border-green-200' : 
                  'bg-gray-50 border border-gray-200'
                }`}
              >
                {getStepIcon(index, Icon)}
                <span className={`flex-1 font-medium ${
                  status === 'active' ? 'text-indigo-900' : 
                  status === 'completed' ? 'text-green-900' : 
                  'text-gray-500'
                }`}>
                  {step.label}
                </span>
                {status === 'completed' && (
                  <span className="text-xs text-green-600 font-medium">✓ Done</span>
                )}
                {status === 'active' && (
                  <span className="text-xs text-indigo-600 font-medium">In Progress...</span>
                )}
              </div>
            );
          })}
        </div>
      </div>

      <div className="bg-gray-50 p-6 rounded-lg">
        <div className="flex justify-between items-center mb-4">
          <h3 className="font-medium text-gray-900">Processing Logs</h3>
          <span className="text-sm text-gray-500">
            {jobResult?.status === 'processing' ? 'In Progress' : 'Completed'}
          </span>
        </div>

        <div className="bg-white rounded-md border border-gray-200 p-4 h-64 overflow-y-auto text-sm">
          {logs.length > 0 ? (
            <div className="space-y-2">
              {logs.map((log, index) => (
                <div key={index} className="py-1 flex">
                  <span className="text-gray-500 mr-2">[{new Date(log.timestamp).toLocaleTimeString()}]</span>
                  <span className={log.level === 'error' ? 'text-red-600' : 'text-gray-700'}>
                    {log.message}
                  </span>
                </div>
              ))}
              <div ref={logsEndRef} />
            </div>
          ) : (
            <div className="h-full flex items-center justify-center text-gray-500">
              Waiting for processing to begin...
            </div>
          )}
        </div>

        {jobResult?.status === 'processing' && (
          <div className="mt-6 flex justify-center">
            <button
              onClick={onCancel}
              disabled={isCancelling}
              className="px-4 py-2 text-sm font-medium text-red-700 bg-red-100 hover:bg-red-200 rounded-md flex items-center disabled:opacity-50"
            >
              {isCancelling ? (
                <>
                  <RotateCw className="animate-spin h-4 w-4 mr-2" />
                  Cancelling...
                </>
              ) : (
                <>
                  <X className="h-4 w-4 mr-1" />
                  Cancel Processing
                </>
              )}
            </button>
          </div>
        )}

        {(jobResult?.status === 'failed' || jobResult?.error) && (
          <div className="mt-4 p-4 bg-red-50 border border-red-200 text-red-700 rounded-md flex items-start">
            <AlertCircle className="h-5 w-5 mr-2 mt-0.5 flex-shrink-0" />
            <div className="flex-1">
              <p className="font-medium">Processing failed</p>
              <p className="text-sm mt-1">
                {jobResult?.error || "An error occurred while processing your document. Please try again or contact support if the issue persists."}
              </p>
              <button
                onClick={() => window.location.reload()}
                className="mt-3 px-4 py-2 text-sm font-medium text-white bg-red-600 hover:bg-red-700 rounded-md transition-colors"
              >
                Try Again
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ProcessingStatus;