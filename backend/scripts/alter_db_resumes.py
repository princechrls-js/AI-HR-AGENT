import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app.core.database import engine

def alter_db():
    try:
        with engine.begin() as conn:
            # Check if columns exist and add them
            try:
                conn.execute(text('ALTER TABLE users ADD COLUMN resume_url VARCHAR;'))
                print("Added resume_url")
            except Exception as e:
                print(f"resume_url error or exists: {e}")
                
            try:
                conn.execute(text('ALTER TABLE users ADD COLUMN parsed_resume_text TEXT;'))
                print("Added parsed_resume_text")
            except Exception as e:
                print(f"parsed_resume_text error or exists: {e}")
                
    except Exception as e:
        print(f"Error executing raw alter: {e}")

if __name__ == "__main__":
    alter_db()
