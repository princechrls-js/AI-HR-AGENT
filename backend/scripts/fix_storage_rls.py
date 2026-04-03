import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def fix_storage_rls():
    db_url = os.getenv('DATABASE_URL', '')
    db_url = db_url.replace('+psycopg2', '')
    if not db_url.startswith('postgresql://'): 
        db_url = db_url.replace('postgres://', 'postgresql://')
        
    print(f"Connecting to database to applied public Storage RLS policies...")
    
    try:
        conn = psycopg2.connect(db_url)
        conn.autocommit = True
        cur = conn.cursor()
        
        # We need to make sure the bucket is fully set to public and has policies
        # 1. Enable RLS on storage.objects if not already
        cur.execute("ALTER TABLE storage.objects ENABLE ROW LEVEL SECURITY;")
        
        # 2. Add an INSERT policy for the 'resumes' bucket
        # We use standard SQL syntax.
        sql_insert_policy = """
        DO $$ 
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pg_policies 
                WHERE tablename = 'objects' AND policyname = 'Give public access to resumes bucket for inserts'
            ) THEN
                CREATE POLICY "Give public access to resumes bucket for inserts" ON storage.objects
                FOR INSERT TO public WITH CHECK (bucket_id = 'resumes');
            END IF;
        END $$;
        """
        cur.execute(sql_insert_policy)

        # 3. Add a SELECT policy just in case
        sql_select_policy = """
        DO $$ 
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pg_policies 
                WHERE tablename = 'objects' AND policyname = 'Give public access to select resumes'
            ) THEN
                CREATE POLICY "Give public access to select resumes" ON storage.objects
                FOR SELECT TO public USING (bucket_id = 'resumes');
            END IF;
        END $$;
        """
        cur.execute(sql_select_policy)
        
        print("Successfully added RLS policies to storage.objects for the 'resumes' bucket!")
        cur.close()
        conn.close()
    except Exception as e:
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    fix_storage_rls()
