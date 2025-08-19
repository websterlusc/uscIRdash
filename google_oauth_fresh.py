# Fresh Google OAuth Implementation for USC IR Portal
# Complete replacement for existing Google Sign-In

import os
import json
from datetime import datetime, timedelta
import sqlite3
import secrets
import jwt

# First, install required packages:
# pip install google-auth google-auth-oauthlib google-auth-httplib2

try:
    from google.auth.transport import requests
    from google.oauth2 import id_token
    GOOGLE_AUTH_AVAILABLE = True
except ImportError:
    print("⚠️ Google Auth libraries not installed. Run: pip install google-auth google-auth-oauthlib")
    GOOGLE_AUTH_AVAILABLE = False

# Configuration
GOOGLE_CLIENT_ID = "890006312213-jb98t4ftcjgbvalgrrbo46sl9u77e524.apps.googleusercontent.com"
USC_DOMAIN = 'usc.edu.tt'
SECRET_KEY = 'usc-ir-secret-key-2025'  # Change this in production
TOKEN_EXPIRY_HOURS = 8
DATABASE = 'usc_ir.db'


class GoogleOAuth:
    """Clean Google OAuth implementation"""
    
    def __init__(self, client_id=GOOGLE_CLIENT_ID):
        self.client_id = client_id
        
    def verify_token(self, credential_token):
        """Verify Google ID token and extract user info"""
        if not GOOGLE_AUTH_AVAILABLE:
            return {'success': False, 'error': 'Google Auth libraries not available'}
            
        try:
            # Verify the token with Google
            idinfo = id_token.verify_oauth2_token(
                credential_token, 
                requests.Request(), 
                self.client_id
            )
            
            # Verify the issuer
            if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                raise ValueError('Invalid token issuer')
            
            # Extract user information
            user_info = {
                'email': idinfo['email'],
                'name': idinfo['name'],
                'picture': idinfo.get('picture', ''),
                'email_verified': idinfo.get('email_verified', False),
                'given_name': idinfo.get('given_name', ''),
                'family_name': idinfo.get('family_name', ''),
                'domain': idinfo['email'].split('@')[1] if '@' in idinfo['email'] else ''
            }
            
            return {'success': True, 'user': user_info}
            
        except ValueError as e:
            return {'success': False, 'error': f'Token verification failed: {str(e)}'}
        except Exception as e:
            return {'success': False, 'error': f'Unexpected error: {str(e)}'}
    
    def is_usc_employee(self, email):
        """Check if email belongs to USC domain"""
        return email.lower().endswith(f'@{USC_DOMAIN.lower()}')
    
    def create_or_update_user(self, user_info):
        """Create or update user in database from Google OAuth"""
        try:
            conn = sqlite3.connect(DATABASE)
            cursor = conn.cursor()
            
            email = user_info['email'].lower()
            name = user_info['name']
            picture = user_info.get('picture', '')
            
            # Check if user exists
            cursor.execute('SELECT id, email, full_name, role, is_approved FROM users WHERE email = ?', (email,))
            existing_user = cursor.fetchone()
            
            if existing_user:
                user_id = existing_user[0]
                # Update existing user
                cursor.execute('''
                    UPDATE users 
                    SET full_name = ?, last_login = ?, google_auth = 1, profile_picture = ?
                    WHERE id = ?
                ''', (name, datetime.now(), picture, user_id))
                
                # Get updated user data
                user_data = {
                    'id': user_id,
                    'email': existing_user[1],
                    'full_name': name,
                    'role': existing_user[3],
                    'is_approved': existing_user[4],
                    'is_new_user': False
                }
                
            else:
                # Create new user
                is_usc = self.is_usc_employee(email)
                role = 'employee' if is_usc else 'guest'
                is_approved = 1 if is_usc else 0  # USC employees auto-approved
                username = email.split('@')[0]  # Use email prefix as username
                
                cursor.execute('''
                    INSERT INTO users 
                    (email, username, full_name, role, is_approved, is_active, google_auth, 
                     profile_picture, created_at, last_login)
                    VALUES (?, ?, ?, ?, ?, 1, 1, ?, ?, ?)
                ''', (email, username, name, role, is_approved, picture, datetime.now(), datetime.now()))
                
                user_id = cursor.lastrowid
                
                user_data = {
                    'id': user_id,
                    'email': email,
                    'full_name': name,
                    'role': role,
                    'is_approved': is_approved,
                    'is_new_user': True
                }
            
            conn.commit()
            conn.close()
            
            return {'success': True, 'user': user_data}
            
        except Exception as e:
            return {'success': False, 'error': f'Database error: {str(e)}'}
    
    def generate_session_token(self, user_id):
        """Generate JWT session token"""
        payload = {
            'user_id': user_id,
            'exp': datetime.utcnow() + timedelta(hours=TOKEN_EXPIRY_HOURS),
            'iat': datetime.utcnow()
        }
        return jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    
    def process_google_login(self, credential_token):
        """Complete Google login process"""
        # Step 1: Verify Google token
        token_result = self.verify_token(credential_token)
        if not token_result['success']:
            return token_result
        
        # Step 2: Create/update user
        user_result = self.create_or_update_user(token_result['user'])
        if not user_result['success']:
            return user_result
        
        user_data = user_result['user']
        
        # Step 3: Check if user is approved
        if not user_data['is_approved']:
            return {
                'success': False, 
                'error': 'Account pending approval. USC employees are auto-approved.',
                'requires_approval': True
            }
        
        # Step 4: Generate session token
        session_token = self.generate_session_token(user_data['id'])
        
        # Step 5: Store session in database
        try:
            conn = sqlite3.connect(DATABASE)
            cursor = conn.cursor()
            
            expires_at = datetime.now() + timedelta(hours=TOKEN_EXPIRY_HOURS)
            cursor.execute('''
                INSERT INTO sessions (user_id, token, expires_at, created_at)
                VALUES (?, ?, ?, ?)
            ''', (user_data['id'], session_token, expires_at, datetime.now()))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            return {'success': False, 'error': f'Session creation failed: {str(e)}'}
        
        return {
            'success': True,
            'token': session_token,
            'user': user_data,
            'message': f"Welcome {user_data['full_name']}!" + 
                      (" (USC Employee)" if self.is_usc_employee(token_result['user']['email']) else "")
        }


# Initialize Google OAuth handler
google_oauth = GoogleOAuth()


# Dash callback function for Google OAuth
def handle_google_oauth_callback(credential_token):
    """Handle Google OAuth callback in Dash"""
    if not credential_token:
        return {
            'success': False,
            'error': 'No credential received',
            'session_data': None,
            'redirect': None,
            'alert': {'message': 'No Google credential received', 'color': 'danger'}
        }
    
    # Process the Google login
    result = google_oauth.process_google_login(credential_token)
    
    if result['success']:
        # Create session data for Dash
        session_data = {
            'token': result['token'],
            'user': {
                'id': result['user']['id'],
                'email': result['user']['email'],
                'full_name': result['user']['full_name'],
                'role': result['user']['role']
            }
        }
        
        return {
            'success': True,
            'session_data': session_data,
            'redirect': '/',  # Redirect to home page
            'alert': {'message': result['message'], 'color': 'success'}
        }
    
    else:
        return {
            'success': False,
            'error': result['error'],
            'session_data': None,
            'redirect': None,
            'alert': {'message': result['error'], 'color': 'danger'}
        }


# Database initialization (add to your existing init_database function)
def init_google_oauth_tables():
    """Initialize tables needed for Google OAuth"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Add columns to users table if they don't exist
    try:
        cursor.execute('ALTER TABLE users ADD COLUMN google_auth INTEGER DEFAULT 0')
    except sqlite3.OperationalError:
        pass  # Column already exists
    
    try:
        cursor.execute('ALTER TABLE users ADD COLUMN profile_picture TEXT')
    except sqlite3.OperationalError:
        pass  # Column already exists
    
    # Ensure sessions table exists
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            token TEXT NOT NULL,
            expires_at DATETIME NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    conn.commit()
    conn.close()


# Test function
def test_google_oauth():
    """Test Google OAuth setup"""
    print("Testing Google OAuth Setup...")
    print(f"Google Auth Available: {GOOGLE_AUTH_AVAILABLE}")
    print(f"Client ID: {GOOGLE_CLIENT_ID}")
    print(f"USC Domain: {USC_DOMAIN}")
    
    if GOOGLE_AUTH_AVAILABLE:
        print("✅ Google OAuth is ready to use")
    else:
        print("❌ Install Google Auth libraries first")
        print("Run: pip install google-auth google-auth-oauthlib google-auth-httplib2")


if __name__ == "__main__":
    test_google_oauth()
