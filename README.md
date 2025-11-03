# 📄 PDF Resolver

### 🚀 Intelligent PDF Reconstruction & Analysis System

PDF Resolver is an intelligent document processing system that analyzes, reorders, and reconstructs PDF documents that have been shuffled or scanned out of order.  
It uses **OCR (Optical Character Recognition)**, **Computer Vision**, and **Machine Learning** to detect the correct page sequence and rebuilds the document accurately.

---

## 📚 Table of Contents
1. [Overview](#overview)
2. [System Architecture](#system-architecture)
3. [Frontend Implementation](#frontend-implementation)
4. [Backend Implementation](#backend-implementation)
5. [API Endpoints](#api-endpoints)
6. [Installation & Setup](#installation--setup)
7. [Usage Guide](#usage-guide)
8. [Troubleshooting](#troubleshooting)
9. [Future Enhancements](#future-enhancements)

---

## 🧩 Overview
PDF Resolver intelligently:
- Extracts text and images from PDFs  
- Uses OCR to analyze image-based pages  
- Applies content and visual analysis to detect the correct page order  
- Reconstructs the document in its proper sequence  
- Provides an interface for querying document contents  

---

## 🏗️ System Architecture

### **Frontend**
- **Framework:** React.js (Vite)
- **Styling:** Tailwind CSS
- **State Management:** React Hooks (`useState`, `useEffect`, `useContext`)
- **HTTP Client:** Fetch API
- **Icons:** Lucide React Icons

### **Backend**
- **Framework:** FastAPI (Python)
- **Document Processing:** PyPDF2, pdf2image, pytesseract
- **Machine Learning:** scikit-learn, numpy
- **API Type:** RESTful API with CORS support
- **Job Queue:** Background Task Processing

---

## 💻 Frontend Implementation

### Core Components

#### 1. `pdfAgent.jsx`
Main component that manages application state and routes between views.

**Features:**
- Handles file uploads, processing states, and result display  
- Visualizes processing pipeline  
- Responsive and error-tolerant UI  

#### 2. Upload Component
- Drag-and-drop or file selector for PDFs  
- Validates file type and size  
- Shows upload progress  

#### 3. Processing Component
- Displays real-time progress  
- Step-by-step visualization  
- Error handling and feedback  

#### 4. Results Component
- Download reconstructed PDF  
- View confidence scores  
- Query document content  
- Option to process a new document  

---

## ⚙️ Backend Implementation

### Core Modules

#### 1. File Upload Handler
- Validates and stores incoming PDFs  
- Initiates processing pipeline  

#### 2. Document Processor
- Extracts text & images  
- Runs OCR on scanned pages  
- Analyzes relationships between pages  

#### 3. Page Order Analyzer
- Determines order using:
  - Text continuity  
  - Header/Footer matching  
  - Page number detection  
  - Visual similarity scoring  

#### 4. PDF Reconstructor
- Reorders pages  
- Rebuilds optimized PDF  
- Applies quality and size optimization  

---

## 🧠 API Endpoints

| Endpoint | Method | Description |
|-----------|---------|-------------|
| `/agent/upload/` | **POST** | Uploads PDF and starts processing |
| `/agent/status/{job_id}` | **GET** | Returns current processing status |
| `/agent/download/{job_id}` | **GET** | Downloads reconstructed PDF |
| `/agent/query/{job_id}` | **POST** | Ask natural language queries about the document |

---

## 🛠️ Installation & Setup

### **🔹 Prerequisites**
Ensure the following are installed:
- **Node.js** (v16+)
- **Python** (3.8+)
- **Tesseract OCR**
- **Poppler** (for PDF to image conversion)
- **Git**

---

### **1️⃣ Clone the Repository**
```bash
git clone https://github.com/ansh7singh/MyPdfAgent.git
cd MyPdfAgent
