import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()
DB_URL = os.getenv("DATABASE_URL")

def apply_migrations():
    try:
        engine = create_engine(DB_URL)
        
        with engine.begin() as conn:
            # Add profile columns to users table
            print("Adding columns to users table...")
            
            columns_to_add = [
                ("title", "VARCHAR"),
                ("company_name", "VARCHAR"),
                ("bio", "TEXT"),
                ("avatar_url", "VARCHAR"),
                ("bg_url", "VARCHAR")
            ]
            
            for col_name, col_type in columns_to_add:
                try:
                    conn.execute(text(f"ALTER TABLE users ADD COLUMN {col_name} {col_type};"))
                    print(f"Added column {col_name}")
                except Exception as e:
                    print(f"Could not add {col_name} (might already exist): {e}")
                    
            # Create posts table
            print("\nCreating posts table...")
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS posts (
                    id SERIAL PRIMARY KEY,
                    author_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                    content TEXT NOT NULL,
                    media_url VARCHAR,
                    likes_count INTEGER DEFAULT 0,
                    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );
            """))
            print("Posts table ready.")
            
        print("\nMigrations applied successfully.")
        
    except Exception as e:
        print(f"Migration error: {e}")

if __name__ == "__main__":
    apply_migrations()
