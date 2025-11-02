# Create a README.md
echo "# PDF Agent

A full-stack application for processing PDF documents with AI.

## Features
- PDF Upload and Processing
- Document Analysis
- AI-powered Reconstruction

## Tech Stack
- Frontend: React.js, TailwindCSS
- Backend: Django, Django REST Framework
- AI: Custom Agents (OCR, PDF Processing)

## Getting Started

### Prerequisites
- Python 3.8+
- Node.js 16+
- npm or yarn

### Installation

1. Clone the repository
   \`\`\`bash
   git clone https://github.com/yourusername/pdf-agent.git
   cd pdf-agent
   \`\`\`

2. Set up the backend
   \`\`\`bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\\Scripts\\activate
   pip install -r requirements.txt
   python manage.py migrate
   \`\`\`

3. Set up the frontend
   \`\`\`bash
   cd ../frontend
   npm install
   \`\`\`

### Running the Application

1. Start the backend server
   \`\`\`bash
   cd backend
   python manage.py runserver
   \`\`\`

2. Start the frontend development server
   \`\`\`bash
   cd frontend
   npm run dev
   \`\`\"

## Environment Variables

### Backend (.env)
\`\`\`
DEBUG=True
SECRET_KEY=your-secret-key
ALLOWED_HOSTS=localhost,127.0.0.1
\`\`\`

## License
MIT
" > README.md