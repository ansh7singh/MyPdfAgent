# 📄 PDF Resolver — Intelligent Document Reconstruction System

## 🧠 Overview

**PDF Resolver** is an AI-powered document processing system built with **Django (Backend)** and **React (Frontend)** that intelligently analyzes, reorders, and reconstructs **shuffled or scanned PDF documents**.

It combines **Computer Vision**, **Optical Character Recognition (OCR)**, and **Machine Learning** to:
- Extract text and visual features from PDFs  
- Detect logical order of pages (even if scanned or jumbled)  
- Reconstruct the correct document sequence  
- Provide confidence metrics for accuracy  
- Allow document-based Q&A queries (via LLM integration)

---

## 📘 Table of Contents
1. [Features](#features)
2. [System Architecture](#system-architecture)
3. [Technology Stack](#technology-stack)
4. [Project Structure](#project-structure)
5. [Installation & Setup](#installation--setup)
6. [Backend Setup](#backend-setup)
7. [Frontend Setup](#frontend-setup)
8. [Environment Variables](#environment-variables)
9. [API Endpoints](#api-endpoints)
10. [Usage Guide](#usage-guide)
11. [Troubleshooting](#troubleshooting)
12. [Testing](#testing)
13. [Future Enhancements](#future-enhancements)
14. [Contribution Guide](#contribution-guide)
15. [License](#license)
16. [Author](#author)

---

## 🚀 Features

✅ **AI-driven Page Reordering** — Detects correct page order intelligently  
✅ **OCR Extraction** — Reads scanned or image-based PDFs using Tesseract  
✅ **Text Continuity Analysis** — Ensures logical document flow  
✅ **Visual Similarity Check** — Matches headers, footers, and content  
✅ **Confidence Scoring** — Displays result reliability metrics  
✅ **REST API** — Full backend integration for automation  
✅ **Frontend UI** — Simple, modern React interface  
✅ **Error Handling & Logging** — Graceful exception management  
✅ **Scalable Architecture** — Modular design for easy extension  

---

## 🏗️ System Architecture

### **1️⃣ Frontend (React + Vite)**
- **Framework:** React.js  
- **Build Tool:** Vite (fast dev server)  
- **Styling:** Tailwind CSS  
- **Icons:** Lucide React Icons  
- **State Management:** React Hooks (`useState`, `useEffect`, `useContext`)  
- **HTTP Client:** Fetch API  

**Main Components:**
- `pdfAgent.jsx` — Core app logic (file upload, processing state, results)  
- `Upload Component` — Handles file input, drag/drop, validation  
- `Processing Component` — Shows live progress  
- `Results Component` — Displays reconstructed PDF + confidence metrics  

---

### **2️⃣ Backend (Django + REST Framework)**
- **Framework:** Django 5 + DRF  
- **PDF Tools:** `PyPDF2`, `pypdfium2`, `pdf2image`  
- **OCR Engine:** `pytesseract`  
- **ML/Heuristics:** `numpy`, `regex`, `scikit-learn` (if extended)  
- **Task Pipeline:** Sequential multi-stage processor  
- **API:** REST endpoints for upload, status, download, and query  
- **Logging:** Structured error and debug logs  

---

## 🧰 Technology Stack

| Layer | Technology |
|-------|-------------|
| **Frontend** | React.js + Vite + Tailwind CSS |
| **Backend** | Django + Django REST Framework |
| **OCR** | Tesseract |
| **PDF Parsing** | PyPDF2, pdf2image, pypdfium2 |
| **ML/Analysis** | NumPy, regex |
| **Storage** | Local (Media folder) |
| **API Communication** | REST (Fetch / Axios optional) |
| **Version Control** | Git + GitHub |

---

## 🗂️ Project Structure

pdfResolver/
│
├── backend/
│ ├── mainAgent/
│ │ ├── views.py
│ │ ├── services/
│ │ │ ├── ocr_service.py
│ │ │ ├── pdf_service.py
│ │ │ └── reorder_service.py
│ │ ├── utils/
│ │ ├── urls.py
│ │ └── models.py
│ ├── manage.py
│ ├── requirements.txt
│ └── settings.py
│
├── frontend/
│ ├── src/
│ │ ├── components/
│ │ │ ├── Upload.jsx
│ │ │ ├── ProcessingStatus.jsx
│ │ │ └── ResultsView.jsx
│ │ ├── pages/pdfAgent.jsx
│ │ └── App.jsx
│ ├── package.json
│ └── vite.config.js
│
└── README.md


---

## ⚙️ Installation & Setup

### 🧾 Prerequisites
Ensure you have installed:
- **Python 3.8+**
- **Node.js 16+**
- **Tesseract OCR**
- **Poppler-utils**
- **Git**

---

## 🔧 Backend Setup


# 1️⃣ Clone the repository
git clone https://github.com/ansh7singh/MyPdfAgent.git
cd MyPdfAgent/backend

# 2️⃣ Create a virtual environment
python -m venv venv

# 3️⃣ Activate environment
source venv/bin/activate     # macOS/Linux
venv\Scripts\activate        # Windows

# 4️⃣ Install dependencies
pip install -r requirements.txt

# 5️⃣ Run migrations
python manage.py makemigrations
python manage.py migrate

# 6️⃣ Run backend server
python manage.py runserver


✅ The backend will now be live at: http://127.0.0.1:8000

🧾 Environment Variables

Create a .env file in backend/ directory:

OPENAI_API_KEY=your_openai_api_key_here
DEBUG=True
ALLOWED_HOSTS=*

🧩 Backend Dependencies (requirements.txt)
# Core
Django==5.2.7
djangorestframework==3.16.1
python-dotenv==1.2.1

# LLM
openai>=1.0.0

# PDF Processing
PyPDF2==3.0.1
pdf2image==1.17.0
pypdfium2==5.0.0
pytesseract==0.3.13
fpdf2==2.8.2

# Utilities
numpy>=1.24.0
requests>=2.31.0
python-multipart>=0.0.6
PyYAML==6.0.3
regex==2025.10.23
tqdm==4.67.1
urllib3==2.5.0
wheel==0.45.1
wrapt==2.0.0

💻 Frontend Setup
# Navigate to frontend
cd ../frontend

# Install dependencies
npm install

# Start development server
npm run dev


Frontend runs on: http://localhost:5173

🌐 CORS Setup (Important)

In backend/settings.py, add:

INSTALLED_APPS = [
  
    'corsheaders',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    
]

CORS_ALLOW_ALL_ORIGINS = True

🔌 API Endpoints
Endpoint	Method	Description
/agent/upload/	POST	Upload a PDF for processing
/agent/status/{job_id}	GET	Fetch processing status
/agent/download/{job_id}	GET	Download reconstructed PDF
/agent/query/{job_id}	POST	Ask a question about the PDF content
🧭 Usage Guide
Step 1️⃣ — Upload Document


Click “Choose File” or drag a PDF into upload area


Hit “Process Document”


Step 2️⃣ — Monitor Progress


Observe the progress tracker


Shows which processing steps (OCR/Text/Ordering) are complete


Step 3️⃣ — View and Download Results


Download reconstructed PDF


Review page confidence


Query document contents if enabled



⚙️ Example Workflow (CLI Alternative)
# Upload
curl -F "file=@/path/to/file.pdf" http://127.0.0.1:8000/agent/upload/

# Check status
curl http://127.0.0.1:8000/agent/status/<job_id>

# Download
curl -O http://127.0.0.1:8000/agent/download/<job_id>


🧪 Testing
To run backend unit tests:
python manage.py test

To test OCR pipeline manually:
python manage.py shell
from mainAgent.services.ocr_service import extract_text
extract_text('/path/to/file.pdf')


🔍 Troubleshooting
ProblemPossible CauseFix❌ Blank screenReact or backend not runningStart both servers⚠️ 403 on uploadCORS or CSRF issueSet CORS_ALLOW_ALL_ORIGINS=True📄 “File not found” errorWrong path in MEDIA_ROOTEnsure /media/processed/ exists🧠 OCR inaccurateLow quality scanUse higher DPI or clean image⏳ Stuck processingTesseract/Poppler not installedReinstall via Homebrew or apt

🔮 Future Enhancements
✅ AI Enhancements


Use embeddings + LLMs for semantic document reconstruction


Train classifier for document type detection


✅ Performance


Add background task queue (Celery/RQ)


Async OCR for large PDFs


✅ Security


JWT-based user authentication


Encrypted file storage


✅ Integrations


Google Drive / Dropbox upload


Webhooks for automation



🤝 Contribution Guide


Fork this repository


Create a new branch: git checkout -b feature-xyz


Commit changes: git commit -m "Added new feature xyz"


Push to your fork: git push origin feature-xyz


Submit a Pull Request 🎉



📜 License
This project is licensed under the MIT License — free for commercial and personal use.

👨‍💻 Author
Ansh Singh
💼 Backend & AI Developer
🌐 GitHub Profile
📧 anshsingh@example.com

“Turning raw data into intelligent decisions.”


⚡ Quick Start (Developers’ Shortcut)
git clone https://github.com/ansh7singh/MyPdfAgent.git
cd MyPdfAgent/backend && python -m venv venv && source venv/bin/activate
pip install -r requirements.txt && python manage.py runserver
cd ../frontend && npm install && npm run dev

Then open: 👉 http://localhost:5173
Upload any shuffled PDF and see the magic ✨

---

Would you like me to include **diagram-style ASCII architecture** (showing data flow: upload → OCR → reorder → reconstruct → download)?  
It looks great visually in GitHub and helps interviewers understand your system design fast.
