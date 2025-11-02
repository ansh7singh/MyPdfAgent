// src/components/ProcessingStatus.jsx
import React, { useEffect, useRef } from 'react';
import { RotateCw, X, AlertCircle } from 'lucide-react';

const ProcessingStatus = ({ jobResult, logs, onCancel, isCancelling }) => {
  const logsEndRef = useRef(null);

  const scrollToBottom = () => {
    logsEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [logs]);

  return (
    <div className="space-y-6">
      <div className="text-center">
        <div className="mx-auto flex items-center justify-center h-16 w-16 rounded-full bg-indigo-100 animate-pulse">
          <RotateCw className="h-8 w-8 text-indigo-600 animate-spin" />
        </div>
        <h2 className="mt-4 text-2xl font-bold text-gray-900">Processing Your Document</h2>
        <p className="mt-2 text-gray-600">This may take a few moments. Please don't close this page.</p>
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

        {jobResult?.status === 'failed' && (
          <div className="mt-4 p-3 bg-red-50 text-red-700 rounded-md flex items-start">
            <AlertCircle className="h-5 w-5 mr-2 mt-0.5 flex-shrink-0" />
            <div>
              <p className="font-medium">Processing failed</p>
              <p className="text-sm mt-1">
                An error occurred while processing your document. Please try again or contact support if the issue persists.
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ProcessingStatus;