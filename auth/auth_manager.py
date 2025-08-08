import hashlib
import secrets
from datetime import datetime, timedelta
import sqlite3
from typing import Dict, Optional, Any


class AuthManager:
    """Handles all authentication and session management"""

    def __init__(self, db_path: str = "usc_ir.db"):
        self.db_path = db_path
        self.session_duration = timedelta(hours=8)  # 8-hour sessions

    def authenticate(self, username: str, password: str) -> Dict[str, Any]:
        """
        Authenticate user credentials
        Returns: {"success": bool, "user": dict, "message": str}
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Check user credentials
            cursor.execute('''
                SELECT id, username, password_hash, is_admin, email, full_name, department
                FROM users 
                WHERE username = ? AND is_active = 1
            ''', (username,))

            user_row = cursor.fetchone()
            conn.close()

            if not user_row:
                return {
                    "success": False,
                    "user": None,
                    "message": "Invalid username or password"
                }

            # Verify password
            stored_hash = user_row[2]
            if not self._verify_password(password, stored_hash):
                return {
                    "success": False,
                    "user": None,
                    "message": "Invalid username or password"
                }

            # Create user object
            user = {
                "id": user_row[0],
                "username": user_row[1],
                "is_admin": bool(user_row[3]),
                "email": user_row[4],
                "full_name": user_row[5],
                "department": user_row[6]
            }

            return {
                "success": True,
                "user": user,
                "message": "Login successful"
            }

        except Exception as e:
            return {
                "success": False,
                "user": None,
                "message": f"Authentication error: {str(e)}"
            }

    def create_session(self, user: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new session for authenticated user"""
        try:
            session_id = secrets.token_urlsafe(32)
            expires_at = datetime.now() + self.session_duration

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Store session in database
            cursor.execute('''
                INSERT INTO user_sessions (session_id, user_id, expires_at, created_at)
                VALUES (?, ?, ?, ?)
            ''', (session_id, user["id"], expires_at, datetime.now()))

            conn.commit()
            conn.close()

            return {
                "session_id": session_id,
                "user_id": user["id"],
                "expires_at": expires_at.isoformat(),
                "created_at": datetime.now().isoformat()
            }

        except Exception as e:
            print(f"Session creation error: {e}")
            return {}

    def validate_session(self, session_data: Optional[Dict[str, Any]]) -> bool:
        """Validate if session is still active"""
        if not session_data or "session_id" not in session_data:
            return False

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                SELECT user_id, expires_at FROM user_sessions 
                WHERE session_id = ? AND expires_at > datetime('now')
            ''', (session_data["session_id"],))

            result = cursor.fetchone()
            conn.close()

            return result is not None

        except Exception as e:
            print(f"Session validation error: {e}")
            return False

    def is_admin(self, user_data: Optional[Dict[str, Any]]) -> bool:
        """Check if user has admin privileges"""
        if not user_data:
            return False
        return user_data.get("is_admin", False)

    def destroy_session(self, session_data: Optional[Dict[str, Any]]) -> bool:
        """Destroy user session"""
        if not session_data or "session_id" not in session_data:
            return True

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                DELETE FROM user_sessions WHERE session_id = ?
            ''', (session_data["session_id"],))

            conn.commit()
            conn.close()
            return True

        except Exception as e:
            print(f"Session destruction error: {e}")
            return False

    def get_user_from_session(self, session_data: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Get user data from session"""
        if not self.validate_session(session_data):
            return None

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                SELECT u.id, u.username, u.is_admin, u.email, u.full_name, u.department
                FROM users u
                JOIN user_sessions s ON u.id = s.user_id
                WHERE s.session_id = ?
            ''', (session_data["session_id"],))

            user_row = cursor.fetchone()
            conn.close()

            if user_row:
                return {
                    "id": user_row[0],
                    "username": user_row[1],
                    "is_admin": bool(user_row[2]),
                    "email": user_row[3],
                    "full_name": user_row[4],
                    "department": user_row[5]
                }

        except Exception as e:
            print(f"User retrieval error: {e}")

        return None

    def _hash_password(self, password: str) -> str:
        """Hash password with salt"""
        salt = secrets.token_hex(16)
        password_hash = hashlib.pbkdf2_hmac('sha256',
                                            password.encode('utf-8'),
                                            salt.encode('utf-8'),
                                            100000)
        return f"{salt}:{password_hash.hex()}"

    def _verify_password(self, password: str, stored_hash: str) -> bool:
        """Verify password against stored hash"""
        try:
            salt, hash_hex = stored_hash.split(':')
            password_hash = hashlib.pbkdf2_hmac('sha256',
                                                password.encode('utf-8'),
                                                salt.encode('utf-8'),
                                                100000)
            return password_hash.hex() == hash_hex
        except:
            return False

    def create_user(self, username: str, password: str, email: str,
                    full_name: str, department: str, is_admin: bool = False) -> bool:
        """Create a new user (admin function)"""
        try:
            password_hash = self._hash_password(password)

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                INSERT INTO users (username, password_hash, email, full_name, 
                                 department, is_admin, is_active, created_at)
                VALUES (?, ?, ?, ?, ?, ?, 1, ?)
            ''', (username, password_hash, email, full_name, department,
                  is_admin, datetime.now()))

            conn.commit()
            conn.close()
            return True

        except Exception as e:
            print(f"User creation error: {e}")
            return False