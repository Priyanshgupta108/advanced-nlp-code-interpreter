"""
auth_manager.py — User Authentication via Supabase Auth
NLP BASED CODE INTERPRETER v3.0
Individual accounts — signup, login, logout
"""

import requests
import json


class AuthManager:
    def __init__(self, url: str, key: str):
        self.url = url.rstrip("/")
        self.key = key
        self.auth_url = f"{self.url}/auth/v1"
        self.headers = {
            "apikey": key,
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json"
        }

    def sign_up(self, email: str, password: str, username: str = "") -> dict:
        """Register a new user with email verification"""
        try:
            payload = {
                "email": email,
                "password": password,
                "data": {
                    "username": username or email.split("@")[0]
                },
                "email_redirect_to": "http://localhost:8501"
            }

            resp = requests.post(
                f"{self.auth_url}/signup",
                headers=self.headers,
                json=payload  # Using json instead of data=json.dumps(...)
            )

            data = resp.json()

            if resp.status_code in (200, 201) and data.get("user"):
                return {
                    "success": True,
                    "user": data["user"],
                    "message": "Account created! Please check your email to verify."
                }

            elif data.get("error"):
                return {
                    "success": False,
                    "message": data.get("error_description")
                    or data.get("msg")
                    or data.get("error")
                    or "Signup failed"
                }

            elif data.get("id"):  # User created without email confirmation
                return {
                    "success": True,
                    "user": data,
                    "message": "Account created successfully!"
                }

            return {"success": False, "message": str(data)}

        except Exception as e:
            return {"success": False, "message": f"Error: {str(e)}"}

    def sign_in(self, email: str, password: str) -> dict:
        """Login with email and password"""
        try:
            resp = requests.post(
                f"{self.auth_url}/token?grant_type=password",
                headers=self.headers,
                data=json.dumps({"email": email, "password": password})
            )
            data = resp.json()
            if resp.status_code == 200 and data.get("access_token"):
                return {
                    "success": True,
                    "access_token": data["access_token"],
                    "user": data.get("user", {}),
                    "user_id": data.get("user", {}).get("id", ""),
                    "email": data.get("user", {}).get("email", email),
                    "username": data.get("user", {}).get("user_metadata", {}).get("username", email.split("@")[0]),
                    "message": "Login successful!"
                }
            error_msg = data.get("error_description") or data.get("msg") or data.get("error") or "Login failed"
            return {"success": False, "message": error_msg}
        except Exception as e:
            return {"success": False, "message": f"Error: {str(e)}"}

    def sign_out(self, access_token: str) -> bool:
        """Logout current user"""
        try:
            requests.post(
                f"{self.auth_url}/logout",
                headers={**self.headers, "Authorization": f"Bearer {access_token}"}
            )
            return True
        except Exception:
            return False

    def get_user(self, access_token: str) -> dict:
        """Get current user info from token"""
        try:
            resp = requests.get(
                f"{self.auth_url}/user",
                headers={**self.headers, "Authorization": f"Bearer {access_token}"}
            )
            if resp.status_code == 200:
                return resp.json()
        except Exception:
            pass
        return {}
