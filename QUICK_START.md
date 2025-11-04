# Quick Start Guide

## Starting the Application

### Step 1: Start Backend Server

Open a terminal and run:

```bash
cd backend/mainAgent
python manage.py runserver
```

You should see:
```
Starting development server at http://127.0.0.1:8000/
```

**Important**: Keep this terminal window open - the server must stay running!

### Step 2: Start Frontend (if running separately)

Open another terminal and run:

```bash
cd frontend
npm install  # Only needed first time
npm run dev
```

The frontend will typically run on `http://localhost:5173` (Vite default) or `http://localhost:3000`

### Step 3: Verify Backend is Running

Test if backend is accessible:
```bash
curl http://127.0.0.1:8000/admin/
```

Or visit in browser: http://127.0.0.1:8000/admin/

### Common Issues:

#### "Network Error" in Frontend
- **Cause**: Backend server not running
- **Solution**: Make sure you ran `python manage.py runserver` in the backend/mainAgent directory

#### "Cannot connect to backend"
- **Cause**: Backend stopped or crashed
- **Solution**: Check the backend terminal for error messages and restart

#### Port Already in Use
- **Cause**: Another process is using port 8000
- **Solution**: 
  - Kill the process: `lsof -ti:8000 | xargs kill -9`
  - Or use a different port: `python manage.py runserver 8001`

### Required Services:

1. **Django Backend** - Must be running on port 8000
2. **Ollama** (optional but recommended) - For LLM features:
   ```bash
   ollama serve
   ollama pull llama3:latest
   ```
3. **Tesseract OCR** (optional) - For scanned PDFs:
   ```bash
   brew install tesseract  # macOS
   ```

### Testing the API Directly:

```bash
# Test upload endpoint
curl -X POST http://127.0.0.1:8000/agent/upload/ \
  -F "file=@yourfile.pdf"
```

