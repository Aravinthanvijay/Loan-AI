# Loan Underwriting AI System

A comprehensive AI-powered loan underwriting system using LLMs, ML models, and a multi-agent workflow for automated decision-making.

## System Overview

This project implements a full-stack loan underwriting platform with:
- **Backend**: FastAPI with 6-agent LangGraph workflow powered by Groq Mixtral LLM
- **Frontend**: React SPA with user and admin portals
- **Database**: MongoDB for persistent storage
- **ML**: XGBoost credit scoring with SHAP explainability
- **OCR**: Tesseract-based document extraction
- **RAG**: Policy-based retrieval augmented generation

## Quick Start

### Prerequisites

- Python 3.12+ (with pip and UV)
- Node.js 18+
- MongoDB running locally or remotely
- Groq API key

### Environment Setup

```bash
# Set up Python environment
cd loan_ai
pip install uv
uv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Configuration

Create `.env` file in project root:

```
# Backend
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=mixtral-8x7b-32768
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=loan_ai
JWT_SECRET_KEY=your_secret_key_here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Frontend
VITE_API_URL=http://localhost:8000/api

# OCR & Document Processing
TESSERACT_PATH=/path/to/tesseract

# File Paths
UPLOAD_DIR=./uploads
LOGS_DIR=./logs
```

### Run Backend

```bash
cd backend
python -m uvicorn main:app --reload --port 8000
```

Backend API: `http://localhost:8000`
API Docs: `http://localhost:8000/docs`

### Run Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend: `http://localhost:3000`

## Project Structure

```
loan_ai/
├── backend/
│   ├── main.py              # FastAPI app entry point
│   ├── config.py            # Configuration management
│   ├── routes/              # API endpoints
│   ├── agents/              # 6-agent workflow
│   ├── graph/               # LangGraph workflow orchestration
│   ├── ml/                  # ML models (XGBoost, SHAP)
│   ├── ocr/                 # Document extraction
│   ├── rag/                 # Policy retrieval system
│   ├── db/                  # Database layer
│   │   ├── mongodb.py       # MongoDB connection
│   │   └── repositories/    # CRUD operations
│   └── schemas/             # Pydantic models
├── frontend/
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── pages/          # React pages
│   │   ├── services/       # API services
│   │   ├── context/        # Auth context
│   │   └── App.jsx         # Main router
│   └── package.json
├── data/
│   ├── policies/           # Policy documents for RAG
│   └── models/             # Pre-trained ML models
├── tests/                  # Test suite
├── scripts/                # Utility scripts
├── requirements.txt        # Python dependencies
└── README.md
```

## Agent Workflow

The system uses a 6-agent LangGraph workflow:

1. **Agent 1 - Intake Validation**: Validates application completeness, checks against blacklist/duplicates
2. **Agent 2 - Document Processing**: OCR extraction from PAN and salary slips
3. **Agent 3 - Credit Scoring**: XGBoost model with SHAP explainability
4. **Agent 4 - Rules Engine**: Hard business rules (age, income, FOIR ratios)
5. **Agent 5 - Policy Compliance**: RAG-based policy verification
6. **Agent 6 - Final Decision**: LLM-based decision synthesis using Groq Mixtral

## Key Technologies

### Backend
- **FastAPI 0.115.9**: Web framework
- **LangGraph 0.2.55**: Agent orchestration
- **Langchain 0.3.0**: LLM chain management
- **Groq API**: Mixtral-8x7b-32768 LLM
- **Motor 3.3.2**: Async MongoDB driver
- **XGBoost 2.0.2**: Credit scoring model
- **SHAP 0.44.1**: Model explainability
- **FAISS 1.8.0**: Vector similarity search
- **PyTesseract**: OCR integration
- **JWT**: Authentication

### Frontend
- **React 18.2**: UI framework
- **React Router 6**: Routing
- **Vite 5**: Build tool
- **Vanilla CSS**: Styling

### Database
- **MongoDB**: Document storage
- **Motor**: Async driver

## API Documentation

After starting the backend, access Swagger UI at: `http://localhost:8000/docs`

### Main Endpoints

**Authentication**
- `POST /auth/user/login` - User login
- `POST /auth/admin/login` - Admin login

**User Endpoints**
- `POST /user/applications` - Submit new application
- `GET /user/applications` - Get user's applications
- `POST /user/applications/{id}/upload` - Upload documents

**Admin Endpoints**
- `GET /admin/applications` - Get all applications
- `GET /admin/applications/{id}` - Get application details
- `POST /admin/applications/{id}/approve` - Approve application
- `POST /admin/applications/{id}/reject` - Reject application
- `GET /admin/applications/{id}/trace` - Get agent workflow trace

## Development

### Frontend Development

```bash
cd frontend
npm run dev          # Start dev server
npm run build        # Build for production
npm run preview      # Preview production build
```

### Backend Development

```bash
cd backend
python -m pytest     # Run tests
python -m flake8 .   # Lint code
python -m black .    # Format code
```

### Database

MongoDB collections automatically created on first run:
- `users`
- `applications`
- `blacklist`
- `admins`
- `audit_logs`
- `policies` (for RAG)

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=backend

# Run specific test file
pytest tests/test_graph_flow.py
```

## Deployment

### Backend
```bash
# Production run
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

### Frontend
```bash
npm run build
# Serve dist/ directory with web server
```

## Environment Variables Checklist

- [ ] GROQ_API_KEY set to valid Groq API key
- [ ] MONGODB_URL pointing to MongoDB instance
- [ ] JWT_SECRET_KEY set to strong secret
- [ ] VITE_API_URL set to backend URL

## Common Issues

### Python Dependencies
If you get `ModuleNotFoundError`, ensure UV venv is activated:
```bash
source venv/bin/activate  # Linux/Mac
.\venv\Scripts\activate    # Windows
```

### MongoDB Connection
Ensure MongoDB is running:
```bash
mongod  # Start MongoDB
```

### Groq API
Verify API key is valid and has sufficient quota

### Frontend Build
Clear npm cache if build fails:
```bash
npm cache clean --force
npm install
```

## Performance Considerations

- Frontend React builds with Vite for fast development and production
- Backend uses async/await for non-blocking I/O
- MongoDB indexes on commonly queried fields
- FAISS vector DB for efficient similarity search
- LLM responses cached where applicable

## Security

- JWT authentication with short-lived tokens
- Password hashing with bcrypt
- Input validation on all endpoints
- CORS configured for frontend origin
- Sensitive data in .env (not committed)
- Rate limiting on auth endpoints

## Contributing

1. Create feature branch from `main`
2. Make changes with tests
3. Ensure all tests pass
4. Submit PR with description

## Support

For issues or questions, check:
- Backend docs: http://localhost:8000/docs
- Frontend console for errors
- MongoDB logs for connection issues
