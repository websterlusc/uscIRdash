# auth_routes.py
from flask import Flask, render_template_string, request, jsonify, redirect, session
from google.oauth2 import id_token
from google.auth.transport import requests
import sqlite3
import secrets
import hashlib
from datetime import datetime, timedelta
import os

# Configuration
GOOGLE_CLIENT_ID = "890006312213-jb98t4ftcjgbvalgrrbo46sl9u77e524.apps.googleusercontent.com"
DATABASE = 'usc_ir_new.db'
SECRET_KEY = os.environ.get('SECRET_KEY', 'usc-ir-secret-key-2025-change-in-production')

def create_auth_app():
    """Create Flask app for authentication"""
    app = Flask(__name__)
    app.secret_key = SECRET_KEY
    
    return app

def verify_password(password, stored_hash):
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

def create_user_session(user_id, email):
    """Create a session token for the user"""
    session_token = secrets.token_urlsafe(32)
    expires_at = datetime.now() + timedelta(hours=8)
    
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Store session in database
    cursor.execute('''
        INSERT INTO sessions (user_id, token, expires_at)
        VALUES (?, ?, ?)
    ''', (user_id, session_token, expires_at))
    
    # Update last login
    cursor.execute('UPDATE users SET last_login = ? WHERE id = ?',
                   (datetime.now(), user_id))
    
    conn.commit()
    conn.close()
    
    return session_token

def setup_auth_routes(app):
    """Setup authentication routes"""
    
    @app.route('/login')
    def login_page():
        """Serve the standalone login page"""
        # Read the HTML file or return the template
        with open('login.html', 'r') as f:
            return f.read()
    
    @app.route('/auth/google', methods=['POST'])
    def google_auth():
        """Handle Google OAuth authentication"""
        try:
            data = request.get_json()
            credential = data.get('credential')
            
            if not credential:
                return jsonify({'success': False, 'message': 'No credential provided'})
            
            # Verify Google token
            idinfo = id_token.verify_oauth2_token(
                credential, 
                requests.Request(), 
                GOOGLE_CLIENT_ID
            )
            
            if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                return jsonify({'success': False, 'message': 'Invalid token issuer'})
            
            email = idinfo['email']
            name = idinfo['name']
            
            print(f"✅ Google authentication successful for: {email}")
            
            # Check if user exists or create new user
            conn = sqlite3.connect(DATABASE)
            cursor = conn.cursor()
            
            cursor.execute('SELECT id, is_active, is_approved FROM users WHERE email = ?', (email,))
            user_row = cursor.fetchone()
            
            if user_row:
                user_id, is_active, is_approved = user_row
                
                if not is_active:
                    conn.close()
                    return jsonify({'success': False, 'message': 'Account is deactivated'})
                
                if not is_approved:
                    conn.close()
                    return jsonify({'success': False, 'message': 'Account pending approval'})
                
                # Update user info
                cursor.execute('''
                    UPDATE users 
                    SET full_name = ?, google_auth = 1, last_login = ?
                    WHERE id = ?
                ''', (name, datetime.now(), user_id))
                
            else:
                # Create new user for USC employees
                is_usc = email.endswith('@usc.edu.tt')
                
                cursor.execute('''
                    INSERT INTO users 
                    (email, username, full_name, role, is_active, is_approved, google_auth)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (email, email.split('@')[0], name, 
                     'admin' if is_usc else 'user', 1, is_usc, 1))
                
                user_id = cursor.lastrowid
                
                if not is_usc:
                    conn.commit()
                    conn.close()
                    return jsonify({
                        'success': False, 
                        'message': 'Account created but requires admin approval. Please wait for approval.'
                    })
            
            conn.commit()
            conn.close()
            
            # Create session
            session_token = create_user_session(user_id, email)
            
            # Store in Flask session
            session['token'] = session_token
            session['user_id'] = user_id
            session['email'] = email
            
            return jsonify({
                'success': True,
                'message': 'Authentication successful',
                'redirect': '/dashboard',
                'token': session_token
            })
            
        except Exception as e:
            print(f"❌ Google auth error: {e}")
            return jsonify({'success': False, 'message': f'Authentication failed: {str(e)}'})
    
    @app.route('/auth/login', methods=['POST'])
    def regular_login():
        """Handle regular username/password login"""
        try:
            data = request.get_json()
            username = data.get('username')
            password = data.get('password')
            
            if not username or not password:
                return jsonify({'success': False, 'message': 'Username and password required'})
            
            conn = sqlite3.connect(DATABASE)
            cursor = conn.cursor()
            
            # Check user credentials
            cursor.execute('''
                SELECT id, email, password_hash, is_active, is_approved
                FROM users 
                WHERE (email = ? OR username = ?)
            ''', (username, username))
            
            user_row = cursor.fetchone()
            
            if not user_row:
                conn.close()
                return jsonify({'success': False, 'message': 'Invalid credentials'})
            
            user_id, email, password_hash, is_active, is_approved = user_row
            
            if not verify_password(password, password_hash):
                conn.close()
                return jsonify({'success': False, 'message': 'Invalid credentials'})
            
            if not is_active:
                conn.close()
                return jsonify({'success': False, 'message': 'Account is deactivated'})
            
            if not is_approved:
                conn.close()
                return jsonify({'success': False, 'message': 'Account pending approval'})
            
            conn.close()
            
            # Create session
            session_token = create_user_session(user_id, email)
            
            # Store in Flask session
            session['token'] = session_token
            session['user_id'] = user_id
            session['email'] = email
            
            return jsonify({
                'success': True,
                'message': 'Login successful',
                'redirect': '/dashboard',
                'token': session_token
            })
            
        except Exception as e:
            print(f"❌ Login error: {e}")
            return jsonify({'success': False, 'message': 'Login failed'})
    
    @app.route('/auth/logout', methods=['POST'])
    def logout():
        """Handle logout"""
        try:
            token = session.get('token')
            if token:
                # Remove from database
                conn = sqlite3.connect(DATABASE)
                cursor = conn.cursor()
                cursor.execute('DELETE FROM sessions WHERE token = ?', (token,))
                conn.commit()
                conn.close()
            
            # Clear Flask session
            session.clear()
            
            return jsonify({'success': True, 'redirect': '/login'})
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)})

if __name__ == '__main__':
    # For testing the auth routes independently
    app = create_auth_app()
    setup_auth_routes(app)
    app.run(debug=True, port=5000)
