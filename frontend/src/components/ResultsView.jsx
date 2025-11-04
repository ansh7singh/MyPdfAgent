// src/components/ResultsView.jsx
import React, { useState } from 'react';
import { Download, FileText, Check, Clock, AlertCircle, ChevronDown, ChevronUp, BarChart3, Brain, Search, Send, Loader2 } from 'lucide-react';
import axios from 'axios';

const ResultsView = ({ jobResult, logs, onDownload, onStartNew }) => {
  const [showOrderingDetails, setShowOrderingDetails] = useState(false);
  const [showLogs, setShowLogs] = useState(false);
  const [activeTab, setActiveTab] = useState('download'); // 'download' or 'query'
  
  // Query state
  const [query, setQuery] = useState('');
  const [querying, setQuerying] = useState(false);
  const [queryResult, setQueryResult] = useState(null);
  const [queryError, setQueryError] = useState(null);

  const orderingResult = jobResult?.ordering_result;
  const originalOrder = orderingResult?.original_order || [];
  const reorderedOrder = orderingResult?.reordered_order || [];
  const averageConfidence = orderingResult?.average_confidence || 0;
  const confidenceScores = orderingResult?.confidence_scores || [];
  const reasoning = orderingResult?.reasoning || '';
  const orderChanged = JSON.stringify(originalOrder) !== JSON.stringify(reorderedOrder);
  const jobId = jobResult?.job_id || jobResult?.metadata?.job_id;

  // Handle query submission
  const handleQuery = async (e) => {
    e.preventDefault();
    if (!query.trim() || !jobId) {
      setQueryError('Please enter a question and ensure job ID is available');
      return;
    }

    setQuerying(true);
    setQueryError(null);
    setQueryResult(null);

    try {
      const response = await axios.post(
        'http://127.0.0.1:8000/agent/query/',
        {
          job_id: jobId,
          query: query.trim(),
          top_k: 5,
          similarity_threshold: 0.3,
          include_sources: true
        },
        {
          headers: {
            'Content-Type': 'application/json',
          },
        }
      );

      if (response.data.success) {
        setQueryResult(response.data.result);
      } else {
        setQueryError(response.data.error || 'Query failed');
      }
    } catch (error) {
      console.error('Query error:', error);
      setQueryError(
        error.response?.data?.error || 
        error.message || 
        'Failed to query document. Please try again.'
      );
    } finally {
      setQuerying(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto">
      <div className="text-center">
        <div className="mx-auto flex items-center justify-center h-16 w-16 rounded-full bg-green-100">
          <Check className="h-8 w-8 text-green-600" />
        </div>
        <h2 className="mt-4 text-2xl font-bold text-gray-900">Processing Complete!</h2>
        <p className="mt-2 text-gray-600">
          {orderChanged 
            ? 'Your document has been successfully reordered and is ready to download.'
            : 'Your document was already in the correct order. No changes were needed.'}
        </p>
      </div>

      {/* Ordering Results Card */}
      {orderingResult && (
        <div className="mt-8 bg-white rounded-lg border border-gray-200 p-6 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-2">
              <Brain className="h-5 w-5 text-indigo-600" />
              <h3 className="font-semibold text-gray-900">Page Ordering Results</h3>
            </div>
            <button
              onClick={() => setShowOrderingDetails(!showOrderingDetails)}
              className="text-indigo-600 hover:text-indigo-700 text-sm font-medium flex items-center"
            >
              {showOrderingDetails ? (
                <>
                  Hide Details <ChevronUp className="h-4 w-4 ml-1" />
                </>
              ) : (
                <>
                  Show Details <ChevronDown className="h-4 w-4 ml-1" />
                </>
              )}
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
            <div className="bg-gray-50 p-4 rounded-lg">
              <div className="text-sm text-gray-600 mb-1">Original Order</div>
              <div className="text-lg font-semibold text-gray-900">
                {originalOrder.length > 0 ? `[${originalOrder.join(', ')}]` : 'N/A'}
              </div>
            </div>
            <div className="bg-indigo-50 p-4 rounded-lg">
              <div className="text-sm text-indigo-600 mb-1">Reordered</div>
              <div className="text-lg font-semibold text-indigo-900">
                {reorderedOrder.length > 0 ? `[${reorderedOrder.join(', ')}]` : 'N/A'}
              </div>
            </div>
            <div className="bg-green-50 p-4 rounded-lg">
              <div className="text-sm text-green-600 mb-1">Average Confidence</div>
              <div className="text-lg font-semibold text-green-900">
                {(averageConfidence * 100).toFixed(1)}%
              </div>
            </div>
          </div>

          {showOrderingDetails && (
            <div className="mt-4 space-y-4 border-t pt-4">
              {/* Page Order Visualization */}
              {orderChanged && (
                <div>
                  <h4 className="text-sm font-medium text-gray-700 mb-3 flex items-center">
                    <BarChart3 className="h-4 w-4 mr-2" />
                    Page Order Comparison
                  </h4>
                  <div className="bg-gray-50 p-4 rounded-lg">
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <div className="text-xs text-gray-600 mb-2">Original Order</div>
                        <div className="flex flex-wrap gap-1">
                          {originalOrder.map((pageNum, idx) => (
                            <span
                              key={idx}
                              className="px-2 py-1 bg-gray-200 text-gray-700 rounded text-sm font-medium"
                            >
                              Page {pageNum}
                            </span>
                          ))}
                        </div>
                      </div>
                      <div>
                        <div className="text-xs text-gray-600 mb-2">Reordered</div>
                        <div className="flex flex-wrap gap-1">
                          {reorderedOrder.map((pageNum, idx) => {
                            const originalIdx = originalOrder.indexOf(pageNum);
                            const moved = originalIdx !== idx;
                            return (
                              <span
                                key={idx}
                                className={`px-2 py-1 rounded text-sm font-medium ${
                                  moved
                                    ? 'bg-indigo-100 text-indigo-700 border border-indigo-300'
                                    : 'bg-gray-200 text-gray-700'
                                }`}
                              >
                                Page {pageNum}
                              </span>
                            );
                          })}
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* Confidence Scores */}
              {confidenceScores.length > 0 && (
                <div>
                  <h4 className="text-sm font-medium text-gray-700 mb-3">Confidence Scores</h4>
                  <div className="space-y-2">
                    {reorderedOrder.map((pageNum, idx) => (
                      <div key={idx} className="flex items-center space-x-3">
                        <span className="text-sm text-gray-600 w-20">Page {pageNum}:</span>
                        <div className="flex-1 bg-gray-200 rounded-full h-2">
                          <div
                            className="bg-indigo-600 h-2 rounded-full transition-all"
                            style={{ width: `${(confidenceScores[idx] || 0) * 100}%` }}
                          />
                        </div>
                        <span className="text-sm font-medium text-gray-700 w-16 text-right">
                          {(confidenceScores[idx] || 0) * 100}%
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Reasoning */}
              {reasoning && (
                <div>
                  <h4 className="text-sm font-medium text-gray-700 mb-2">AI Reasoning</h4>
                  <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                    <p className="text-sm text-gray-700 leading-relaxed">{reasoning}</p>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* Processing Summary */}
      <div className="mt-6 bg-gray-50 p-6 rounded-lg text-left">
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
          {orderingResult && (
            <>
              <div className="flex items-center">
                <BarChart3 className="h-4 w-4 text-gray-500 mr-2" />
                <span>Pages processed: {originalOrder.length}</span>
              </div>
              <div className="flex items-center">
                <Brain className="h-4 w-4 text-gray-500 mr-2" />
                <span>Confidence: {(averageConfidence * 100).toFixed(1)}%</span>
              </div>
            </>
          )}
        </div>

        {logs.length > 0 && (
          <div className="mt-6">
            <button
              onClick={() => setShowLogs(!showLogs)}
              className="flex items-center text-sm font-medium text-gray-700 mb-2 hover:text-gray-900"
            >
              {showLogs ? (
                <>
                  Hide Processing Logs <ChevronUp className="h-4 w-4 ml-1" />
                </>
              ) : (
                <>
                  Show Processing Logs <ChevronDown className="h-4 w-4 ml-1" />
                </>
              )}
            </button>
            {showLogs && (
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
            )}
          </div>
        )}
      </div>

      {/* Download and Query Tabs */}
      <div className="mt-8 bg-white rounded-lg border border-gray-200 shadow-sm">
        {/* Tab Headers */}
        <div className="flex border-b border-gray-200">
          <button
            onClick={() => setActiveTab('download')}
            className={`flex-1 px-6 py-4 text-sm font-medium transition-colors ${
              activeTab === 'download'
                ? 'text-indigo-600 border-b-2 border-indigo-600 bg-indigo-50'
                : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
            }`}
          >
            <Download className="h-4 w-4 inline mr-2" />
            Download PDF
          </button>
          <button
            onClick={() => setActiveTab('query')}
            className={`flex-1 px-6 py-4 text-sm font-medium transition-colors ${
              activeTab === 'query'
                ? 'text-indigo-600 border-b-2 border-indigo-600 bg-indigo-50'
                : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
            }`}
          >
            <Search className="h-4 w-4 inline mr-2" />
            Query Document
          </button>
        </div>

        {/* Tab Content */}
        <div className="p-6">
          {activeTab === 'download' && (
            <div className="space-y-4">
              <div className="text-center">
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  Download Reordered PDF
                </h3>
                <p className="text-sm text-gray-600 mb-6">
                  Your document has been reordered and is ready to download. 
                  The PDF contains pages in the correct logical order.
                </p>
                
                {orderChanged && (
                  <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6 text-left">
                    <p className="text-sm text-blue-800">
                      <strong>Order Changed:</strong> Pages have been reordered from{' '}
                      <span className="font-mono">[{originalOrder.join(', ')}]</span> to{' '}
                      <span className="font-mono">[{reorderedOrder.join(', ')}]</span>
                    </p>
                  </div>
                )}

                <div className="flex flex-col sm:flex-row justify-center gap-4">
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
                    Download Reordered PDF
                  </button>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'query' && (
            <div className="space-y-6">
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  Query Your Document
                </h3>
                <p className="text-sm text-gray-600 mb-4">
                  Ask questions about the processed document. The AI will search through the content 
                  and provide answers based on the most relevant sections.
                </p>

                {/* Job ID Display */}
                {jobId && (
                  <div className="bg-gray-50 border border-gray-200 rounded-lg p-3 mb-4">
                    <div className="flex items-center text-sm">
                      <span className="text-gray-600 font-medium mr-2">Job ID:</span>
                      <code className="text-gray-900 font-mono text-xs bg-white px-2 py-1 rounded">
                        {jobId}
                      </code>
                    </div>
                  </div>
                )}

                {/* Query Form */}
                <form onSubmit={handleQuery} className="space-y-4">
                  <div>
                    <label htmlFor="query" className="block text-sm font-medium text-gray-700 mb-2">
                      Enter your question
                    </label>
                    <textarea
                      id="query"
                      value={query}
                      onChange={(e) => setQuery(e.target.value)}
                      placeholder="e.g., What is the problem statement? What are the key findings? What is the conclusion?"
                      rows={3}
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 resize-none"
                      disabled={querying || !jobId}
                    />
                  </div>

                  {queryError && (
                    <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-start">
                      <AlertCircle className="h-5 w-5 text-red-600 mr-2 flex-shrink-0 mt-0.5" />
                      <div className="flex-1">
                        <p className="text-sm font-medium text-red-800">Error</p>
                        <p className="text-sm text-red-700 mt-1">{queryError}</p>
                      </div>
                    </div>
                  )}

                  <button
                    type="submit"
                    disabled={querying || !query.trim() || !jobId}
                    className="w-full px-6 py-3 rounded-md text-white bg-indigo-600 hover:bg-indigo-700 transition-colors flex items-center justify-center disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {querying ? (
                      <>
                        <Loader2 className="h-5 w-5 mr-2 animate-spin" />
                        Querying...
                      </>
                    ) : (
                      <>
                        <Send className="h-5 w-5 mr-2" />
                        Ask Question
                      </>
                    )}
                  </button>
                </form>

                {/* Query Results */}
                {queryResult && (
                  <div className="mt-6 space-y-4">
                    <div className="border-t border-gray-200 pt-6">
                      <h4 className="text-md font-semibold text-gray-900 mb-4 flex items-center">
                        <Brain className="h-5 w-5 mr-2 text-indigo-600" />
                        Answer
                      </h4>
                      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                        <p className="text-gray-700 leading-relaxed whitespace-pre-wrap">
                          {queryResult.answer || queryResult.result || 'No answer found.'}
                        </p>
                      </div>
                    </div>

                    {/* Sources */}
                    {queryResult.sources && queryResult.sources.length > 0 && (
                      <div>
                        <h4 className="text-md font-semibold text-gray-900 mb-4">
                          Sources ({queryResult.sources.length})
                        </h4>
                        <div className="space-y-3">
                          {queryResult.sources.map((source, idx) => (
                            <div
                              key={idx}
                              className="bg-gray-50 border border-gray-200 rounded-lg p-4"
                            >
                              <div className="flex items-start justify-between mb-2">
                                <div className="flex items-center space-x-2">
                                  <span className="text-xs font-medium text-indigo-600 bg-indigo-100 px-2 py-1 rounded">
                                    Source {idx + 1}
                                  </span>
                                  {source.confidence && (
                                    <span className="text-xs text-gray-600">
                                      Confidence: {(source.confidence * 100).toFixed(1)}%
                                    </span>
                                  )}
                                </div>
                                {source.page_number && (
                                  <span className="text-xs text-gray-500">
                                    Page {source.page_number}
                                  </span>
                                )}
                              </div>
                              {source.heading && (
                                <h5 className="text-sm font-medium text-gray-900 mb-2">
                                  {source.heading}
                                </h5>
                              )}
                              <p className="text-sm text-gray-700 leading-relaxed">
                                {source.content || source.text || 'No content available'}
                              </p>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Metadata */}
                    {queryResult.metadata && (
                      <div className="text-xs text-gray-500 mt-4">
                        <p>Query processed in {queryResult.metadata.processing_time || 'N/A'}ms</p>
                        <p>Found {queryResult.metadata.result_count || 0} relevant sections</p>
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ResultsView;