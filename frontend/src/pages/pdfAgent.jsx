import React, { useState } from "react";
import {
  Upload,
  FileText,
  Download,
  CheckCircle,
  Loader,
  AlertCircle,
  ArrowRight,
  Sparkles,
} from "lucide-react";

const API_BASE_URL = "http://127.0.0.1:8000/agent";

export default function PDFAgentApp() {
  const [currentPage, setCurrentPage] = useState("upload");
  const [selectedFile, setSelectedFile] = useState(null);
  const [jobId, setJobId] = useState("");
  const [uploadStatus, setUploadStatus] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);

  // ---------------- Upload Handler ----------------
  const handleFileSelect = (e) => {
    const file = e.target.files[0];
    if (file && file.type === "application/pdf") setSelectedFile(file);
    else alert("Please select a valid PDF file.");
  };

  const handleUpload = async () => {
    if (!selectedFile) return alert("Select a PDF file first!");

    setIsProcessing(true);
    setCurrentPage("processing");

    const formData = new FormData();
    formData.append("file", selectedFile);

    try {
      console.log("🚀 Uploading to:", `${API_BASE_URL}/upload/`);

      const response = await fetch(`${API_BASE_URL}/upload/`, {
        method: "POST",
        body: formData,
      });

      const data = await response.json();
      console.log("✅ Response from backend:", data);

      if (data.success) {
        setJobId(data.job_id);
        setUploadStatus({
          success: true,
          jobId: data.job_id,
          result: data.result,
        });
      } else {
        setUploadStatus({ success: false, error: data.error || "Upload failed" });
      }
    } catch (err) {
      console.error("💥 Upload error:", err);
      setUploadStatus({ success: false, error: err.message });
    } finally {
      setIsProcessing(false);
    }
  };

  // ---------------- Processing Page ----------------
  const ProcessingPage = () => {
    if (!uploadStatus)
      return (
        <div className="min-h-screen flex items-center justify-center">
          <Loader className="w-6 h-6 animate-spin" />
        </div>
      );

    if (!uploadStatus.success)
      return (
        <div className="min-h-screen flex flex-col items-center justify-center text-center p-6">
          <AlertCircle className="w-10 h-10 text-red-500 mb-3" />
          <h2 className="text-xl font-semibold text-red-600 mb-2">
            Upload Failed
          </h2>
          <p className="text-gray-600 mb-4">{uploadStatus.error}</p>
          <button
            onClick={() => setCurrentPage("upload")}
            className="px-6 py-3 bg-blue-500 text-white rounded-xl hover:bg-blue-600"
          >
            Try Again
          </button>
        </div>
      );

    const result = uploadStatus.result;
    const ocrPages = result?.ocr_result?.pages || [];
    const totalChunks =
      result?.reconstruction_result?.reconstructed_doc?.total_chunks || 0;
    const summary = result?.summary || "No summary generated";
    const pdfPath = result?.pdf_result?.file_path || "";

    // 🧩 Normalize file path to open correctly
    const handlePdfDownload = () => {
      let fixedPath = pdfPath;

      // If backend returns absolute path (like /Users/...)
      if (fixedPath.startsWith("/Users")) {
        const parts = fixedPath.split("/media/");
        fixedPath = parts.length > 1 ? parts[1] : fixedPath;
      }

      // Remove incorrect "agent/" prefix if it exists
      if (fixedPath.startsWith("agent/media")) {
        fixedPath = fixedPath.replace("agent/", "");
      }

      // Ensure we point to /media/
      const finalUrl = `http://localhost:8000/media/${fixedPath.replace(
        /^media\//,
        ""
      )}`;
      console.log("📂 Opening PDF from:", finalUrl);
      window.open(finalUrl, "_blank");
    };

    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 flex justify-center p-6">
        <div className="max-w-3xl w-full bg-white p-8 rounded-2xl shadow-xl border border-gray-100">
          <div className="text-center mb-8">
            <CheckCircle className="w-10 h-10 text-green-500 mx-auto mb-3" />
            <h2 className="text-2xl font-bold text-gray-900 mb-1">
              Document Processed Successfully!
            </h2>
            <p className="text-sm text-gray-600">Job ID: {jobId}</p>
          </div>

          <div className="space-y-4">
            {/* OCR Result */}
            <div className="p-4 bg-green-50 border border-green-200 rounded-xl">
              <h3 className="font-semibold text-green-900 mb-2">
                OCR Result Overview
              </h3>
              <ul className="text-sm text-green-700 space-y-1">
                <li>
                  <strong>Pages Extracted:</strong> {ocrPages.length}
                </li>
                <li>
                  <strong>Average Confidence:</strong>{" "}
                  {(
                    (ocrPages.reduce((a, b) => a + (b.confidence || 0), 0) /
                      (ocrPages.length || 1)) *
                    100
                  ).toFixed(2)}
                  %
                </li>
              </ul>
            </div>

            {/* Reconstruction Summary */}
            <div className="p-4 bg-blue-50 border border-blue-200 rounded-xl">
              <h3 className="font-semibold text-blue-900 mb-2">
                Reconstruction Summary
              </h3>
              <p className="text-sm text-blue-700 mb-2 leading-relaxed">
                {summary}
              </p>
              <p className="text-xs text-blue-600">
                <strong>Total Chunks:</strong> {totalChunks}
              </p>
            </div>

            {/* Extracted Sections */}
            <div className="p-4 bg-gray-50 border border-gray-200 rounded-xl">
              <h3 className="font-semibold text-gray-900 mb-2 flex items-center gap-2">
                <FileText className="w-5 h-5 text-gray-700" />
                Extracted Sections
              </h3>
              <ul className="text-sm text-gray-700 list-disc ml-6 space-y-1">
                {result?.reconstruction_result?.reconstructed_doc?.chunks?.map(
                  (chunk, i) => (
                    <li key={i}>
                      <strong>{chunk.heading_buffer.join(", ")}</strong> —{" "}
                      {chunk.content_buffer.join(" ")}
                    </li>
                  )
                )}
              </ul>
            </div>

            {/* Download Button */}
            <button
              onClick={handlePdfDownload}
              className="w-full bg-gradient-to-r from-blue-500 to-purple-600 text-white py-4 px-6 rounded-xl font-semibold hover:from-blue-600 hover:to-purple-700 transition-all shadow-lg flex items-center justify-center gap-2"
            >
              <Download className="w-5 h-5" />
              Download Reconstructed PDF
            </button>

            {/* Process Another Document */}
            <button
              onClick={() => setCurrentPage("upload")}
              className="w-full bg-white text-gray-700 py-4 px-6 rounded-xl font-semibold hover:bg-gray-50 border border-gray-200 shadow-md flex items-center justify-center gap-2"
            >
              <ArrowRight className="w-5 h-5" />
              Process Another Document
            </button>
          </div>
        </div>
      </div>
    );
  };

  // ---------------- Upload Page ----------------
  const UploadPage = () => (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 flex items-center justify-center p-6">
      <div className="max-w-2xl w-full bg-white rounded-2xl shadow-xl p-8 border border-gray-100">
        <div className="text-center mb-6">
          <Sparkles className="w-10 h-10 text-purple-600 mx-auto mb-3" />
          <h1 className="text-3xl font-bold text-gray-900 mb-2">PDF Agent</h1>
          <p className="text-gray-600 text-sm">
            Reconstruct, summarize, and download PDFs intelligently.
          </p>
        </div>

        <div className="mb-6">
          <input
            id="file-upload"
            type="file"
            accept=".pdf"
            onChange={handleFileSelect}
            className="hidden"
          />
          <label
            htmlFor="file-upload"
            className="flex flex-col items-center justify-center w-full h-48 border-2 border-dashed border-gray-300 rounded-xl cursor-pointer hover:border-blue-500 hover:bg-blue-50 transition-all"
          >
            <Upload className="w-12 h-12 text-gray-400 mb-3" />
            <span className="text-sm text-gray-600 mb-1">
              {selectedFile ? selectedFile.name : "Click to upload PDF"}
            </span>
            <span className="text-xs text-gray-400">
              {selectedFile
                ? `${(selectedFile.size / 1024).toFixed(2)} KB`
                : "PDF files only"}
            </span>
          </label>
        </div>

        {selectedFile && (
          <button
            onClick={handleUpload}
            disabled={isProcessing}
            className="w-full bg-gradient-to-r from-blue-500 to-purple-600 text-white py-4 px-6 rounded-xl font-semibold hover:from-blue-600 hover:to-purple-700 transition-all shadow-lg disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
          >
            {isProcessing ? (
              <>
                <Loader className="w-5 h-5 animate-spin" />
                Processing...
              </>
            ) : (
              <>
                <Sparkles className="w-5 h-5" />
                Process Document
                <ArrowRight className="w-5 h-5" />
              </>
            )}
          </button>
        )}
      </div>
    </div>
  );

  // ---------------- Render Current Page ----------------
  return (
    <>
      {currentPage === "upload" && <UploadPage />}
      {currentPage === "processing" && <ProcessingPage />}
    </>
  );
}
