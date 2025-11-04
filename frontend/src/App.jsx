// src/App.jsx
import React, { useState } from "react";
import axios from "axios";
import FileUpload from "./components/FileUpload";
import ProcessingStatus from "./components/ProcessingStatus";
import ResultsView from "./components/ResultsView";

function App() {
  const [uploadedFile, setUploadedFile] = useState(null);
  const [stage, setStage] = useState("upload");
  const [logs, setLogs] = useState([]);
  const [jobResult, setJobResult] = useState(null);

  const handleFileUpload = async (file) => {
    setUploadedFile(file);
    setStage("processing");
    setLogs([{ message: "Starting file upload...", timestamp: new Date() }]);

    const formData = new FormData();
    formData.append("file", file);

    try {
      setLogs((prev) => [...prev, { message: "Uploading file...", timestamp: new Date() }]);

      const res = await axios.post(
        "http://127.0.0.1:8000/agent/upload/",
        formData,
        {
          headers: {
            "Content-Type": "multipart/form-data",
            Accept: "application/json",
          },
        }
      );

      console.log("Upload response:", res.data); // Debug log

      if (res.data && res.data.status === "success") {
        setLogs((prev) => [
          ...prev,
          { message: "✅ File uploaded successfully!", timestamp: new Date() },
          { message: "🔍 Step 1: Extracting text from PDF pages...", timestamp: new Date() },
        ]);

        // Simulate processing steps if result is available immediately
        if (res.data.result) {
          const result = res.data.result;
          
          // Add processing step logs
          setTimeout(() => {
            setLogs((prev) => [
              ...prev,
              { message: "✅ Text extracted from all pages", timestamp: new Date() },
              { message: "🧠 Step 2: Determining correct page order using AI...", timestamp: new Date() },
            ]);
          }, 500);

          setTimeout(() => {
            setLogs((prev) => [
              ...prev,
              { message: "✅ Page order determined", timestamp: new Date() },
              { message: "📄 Step 3: Physically reordering PDF pages...", timestamp: new Date() },
            ]);
          }, 1500);

          setTimeout(() => {
            setLogs((prev) => [
              ...prev,
              { message: "✅ PDF pages reordered successfully", timestamp: new Date() },
              { message: "💾 Saving metadata...", timestamp: new Date() },
            ]);
          }, 2500);

          setTimeout(() => {
            setJobResult({
              ...result,
              job_id: res.data.job_id,
              original_filename: file.name,
              created_at: new Date().toISOString(),
              download_url: res.data.download_url || result?.download_url || result?.pdf_result?.file_path,
              reordered_pdf_filename: result?.reordered_pdf_filename || result?.pdf_result?.file_path?.split('/').pop() || result?.pdf_result?.file_path?.split('\\').pop(),
            });
            setStage("results");
          }, 3000);
        } else {
          await pollForResults(res.data.job_id || res.data.task_id);
        }
      } else {
        throw new Error(res.data?.error || res.data?.message || "Upload failed");
      }
    } catch (err) {
      console.error("Upload error:", err.response?.data || err.message);
      const errorMessage = err.response?.data?.error || err.response?.data?.detail || err.message || "Unknown error occurred";
      setLogs((prev) => [
        ...prev,
        {
          message: `❌ Error: ${errorMessage}`,
          level: "error",
          timestamp: new Date(),
        },
      ]);
      // Stay on processing page to show the error, don't redirect immediately
      // User can manually go back or we show error state
      setJobResult({
        error: errorMessage,
        success: false
      });
      // Give user time to see the error before potentially redirecting
      setTimeout(() => {
        // Only redirect if user wants to try again
      }, 5000);
    }
  };

  const pollForResults = async (jobId) => {
    try {
      const poll = async () => {
        const res = await axios.get(`http://127.0.0.1:8000/agent/query`);
        if (res.data.status === "completed") {
          setJobResult({
            ...res.data.result,
            original_filename: uploadedFile.name,
            created_at: new Date().toISOString(),
          });
          setStage("results");
        } else if (res.data.status === "failed") {
          throw new Error(res.data.message || "Processing failed");
        } else {
          setTimeout(poll, 2000); // Poll every 2 seconds
        }
      };
      await poll();
    } catch (err) {
      console.error("Polling error:", err);
      setLogs((prev) => [
        ...prev,
        {
          message: `Error: ${err.response?.data?.detail || err.message}`,
          level: "error",
          timestamp: new Date(),
        },
      ]);
      setStage("upload");
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      {stage === "upload" && <FileUpload onUpload={handleFileUpload} />}
      {stage === "processing" && (
        <ProcessingStatus jobResult={jobResult} logs={logs} />
      )}
      {stage === "results" && (
        <ResultsView
          jobResult={jobResult}
          logs={logs}
          onStartNew={() => {
            setStage("upload");
            setUploadedFile(null);
            setLogs([]);
            setJobResult(null);
          }}
          onDownload={() => {
            // Ensure we always use the full backend URL
            let downloadUrl = jobResult?.download_url;
            
            // If no download_url, construct from filename
            if (!downloadUrl) {
              const filename = jobResult?.reordered_pdf_filename || 
                               jobResult?.pdf_result?.file_path?.split('/').pop() ||
                               jobResult?.pdf_result?.file_path?.split('\\').pop();
              if (filename) {
                downloadUrl = `http://127.0.0.1:8000/agent/download/${filename}`;
              }
            }
            
            // If download_url is relative, make it absolute
            if (downloadUrl && !downloadUrl.startsWith('http')) {
              downloadUrl = `http://127.0.0.1:8000${downloadUrl.startsWith('/') ? '' : '/'}${downloadUrl}`;
            }
            
            if (!downloadUrl) {
              console.error('No download URL available');
              alert('Download URL not available. Please check the server response.');
              return;
            }
            
            console.log('Downloading PDF from:', downloadUrl);
            window.open(downloadUrl, "_blank");
          }}
        />
      )}
    </div>
  );
}

export default App;
