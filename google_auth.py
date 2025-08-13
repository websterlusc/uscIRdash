# google_auth.py
import os
import json
from google.auth.transport import requests
from google.oauth2 import id_token
import sqlite3
from datetime import datetime, timedelta
import jwt

# Google OAuth Configuration
GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID', 'your-google-client-id.googleusercontent.com')
USC_DOMAIN = 'usc.edu.tt'


def verify_google_token(token):
    """Verify Google ID token and extract user info"""
    try:
        # Verify the token
        idinfo = id_token.verify_oauth2_token(
            token, requests.Request(), GOOGLE_CLIENT_ID)

        # Verify the issuer
        if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            raise ValueError('Wrong issuer.')

        # Extract user information
        user_info = {
            'email': idinfo['email'],
            'name': idinfo['name'],
            'picture': idinfo.get('picture', ''),
            'email_verified': idinfo.get('email_verified', False),
            'domain': idinfo['email'].split('@')[1] if '@' in idinfo['email'] else ''
        }

        return {'success': True, 'user': user_info}

    except ValueError as e:
        return {'success': False, 'error': str(e)}


def is_usc_employee(email):
    """Check if email belongs to USC domain"""
    return email.endswith(f'@{USC_DOMAIN}')


def create_or_update_google_user(user_info):
    """Create or update user from Google OAuth"""
    conn = sqlite3.connect('usc_ir_new.db')
    cursor = conn.cursor()

    try:
        email = user_info['email']
        name = user_info['name']

        # Check if user exists
        cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
        existing_user = cursor.fetchone()

        if existing_user:
            # Update existing user
            cursor.execute('''
                UPDATE users 
                SET full_name = ?, last_login = ?, google_auth = 1, profile_picture = ?
                WHERE email = ?
            ''', (name, datetime.now(), user_info.get('picture', ''), email))

            user_id = existing_user[0]
        else:
            # Determine role based on USC domain
            role = 'employee' if is_usc_employee(email) else 'guest'
            status = 'active' if is_usc_employee(email) else 'pending'

            # Create new user
            cursor.execute('''
                INSERT INTO users 
                (email, username, full_name, role, status, google_auth, profile_picture, created_at, last_login)
                VALUES (?, ?, ?, ?, ?, 1, ?, ?, ?)
            ''', (email, email.split('@')[0], name, role, status,
                  user_info.get('picture', ''), datetime.now(), datetime.now()))

            user_id = cursor.lastrowid

        conn.commit()

        # Get updated user info
        cursor.execute('''
            SELECT id, email, username, full_name, role, status, google_auth, profile_picture
            FROM users WHERE id = ?
        ''', (user_id,))

        user = cursor.fetchone()
        conn.close()

        if user:
            return {
                'success': True,
                'user': {
                    'id': user[0],
                    'email': user[1],
                    'username': user[2],
                    'full_name': user[3],
                    'role': user[4],
                    'status': user[5],
                    'google_auth': bool(user[6]),
                    'profile_picture': user[7]
                }
            }
        else:
            return {'success': False, 'error': 'Failed to retrieve user after creation'}

    except Exception as e:
        conn.rollback()
        conn.close()
        return {'success': False, 'error': str(e)}


def has_financial_access(user):
    """Check if user has access to financial data"""
    # Only admins and specific roles have financial access
    if user['role'] in ['admin', 'finance_admin']:
        return True

    # Check if user has specific financial permissions
    conn = sqlite3.connect('usc_ir_new.db')
    cursor = conn.cursor()

    cursor.execute('''
        SELECT financial_access FROM user_permissions 
        WHERE user_id = ?
    ''', (user['id'],))

    result = cursor.fetchone()
    conn.close()

    return result and result[0] == 1


# Add this to your database initialization
def init_google_auth_tables():
    """Initialize tables for Google authentication"""
    conn = sqlite3.connect('usc_ir_new.db')
    cursor = conn.cursor()

    # Add Google auth columns to users table if they don't exist
    try:
        cursor.execute('ALTER TABLE users ADD COLUMN google_auth INTEGER DEFAULT 0')
    except sqlite3.OperationalError:
        pass  # Column already exists

    try:
        cursor.execute('ALTER TABLE users ADD COLUMN profile_picture TEXT')
    except sqlite3.OperationalError:
        pass  # Column already exists

    # Create user permissions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_permissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            financial_access INTEGER DEFAULT 0,
            admin_access INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    conn.commit()
    conn.close()

# Environment variables you need to set:
# GOOGLE_CLIENT_ID=your-google-client-id.googleusercontent.com