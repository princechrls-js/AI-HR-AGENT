import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "http://127.0.0.1:8000/api/v1"

# 1. Login HR user (Created manually or previously)
hr_creds = {
    "username": "prince.riodejanero@gmail.com",
    "password": "Prince13@"
}
print("--- 1. Login HR ---")
resp = requests.post(f"{BASE_URL}/auth/login", data=hr_creds)
if resp.status_code != 200:
    print("HR Login failed:", resp.text)
    exit(1)
hr_token = resp.json()["access_token"]
hr_headers = {"Authorization": f"Bearer {hr_token}"}
print("HR Login Success")

# 2. Create Job
print("\n--- 2. Create Job ---")
job_data = {
    "title": "Senior Python Developer",
    "company_name": "Tech Corp",
    "location": "Remote",
    "employment_type": "Full-time",
    "experience_required": "5+ years",
    "skills_required": "Python, FastAPI, Supabase",
    "job_description": "Looking for a backend expert to build scalable APIs."
}
resp = requests.post(f"{BASE_URL}/hr/jobs", json=job_data, headers=hr_headers)
if resp.status_code != 200:
    print("Create Job Failed:", resp.text)
    exit(1)
job_id = resp.json()["id"]
print("Created Job with ID:", job_id)

# 3. Create Candidate test user
# Actually, let's just create a new candidate via signup! Since we bypass email limits sometimes, let's just try.
import time
timestamp = int(time.time())
candidate_email = f"candidate_{timestamp}@example.com"
candidate_password = "Password123!"

print(f"\n--- 3. Create Candidate: {candidate_email} ---")
from supabase import create_client
supabase_admin = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_SERVICE_ROLE_KEY'))

# Insert via Admin API to bypass rate limits
print("Creating Candidate via Admin API to bypass Auth limits.")
supabase_resp = supabase_admin.auth.admin.create_user({
    "email": candidate_email,
    "password": candidate_password,
    "email_confirm": True,
    "user_metadata": {"role": "candidate", "full_name": "Test Candidate"}
})

# Insert into local DB using raw connection
import psycopg2
db_url = os.getenv('DATABASE_URL').replace('+psycopg2', '')
if db_url.startswith('postgresql://'):
    pass # valid for psycopg2
conn = psycopg2.connect(db_url)
cur = conn.cursor()
cur.execute(
    "INSERT INTO users (name, email, password_hash, role, created_at, updated_at) VALUES (%s, %s, %s, %s, NOW(), NOW())",
    ("Test Candidate", candidate_email, "[STORED_IN_SUPABASE_AUTH]", "candidate")
)
conn.commit()
cur.close()
conn.close()

print("\n--- 4. Login Candidate ---")
candidate_creds = {
    "username": candidate_email,
    "password": candidate_password
}
resp = requests.post(f"{BASE_URL}/auth/login", data=candidate_creds)
if resp.status_code != 200:
    print("Candidate Login failed:", resp.text)
    exit(1)
candidate_token = resp.json()["access_token"]
candidate_headers = {"Authorization": f"Bearer {candidate_token}"}
print("Candidate Login Success")

# 5. Apply for the job
print(f"\n--- 5. Candidate applies for Job {job_id} ---")
# Create a dummy pdf file for resume
dummy_pdf = "dummy_resume.pdf"
with open(dummy_pdf, 'wb') as f:
    f.write(b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n"
             b"2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n"
             b"3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 612 792]\n/Contents 4 0 R\n>>\nendobj\n"
             b"4 0 obj\n<< /Length 53 >>\nstream\n"
             b"BT\n/F1 12 Tf\n100 700 Td\n(Python, FastAPI user) Tj\nET\n"
             b"endstream\nendobj\ntrailer\n<<\n/Size 5\n/Root 1 0 R\n>>\n%%EOF\n")

files = {'resume': (dummy_pdf, open(dummy_pdf, 'rb'), "application/pdf")}
resp = requests.post(f"{BASE_URL}/applications/apply?job_id={job_id}", files=files, headers=candidate_headers)
if resp.status_code != 200:
    print("Apply failed:", resp.text)
    exit(1)
application_data = resp.json()
print("Applied successfully. Application ID:", application_data['id'])

print("\n--- 6. Wait for background AI screening ---")
time.sleep(15) # Background task takes a little time to run Faiss/OpenRouter

print(f"\n--- 7. HR checks Result for Job {job_id} ---")
resp = requests.get(f"{BASE_URL}/results/job/{job_id}", headers=hr_headers)
if resp.status_code != 200:
    print("Get Results failed:", resp.text)
    exit(1)
print("Results retrieved:", "\n", json.dumps(resp.json(), indent=2))
print("\n✅ All End-to-End Tests Passed successfully!")

