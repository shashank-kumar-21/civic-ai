# Civic AI Complaint Assistant

An AI-powered web application that helps users register civic complaints through a conversational interface.

## Features
- AI-powered chat assistant
- Complaint classification
- Follow-up question handling
- Web-based UI (FastAPI)
- Easy to extend and deploy

## Tech Stack
- Python
- FastAPI
- Phidata
- Groq LLM
- HTML/CSS

## How to Run

### 1. Install dependencies
```bash
pip install -r requirements.txt

GROQ_API_KEY=your_api_key_here

uvicorn app:app --reload

JANAI/
│
├── app.py
├── agent.py
├── templates/
│   └── index.html
├── requirements.txt
├── .env (ignored)
└── README.md
