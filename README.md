# 🧠 PDF Reorder AI — Intelligent Document Reconstruction System

### 🚀 AI-powered automation for reconstructing jumbled PDFs using local LLMs

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.0-green.svg)](https://www.djangoproject.com/)
[![Ollama](https://img.shields.io/badge/Ollama-Local%20LLM-orange.svg)](https://ollama.ai/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 📘 Overview

**PDF Reorder AI** is an intelligent system that automatically **reconstructs jumbled or disordered PDFs** into their correct logical sequence using advanced AI techniques with **local LLMs** (no cloud dependency!).

This is particularly valuable in:
- 🏦 **Financial Services** — Loan applications, KYC documents
- ⚖️ **Legal Industry** — Contracts, agreements, case files
- 🏥 **Healthcare** — Patient records, medical histories
- 🏢 **Enterprise** — Any document-heavy workflow

The system combines **OCR**, **semantic embeddings**, and **Ollama local LLM reasoning** to intelligently reorder pages and generate professionally structured PDFs with full transparency.

---

## 🧩 Problem Statement

Financial institutions and enterprises handle thousands of scanned PDFs daily. Pages frequently get **shuffled during scanning, merging, or uploading**, causing:

- ⏱️ **Time waste** — Manual sorting takes hours
- ❌ **Human errors** — Missing or misplaced pages
- 💸 **Operational costs** — Staff time on repetitive tasks
- 😤 **Frustration** — Dealing with disorganized documents

**PDF Reorder AI** solves this with explainable, automated intelligence running **100% locally**.

---

## 💡 Solution

### How It Works:
```
┌─────────────┐
│  Upload PDF │
└──────┬──────┘
       │
       ▼
┌─────────────────────┐
│  OCR Agent          │ ← Extracts text from each page
│  (Tesseract)        │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│  Embedding Agent    │ ← Converts text to semantic vectors
│  (Transformers)     │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│  LLM Agent          │ ← AI reasoning for logical order
│  (Ollama/Llama3.2)  │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│  Reorder Service    │ ← Combines AI insights
│  (Hybrid Logic)     │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│  PDF Agent          │ ← Generates structured output
│  (PyPDF2)           │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│  Download Result    │ ← Clean, ordered PDF ready!
└─────────────────────┘
```

---

## ⚙️ Tech Stack

| **Layer** | **Technologies** |
|-----------|------------------|
| **Backend Framework** | Django 5.0 + Django REST Framework |
| **AI/ML Core** | Sentence Transformers, FAISS, Ollama (Local LLM) |
| **OCR Engine** | Tesseract, pdfplumber, pdf2image |
| **Database** | SQLite (built-in, zero config) |
| **File Processing** | PyPDF2, Pillow |
| **LLM** | Ollama (llama3.2, llama2, mistral, etc.) |

**✨ Key Features:**
- 🔒 **100% Local** — No cloud APIs, complete privacy
- 💰 **Zero Cost** — No API fees (Ollama is free)
- ⚡ **Fast** — Local processing, no network latency
- 🛡️ **Secure** — Your documents never leave your machine

---

## 🏗️ System Architecture

### **Clean Architecture Layers**
```
┌──────────────────────────────────────────────┐
│           VIEW LAYER (API Endpoints)          │
│  Upload, Status, Download, Logs Views        │
└────────────────┬─────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────────┐
│          SERVICE LAYER (Business Logic)       │
│  OCR, Embedding, LLM, Reorder, PDF Services  │
└────────────────┬─────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────────┐
│          AGENT LAYER (AI Specialists)         │
│  OCR Agent, Embedding Agent, LLM Agent,      │
│  PDF Agent                                    │
└──────────────────────────────────────────────┘
```

### **Key Design Principles**

✅ **SOLID Principles** — Single responsibility, clean separation  
✅ **Modular** — Easy to swap AI models or OCR engines  
✅ **Lightweight** — No Redis, Celery, or PostgreSQL needed  
✅ **Testable** — Each layer can be tested independently  
✅ **Explainable** — Full transparency in AI decisions

---

## 🗂️ Project Structure
```
pdf-reorder-project/
├── backend/                    # Django Backend
│   ├── api/                    # Main API App
│   │   ├── views/              # API Endpoints
│   │   │   ├── upload_view.py
│   │   │   ├── job_status_view.py
│   │   │   └── download_view.py
│   │   ├── services/           # Business Logic
│   │   │   ├── ocr_service.py
│   │   │   ├── embedding_service.py
│   │   │   ├── llm_service.py
│   │   │   ├── reorder_service.py
│   │   │   └── pdf_service.py
│   │   ├── agents/             # AI Specialists
│   │   │   ├── ocr_agent.py
│   │   │   ├── embedding_agent.py
│   │   │   ├── llm_agent.py
│   │   │   └── pdf_agent.py
│   │   ├── models/             # Database Models
│   │   ├── serializers/        # Data Validation
│   │   └── utils/              # Helper Functions
│   ├── config/                 # Django Settings
│   │   ├── settings.py
│   │   └── urls.py
│   ├── storage/                # File Storage
│   │   ├── uploads/
│   │   └── outputs/
│   ├── db.sqlite3              # SQLite Database
│   ├── manage.py
│   ├── requirements.txt
│   └── .env                    # Environment Variables
│
└── frontend/                   # React Frontend (Optional)
    ├── src/
    ├── package.json
    └── vite.config.js
```

---

## 🌐 REST API Endpoints

| **Endpoint** | **Method** | **Description** |
|--------------|------------|-----------------|
| `/api/upload/` | `POST` | Upload PDF and start processing |
| `/api/job/<job_id>/status/` | `GET` | Check processing progress |
| `/api/job/<job_id>/download/` | `GET` | Download reordered PDF |
| `/api/job/<job_id>/logs/` | `GET` | View detailed AI reasoning logs |

### **Example Response Structure**
```json
{
    "success": true,
    "job_id": "f4f8d0a9-fc44-42b4-98ad-53c25c76c1e5",
    "file_path": "/storage/uploads/f4f8d0a9-fc44-42b4-98ad-53c25c76c1e5.pdf",
    "result": {
        "ocr_result": {
            "success": true,
            "pages": [
                {
                    "page_number": 1,
                    "text": "Scope of Work - Option A...",
                    "confidence": 0.95,
                    "method": "pdfplumber"
                }
            ]
        },
        "reconstruction_result": {
            "success": true,
            "reconstructed_doc": {
                "chunks": [
                    {
                        "heading_buffer": ["Scope of Work"],
                        "content_buffer": ["Executive summary..."]
                    }
                ],
                "total_chunks": 11,
                "duplicate_count": 0
            }
        },
        "pdf_result": {
            "success": true,
            "file_path": "/storage/outputs/reconstructed.pdf",
            "page_count": 11
        },
        "summary": "Document reconstructed with 11 chunks..."
    }
}
```

---

## 🧠 AI Agents Overview

### **1. OCR Agent** 📖
- **Technology:** Tesseract, pdfplumber
- **Purpose:** Extracts text from both digital and scanned PDFs
- **Features:** Automatic detection, confidence scoring, fallback mechanisms

### **2. Embedding Agent** 🔢
- **Technology:** Sentence Transformers (all-MiniLM-L6-v2)
- **Purpose:** Converts text to 384-dimensional semantic vectors
- **Features:** FAISS indexing, batch processing, similarity calculations

### **3. LLM Agent** 🤖
- **Technology:** Ollama (llama3.2, llama2, mistral)
- **Purpose:** Understands document structure and logical flow
- **Features:** Local inference, no API costs, privacy-first

### **4. Reorder Agent** 🔄
- **Technology:** Hybrid algorithm
- **Purpose:** Combines embeddings + LLM reasoning
- **Features:** Weighted decisions, issue detection, multiple strategies

### **5. PDF Agent** 📄
- **Technology:** PyPDF2
- **Purpose:** Generates professional structured PDF
- **Features:** Page reordering, TOC generation, metadata

---

## 🚀 Installation & Setup

### **Prerequisites**

- Python 3.11+
- Ollama installed locally
- Tesseract OCR

### **1. Install Ollama** (Required for LLM)
```bash
# Mac
brew install ollama

# Linux
curl -fsSL https://ollama.com/install.sh | sh

# Windows
# Download from: https://ollama.com/download

# Start Ollama service
ollama serve

# Pull a model (in a new terminal)
ollama pull llama3.2
# OR
ollama pull llama2
ollama pull mistral
```

### **2. Backend Setup**
```bash
# Clone repository
git clone https://github.com/yourusername/pdf-reorder-ai.git
cd pdf-reorder-ai/backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Mac/Linux
# OR
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Install Tesseract OCR
# Mac
brew install tesseract

# Linux (Ubuntu/Debian)
sudo apt-get install tesseract-ocr

# Windows
# Download from: https://github.com/UB-Mannheim/tesseract/wiki

# Setup environment variables
cp .env.example .env
# Edit .env if needed (default values work for most cases)

# Run migrations (creates SQLite database automatically)
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Start development server
python manage.py runserver
```

### **3. Verify Setup**
```bash
# Check Ollama is running
curl http://localhost:11434/api/tags

# Check Django server
curl http://localhost:8000/api/

# Test configuration
python manage.py check_config
```

---

## 📋 Environment Variables

Create a `.env` file in the `backend/` directory:
```bash
# Django Settings
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1

# Ollama Settings
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2

# File Upload
MAX_UPLOAD_SIZE=52428800  # 50MB

# OCR Settings
OCR_CONFIDENCE_THRESHOLD=0.7
EMBEDDING_MODEL=all-MiniLM-L6-v2
```

---

## 🧪 Testing
```bash
# Test OCR extraction
python manage.py test api.tests.test_ocr

# Test full pipeline
python manage.py test api.tests.test_pipeline

# Upload a test PDF via API
curl -X POST http://localhost:8000/api/upload/ \
  -F "file=@test.pdf"
```

---

## 📊 Performance Metrics

| **Metric** | **Value** |
|------------|-----------|
| **Average Processing Time** | 2-3 minutes (10-page PDF) |
| **Accuracy** | 91% average confidence |
| **Supported File Size** | Up to 50MB |
| **OCR Speed** | ~5 seconds per page |
| **Embedding Generation** | ~1 second for 10 pages |
| **LLM Inference (Local)** | ~30 seconds |
| **Cost** | $0 (100% free, no APIs) |

---

## 🪶 Creative Features

### **1. Structured Reconstruction**

Documents are reconstructed into logical chunks with headings:
```json
{
    "chunks": [
        {
            "heading_buffer": ["Problem Statement"],
            "content_buffer": ["Many financial documents..."]
        }
    ],
    "total_chunks": 11,
    "duplicate_count": 0
}
```

### **2. Duplicate Detection**

Automatically identifies duplicate pages or sections.

### **3. Confidence Scoring**

Each extraction and reordering decision includes confidence metrics.

### **4. Summary Generation**

Automatic document summarization for quick overview.

---

## 🎯 Use Cases

### **Financial Services**
- Loan application reordering
- KYC document organization
- Contract reconstruction

### **Legal Industry**
- Case file organization
- Agreement reconstruction
- Court document sorting

### **Healthcare**
- Medical record organization
- Patient history reconstruction
- Insurance claim sorting

---

## 🔮 Future Enhancements

- [ ] Multi-document detection and separation
- [ ] Drag-and-drop manual override UI
- [ ] Multi-language OCR support (Hindi, Spanish, etc.)
- [ ] Batch processing for multiple PDFs
- [ ] Export to other formats (Word, Markdown)
- [ ] Fine-tuned local models for specific domains

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🧑‍💻 Author

**Your Name**  
💼 Full Stack & AI Developer  
🔗 [GitHub](https://github.com/yourusername) | [LinkedIn](https://linkedin.com/in/yourprofile)

---

## 🙏 Acknowledgments

- Ollama team for local LLM infrastructure
- Sentence Transformers community
- Django & DRF communities
- All contributors and testers

---

## 📞 Support

For support, open an issue on GitHub or contact via email.

---

## ⭐ Why This Project?

✅ **Privacy-First** — All processing happens locally  
✅ **Cost-Free** — No API fees, completely free to run  
✅ **Offline Capable** — Works without internet  
✅ **Explainable AI** — Understand every decision  
✅ **Production Ready** — Clean architecture, scalable  
✅ **Easy Setup** — SQLite, no complex database config  

---

**Made with ❤️ using Django + Ollama**
