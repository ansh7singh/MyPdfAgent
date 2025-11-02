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
          { message: "File uploaded successfully!", timestamp: new Date() },
          { message: "Processing document...", timestamp: new Date() },
        ]);

        if (res.data.result) {
          setJobResult({
            ...res.data.result,
            original_filename: file.name,
            created_at: new Date().toISOString(),
          });
          setStage("results");
        } else {
          await pollForResults(res.data.job_id || res.data.task_id);
        }
      } else {
        throw new Error(res.data?.message || "Upload failed");
      }
    } catch (err) {
      console.error("Upload error:", err.response?.data || err.message);
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
          onDownload={() =>
            window.open(
              jobResult?.download_url || "http://127.0.0.1:8000/agent/download",
              "_blank"
            )
          }
        />
      )}
    </div>
  );
}

export default App;
