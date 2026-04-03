-- AI HR Agent Backend: Supabase Database Schema

-- 1. Users Table
CREATE TABLE IF NOT EXISTS public.users (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('hr', 'candidate')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 2. Jobs Table
CREATE TABLE IF NOT EXISTS public.jobs (
    id SERIAL PRIMARY KEY,
    hr_id INTEGER REFERENCES public.users(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    company_name TEXT NOT NULL,
    location TEXT NOT NULL,
    employment_type TEXT NOT NULL,
    experience_required TEXT NOT NULL,
    skills_required TEXT NOT NULL,
    job_description TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 3. Applications Table
CREATE TABLE IF NOT EXISTS public.applications (
    id SERIAL PRIMARY KEY,
    job_id INTEGER REFERENCES public.jobs(id) ON DELETE CASCADE,
    candidate_id INTEGER REFERENCES public.users(id) ON DELETE CASCADE,
    resume_path TEXT NOT NULL,
    resume_text TEXT,
    application_status TEXT DEFAULT 'pending' CHECK (application_status IN ('pending', 'processing', 'screened', 'rejected', 'accepted')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 4. Parsed Resumes Table
CREATE TABLE IF NOT EXISTS public.parsed_resumes (
    id SERIAL PRIMARY KEY,
    application_id INTEGER UNIQUE REFERENCES public.applications(id) ON DELETE CASCADE,
    full_name TEXT,
    email TEXT,
    phone TEXT,
    skills_json JSONB,
    experience_json JSONB,
    education_json JSONB,
    projects_json JSONB,
    raw_text TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 5. Screening Results Table
CREATE TABLE IF NOT EXISTS public.screening_results (
    id SERIAL PRIMARY KEY,
    application_id INTEGER UNIQUE REFERENCES public.applications(id) ON DELETE CASCADE,
    semantic_score FLOAT,
    skill_score FLOAT,
    experience_score FLOAT,
    final_score FLOAT,
    summary TEXT,
    strengths_json JSONB,
    missing_skills_json JSONB,
    recommendation TEXT,
    explanation_text TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
