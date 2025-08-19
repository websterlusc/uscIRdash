# auth_routes.py - FIXED VERSION
from flask import Flask, request, jsonify, session, redirect, url_for
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
        try:
            with open('login.html', 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            return "<h1>Login page not found</h1><p>Please ensure login.html exists in the project root.</p>"

    @app.route('/auth/google', methods=['POST'])
    def google_auth():
        """Handle Google OAuth authentication"""
        try:
            data = request.get_json()
            credential = data.get('credential')

            if not credential:
                return jsonify({'success': False, 'message': 'No credential provided'})

            print(f"🔍 Received Google credential: {len(credential)} characters")

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

            cursor.execute('SELECT id, is_active, is_approved, role FROM users WHERE email = ?', (email,))
            user_row = cursor.fetchone()

            if user_row:
                user_id, is_active, is_approved, role = user_row

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

                print(f"✅ Updated existing user: {email}")

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
                role = 'admin' if is_usc else 'user'

                print(f"✅ Created new user: {email} (USC: {is_usc})")

                if not is_usc:
                    conn.commit()
                    conn.close()
                    return jsonify({
                        'success': False,
                        'message': 'Account created but requires admin approval. Please contact ir@usc.edu.tt'
                    })

            conn.commit()
            conn.close()

            # Create session
            session_token = create_user_session(user_id, email)

            # Store in Flask session
            session['token'] = session_token
            session['user_id'] = user_id
            session['email'] = email
            session['authenticated'] = True

            print(f"✅ Session created: {session_token[:20]}...")
            print(f"✅ Flask session: {dict(session)}")

            return jsonify({
                'success': True,
                'message': 'Authentication successful',
                'redirect': '/',  # Redirect to home page (Dash will handle routing)
                'token': session_token,
                'user': {
                    'id': user_id,
                    'email': email,
                    'name': name
                }
            })

        except Exception as e:
            print(f"❌ Google auth error: {e}")
            import traceback
            traceback.print_exc()
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
                SELECT id, email, password_hash, is_active, is_approved, full_name
                FROM users 
                WHERE (email = ? OR username = ?)
            ''', (username, username))

            user_row = cursor.fetchone()

            if not user_row:
                conn.close()
                return jsonify({'success': False, 'message': 'Invalid credentials'})

            user_id, email, password_hash, is_active, is_approved, full_name = user_row

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
            session['authenticated'] = True

            return jsonify({
                'success': True,
                'message': 'Login successful',
                'redirect': '/',
                'token': session_token,
                'user': {
                    'id': user_id,
                    'email': email,
                    'name': full_name
                }
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

    @app.route('/auth/status')
    def auth_status():
        """Check authentication status"""
        try:
            token = session.get('token')
            if not token:
                return jsonify({'authenticated': False})

            # Validate token in database
            conn = sqlite3.connect(DATABASE)
            cursor = conn.cursor()

            cursor.execute('''
                SELECT u.id, u.email, u.full_name, u.role
                FROM users u
                JOIN sessions s ON u.id = s.user_id
                WHERE s.token = ? AND s.expires_at > datetime('now')
            ''', (token,))

            user_row = cursor.fetchone()
            conn.close()

            if user_row:
                return jsonify({
                    'authenticated': True,
                    'user': {
                        'id': user_row[0],
                        'email': user_row[1],
                        'full_name': user_row[2],
                        'role': user_row[3]
                    }
                })
            else:
                # Invalid token, clear session
                session.clear()
                return jsonify({'authenticated': False})

        except Exception as e:
            print(f"Auth status error: {e}")
            return jsonify({'authenticated': False})


if __name__ == '__main__':
    # For testing the auth routes independently
    app = create_auth_app()
    setup_auth_routes(app)
    app.run(debug=True, port=5000)