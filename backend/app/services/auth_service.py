from app.core.database import supabase

class AuthService:
    def __init__(self):
        self.supabase = supabase

    async def sign_up_user(self, email: str, password: str, name: str, role: str):
        # 1. Sign up via Supabase Auth Admin to bypass email rate limits and confirm email
        from app.core.database import supabase_admin
        auth_response = supabase_admin.auth.admin.create_user({
            "email": email,
            "password": password,
            "email_confirm": True,
            "user_metadata": {
                "full_name": name,
                "role": role
            }
        })
        return auth_response

    async def sign_in_user(self, email: str, password: str):
        # 2. Sign in via Supabase Auth
        auth_response = self.supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        return auth_response

auth_service = AuthService()
