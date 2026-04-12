"""
history_manager.py — Supabase History & Caching (FIXED)
NLP BASED CODE INTERPRETER v2.0
Fix: Uses requests directly to bypass RLS issues with supabase-py
"""

import hashlib
import requests
import json
from datetime import datetime


class HistoryManager:
    def __init__(self, url: str, key: str):
        self.url = url.rstrip("/")
        self.key = key
        self.headers = {
            "apikey": key,
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "Prefer": "return=representation"
        }
        self.enabled = bool(url and key)
        self.client = None  # kept for compatibility
        if self.enabled:
            try:
                from supabase import create_client
                self.client = create_client(url, key)
            except Exception:
                pass

    def get_code_hash(self, code: str) -> str:
        return hashlib.md5(code.strip().encode()).hexdigest()

    def get_cached(self, code: str) -> dict:
        if not self.enabled:
            return None
        try:
            code_hash = self.get_code_hash(code)
            resp = requests.get(
                f"{self.url}/rest/v1/code_history",
                headers=self.headers,
                params={"code_hash": f"eq.{code_hash}", "select": "*", "limit": "1"}
            )
            if resp.status_code == 200:
                data = resp.json()
                return data[0] if data else None
        except Exception as e:
            print(f"Cache fetch error: {e}")
        return None

    def save_to_history(self, code: str, language: str, results: dict) -> bool:
        if not self.enabled:
            return False
        try:
            code_hash = self.get_code_hash(code)
            payload = {
                "code_hash": code_hash,
                "language": language,
                "code": code[:5000],
                "explanation": results.get("explanation", ""),
                "translation": results.get("translation", ""),
                "complexity": results.get("complexity", ""),
                "bugs": results.get("bugs", ""),
                "test_cases": results.get("test_cases", ""),
                "pseudocode": results.get("pseudocode", ""),
                "approaches": results.get("approaches", ""),
                "algorithm": results.get("algorithm", ""),
            }
            # Use upsert to avoid duplicate key errors
            headers = {**self.headers, "Prefer": "resolution=merge-duplicates,return=representation"}
            resp = requests.post(
                f"{self.url}/rest/v1/code_history",
                headers=headers,
                data=json.dumps(payload)
            )
            if resp.status_code in [200, 201]:
                return True
            else:
                print(f"Save error {resp.status_code}: {resp.text}")
                return False
        except Exception as e:
            print(f"Save error: {e}")
            return False

    def get_all_history(self) -> list:
        if not self.enabled:
            return []
        try:
            resp = requests.get(
                f"{self.url}/rest/v1/code_history",
                headers=self.headers,
                params={
                    "select": "id,language,code,created_at",
                    "order": "created_at.desc",
                    "limit": "50"
                }
            )
            if resp.status_code == 200:
                return resp.json()
        except Exception as e:
            print(f"History fetch error: {e}")
        return []

    def delete_history(self, record_id: str) -> bool:
        if not self.enabled:
            return False
        try:
            resp = requests.delete(
                f"{self.url}/rest/v1/code_history",
                headers=self.headers,
                params={"id": f"eq.{record_id}"}
            )
            return resp.status_code in [200, 204]
        except Exception as e:
            print(f"Delete error: {e}")
            return False

    def get_stats(self) -> dict:
        if not self.enabled:
            return {"total": 0, "languages": {}}
        try:
            resp = requests.get(
                f"{self.url}/rest/v1/code_history",
                headers=self.headers,
                params={"select": "language"}
            )
            if resp.status_code == 200:
                data = resp.json()
                total = len(data)
                lang_count = {}
                for row in data:
                    lang = row.get("language", "Unknown")
                    lang_count[lang] = lang_count.get(lang, 0) + 1
                return {"total": total, "languages": lang_count}
        except Exception as e:
            print(f"Stats error: {e}")
        return {"total": 0, "languages": {}}

    def get_full_record(self, record_id: str) -> dict:
        if not self.enabled:
            return {}
        try:
            resp = requests.get(
                f"{self.url}/rest/v1/code_history",
                headers=self.headers,
                params={"id": f"eq.{record_id}", "select": "*"}
            )
            if resp.status_code == 200:
                data = resp.json()
                return data[0] if data else {}
        except Exception as e:
            print(f"Fetch record error: {e}")
        return {}

    def get_user_history(self, user_id=None) -> list:
        """Get history for specific user (or anonymous if user_id is None)"""
        if not self.enabled:
            return []
        try:
            params = {"select": "id,language,code,created_at", "order": "created_at.desc", "limit": "30"}
            if user_id:
                params["user_id"] = f"eq.{user_id}"
            else:
                params["user_id"] = "is.null"
            resp = requests.get(f"{self.url}/rest/v1/code_history", headers=self.headers, params=params)
            if resp.status_code == 200:
                return resp.json()
        except Exception as e:
            print(f"User history error: {e}")
        return []

    def save_to_history(self, code: str, language: str, results: dict, user_id=None) -> bool:
        """Save with optional user_id"""
        if not self.enabled:
            return False
        try:
            code_hash = self.get_code_hash(code)
            payload = {
                "code_hash": code_hash,
                "language": language,
                "code": code[:5000],
                "explanation": results.get("explanation", ""),
                "translation": results.get("translation", ""),
                "complexity": results.get("complexity", ""),
                "bugs": results.get("bugs", ""),
                "test_cases": results.get("test_cases", ""),
                "pseudocode": results.get("pseudocode", ""),
                "algorithm": results.get("algorithm", ""),
                "approaches": results.get("approaches", ""),
            }
            if user_id:
                payload["user_id"] = str(user_id)
            headers = {**self.headers, "Prefer": "resolution=merge-duplicates,return=representation"}
            resp = requests.post(f"{self.url}/rest/v1/code_history", headers=headers, data=json.dumps(payload))
            return resp.status_code in [200, 201]
        except Exception as e:
            print(f"Save error: {e}")
            return False

    def get_cached(self, code: str, user_id=None) -> dict:
        """Get cached result for code, scoped to user"""
        if not self.enabled:
            return None
        try:
            code_hash = self.get_code_hash(code)
            params = {"code_hash": f"eq.{code_hash}", "select": "*", "limit": "1"}
            if user_id:
                params["user_id"] = f"eq.{user_id}"
            else:
                params["user_id"] = "is.null"
            resp = requests.get(f"{self.url}/rest/v1/code_history", headers=self.headers, params=params)
            if resp.status_code == 200:
                data = resp.json()
                return data[0] if data else None
        except Exception as e:
            print(f"Cache error: {e}")
        return None
