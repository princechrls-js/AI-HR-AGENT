from app.core.database import engine
from sqlalchemy import text

def migrate():
    with engine.connect() as conn:
        print("Checking for 'career' column in 'users' table...")
        try:
            # Check if column exists (SQLite/PostgreSQL compatible check)
            # For simplicity, we just try to add it and catch the error if it exists
            conn.execute(text("ALTER TABLE users ADD COLUMN career TEXT"))
            conn.commit()
            print("Successfully added 'career' column to 'users' table.")
        except Exception as e:
            if "duplicate column name" in str(e).lower() or "already exists" in str(e).lower():
                print("Column 'career' already exists.")
            else:
                print(f"Error migrating: {e}")

if __name__ == "__main__":
    migrate()
