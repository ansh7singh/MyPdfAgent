// src/components/ResultsView.jsx
import React from 'react';
import { Download, FileText, Check, Clock, AlertCircle } from 'lucide-react';

const ResultsView = ({ jobResult, logs, onDownload, onStartNew }) => {
  return (
    <div className="text-center">
      <div className="mx-auto flex items-center justify-center h-16 w-16 rounded-full bg-green-100">
        <Check className="h-8 w-8 text-green-600" />
      </div>
      <h2 className="mt-4 text-2xl font-bold text-gray-900">Processing Complete!</h2>
      <p className="mt-2 text-gray-600">
        Your document has been successfully reordered and is ready to download.
      </p>

      <div className="mt-8 bg-gray-50 p-6 rounded-lg text-left">
        <h3 className="font-medium text-gray-900 mb-4">Processing Summary</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
          <div className="flex items-center">
            <FileText className="h-4 w-4 text-gray-500 mr-2" />
            <span>Original file: {jobResult?.original_filename || 'document.pdf'}</span>
          </div>
          <div className="flex items-center">
            <Clock className="h-4 w-4 text-gray-500 mr-2" />
            <span>Processed on: {new Date(jobResult?.created_at).toLocaleString()}</span>
          </div>
        </div>

        {logs.length > 0 && (
          <div className="mt-6">
            <h4 className="text-sm font-medium text-gray-700 mb-2">Processing Logs</h4>
            <div className="bg-white rounded-md border border-gray-200 max-h-40 overflow-y-auto p-3 text-xs">
              {logs.map((log, index) => (
                <div key={index} className="py-1 flex">
                  <span className="text-gray-500 mr-2">[{new Date(log.timestamp).toLocaleTimeString()}]</span>
                  <span className={log.level === 'error' ? 'text-red-600' : 'text-gray-700'}>
                    {log.message}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      <div className="mt-8 flex flex-col sm:flex-row justify-center gap-4">
        <button
          onClick={onStartNew}
          className="px-6 py-3 rounded-md text-indigo-700 bg-indigo-100 hover:bg-indigo-200 transition-colors"
        >
          Process Another Document
        </button>
        <button
          onClick={onDownload}
          className="px-6 py-3 rounded-md text-white bg-indigo-600 hover:bg-indigo-700 transition-colors flex items-center justify-center"
        >
          <Download className="h-5 w-5 mr-2" />
          Download PDF
        </button>
      </div>
    </div>
  );
};

export default ResultsView;