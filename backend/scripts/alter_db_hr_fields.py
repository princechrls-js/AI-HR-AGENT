from app.core.database import engine
from sqlalchemy import text

def migrate():
    with engine.connect() as conn:
        print("Adding new HR-specific columns to 'users' table...")
        columns = [
            ("skills", "TEXT"),
            ("company_details", "TEXT"),
            ("achievements", "TEXT"),
            ("employee_count", "TEXT")
        ]
        
        for col_name, col_type in columns:
            try:
                conn.execute(text(f"ALTER TABLE users ADD COLUMN {col_name} {col_type}"))
                conn.commit()
                print(f"Successfully added '{col_name}' column.")
            except Exception as e:
                if "duplicate column name" in str(e).lower() or "already exists" in str(e).lower():
                    print(f"Column '{col_name}' already exists.")
                else:
                    print(f"Error adding '{col_name}': {e}")

if __name__ == "__main__":
    migrate()
