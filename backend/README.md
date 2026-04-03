# AI HR Agent Backend

A production-ready, modular monolithic backend for an AI-powered HR platform built with FastAPI.

## Architecture

The project follows a **Modular Monolithic** architecture with clear separation of concerns:

- **app/core**: Core configurations, database setup, and security utilities.
- **app/models**: SQLAlchemy database models.
- **app/schemas**: Pydantic data validation and transformation schemas.
- **app/services**: Business logic layers including AI services, file storage, and OCR.
- **app/routes**: API endpoints grouped by functionality (Auth, HR, Candidate, Applications, Results).
- **app/ai**: AI prompts and the screening pipeline orchestration.
- **app/dependencies**: FastAPI dependencies for auth and role-based access.

## Features

- **Role-Based Authentication**: Separate flows for HR and Candidates using JWT.
- **Job Management**: Full CRUD for HR to manage job postings.
- **Smart Resume Parsing**: Extracts text using PyMuPDF with Tesseract OCR fallback for scanned PDFs.
- **AI Screening Pipeline**:
  - LLM-based resume structuring (OpenRouter).
  - Semantic similarity scoring (Sentence Transformers + FAISS).
  - Skill and experience matching logic.
  - AI-generated explanations for scoring.
- **Explainable AI**: HR can see *why* a candidate received a certain score.

## Tech Stack

- **Framework**: FastAPI
- **Database**: PostgreSQL (via SQLAlchemy ORM)
- **AI/LLM**: OpenRouter (GPT-based models)
- **Embeddings**: Sentence Transformers (`BAAI/bge-base-en-v1.5`)
- **Vector Store**: FAISS
- **OCR**: Tesseract OCR
- **PDF Processing**: PyMuPDF (fitz)

## Setup and Installation

### Prerequisites
- Python 3.9+
- Supabase Account and Project
- Tesseract OCR installed on your system (optional but recommended for scanned resumes)

### Installation Steps

1. **Navigate to the backend directory**:
   ```bash
   cd backend
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Setup Environment Variables**:
   Copy `.env.example` to `.env` and fill in your details (Supabase URL, Keys, and DB URL):
   ```bash
   cp .env.example .env
   ```

5. **Supabase Setup**:
   - **Database**: Go to the SQL Editor in Supabase and paste the contents of `supabase_schema.sql` (found in the artifacts or project root).
   - **Storage**: 
     1. Go to **Storage** in the Supabase Sidebar.
     2. Click **New Bucket**.
     3. Name it `resumes` (or whatever you set in `SUPABASE_STORAGE_BUCKET`).
     4. Set it to **Public**.
     5. Under **Policies**, ensure `authenticated` and `anon` users have `INSERT` and `SELECT` permissions (or use the 'Full Access' template for development).

6. **Run the application**:
   ```bash
   # From within the backend directory
   uvicorn app.main:app --reload
   ```

6. **Access API Documentation**:
   Open [http://localhost:8000/docs](http://localhost:8000/docs) in your browser.

## API Overview

### Authentication
- `POST /auth/signup`: Create a new account (role: 'hr' or 'candidate').
- `POST /auth/login`: Get JWT access token.
- `GET /auth/me`: Get current user details.

### HR Features
- `POST /hr/jobs`: Create a new job.
- `GET /hr/jobs`: List jobs created by current HR.
- `GET /results/job/{job_id}`: View all applicant results for a job.

### Candidate Features
- `GET /jobs`: Browse available jobs.
- `POST /applications/apply`: Apply to a job with a PDF resume.
- `GET /results/{application_id}`: View your AI screening result.

## Future Improvements
- Implement background task queues (Celery/Redis) for resume processing.
- Add support for docx files.
- Enhance experience relevance matching using LLM-based timeline analysis.
- Add multi-language support for resumes.
