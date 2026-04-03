import os
from dotenv import load_dotenv
from supabase import create_client
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.user import User

load_dotenv()
supabase_admin = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_SERVICE_ROLE_KEY'))

db_url = os.getenv('DATABASE_URL')
engine = create_engine(db_url)
Session = sessionmaker(bind=engine)
db = Session()

def setup_user(email, password, role):
    print(f"Setting up {role} user: {email}...")
    try:
        # Check if user exists in local DB
        local_user = db.query(User).filter(User.email == email).first()
        if not local_user:
            # Create in Supabase (Auth Admin ignores rate limits mostly)
            resp = supabase_admin.auth.admin.create_user({
                "email": email,
                "password": password,
                "email_confirm": True,
                "user_metadata": {"role": role, "full_name": f"Test {role}"}
            })
            # Insert into local DB
            new_user = User(
                name=f"Test {role}",
                email=email,
                password_hash="[STORED_IN_SUPABASE_AUTH]",
                role=role
            )
            db.add(new_user)
            db.commit()
            print(f"Created {role} user successfully.")
        else:
            print(f"{role} user already exists in local DB.")
    except Exception as e:
        print(f"Error for {email}: {e}")

setup_user("test_hr_user@example.com", "Password123!", "hr")
setup_user("test_candidate_user@example.com", "Password123!", "candidate")
