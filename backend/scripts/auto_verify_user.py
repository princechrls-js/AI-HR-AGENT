import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()
supabase_admin = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_SERVICE_ROLE_KEY'))

email_to_verify = "prince.riodejanero@gmail.com"

print(f"Fetching user with email {email_to_verify}...")
try:
    # Use the admin API to list users and find the one with the matching email
    users_response = supabase_admin.auth.admin.list_users()
    target_user = next((u for u in users_response if u.email == email_to_verify), None)

    if target_user:
        print(f"Found user ID: {target_user.id}")
        # Mark as email confirmed
        supabase_admin.auth.admin.update_user_by_id(target_user.id, {"email_confirm": True})
        print(f"Successfully auto-verified {email_to_verify}!")
    else:
        print(f"User {email_to_verify} not found in Supabase Auth.")
except Exception as e:
    print(f"Error: {e}")
