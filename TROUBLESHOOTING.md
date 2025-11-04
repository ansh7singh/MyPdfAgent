# Troubleshooting Guide

## Issue: Upload fails and redirects back to upload page

### Common Causes and Solutions:

#### 1. **Ollama Not Running**
**Symptom**: Error mentions "Ollama", "LLM", or "PageOrderingAgent"

**Solution**:
```bash
# Start Ollama in a separate terminal
ollama serve

# Make sure llama3 model is available
ollama pull llama3:latest
```

#### 2. **Tesseract OCR Not Installed**
**Symptom**: Error mentions "OCR", "Tesseract", or "Text extraction failed"

**Solution**:
```bash
# macOS
brew install tesseract

# Linux
sudo apt-get install tesseract-ocr

# Windows
# Download from https://github.com/UB-Mannheim/tesseract/wiki
```

#### 3. **Backend Server Not Running**
**Symptom**: Network error or connection refused

**Solution**:
```bash
cd backend/mainAgent
python manage.py runserver
```

#### 4. **Missing Dependencies**
**Symptom**: ModuleNotFoundError

**Solution**:
```bash
cd backend/mainAgent
pip install -r requirements.txt
pip install django-cors-headers fpdf2
```

#### 5. **Check Browser Console**
Open browser DevTools (F12) and check:
- Console tab for JavaScript errors
- Network tab for API request/response details

#### 6. **Check Backend Logs**
Look at the Django server console output for detailed error messages.

### Debugging Steps:

1. **Check if backend is running**:
   - Visit: http://127.0.0.1:8000/admin/
   - Should show Django admin page

2. **Test upload endpoint directly**:
   ```bash
   curl -X POST http://127.0.0.1:8000/agent/upload/ \
     -F "file=@yourfile.pdf"
   ```

3. **Check frontend console**:
   - Open browser DevTools (F12)
   - Go to Console tab
   - Look for error messages
   - Check Network tab for API responses

4. **Verify all services are running**:
   - Django server: `python manage.py runserver`
   - Ollama: `ollama serve` (if using LLM)
   - Frontend: `npm run dev` (if running separately)

### Error Messages:

The improved error handling now provides more specific error messages:

- **"AI processing failed"**: Ollama not running or model not available
- **"Text extraction failed"**: Tesseract OCR not installed
- **"PDF processing failed"**: File may be corrupted or unsupported format
- **"Processing failed"**: Check server logs for details

