# auth_routes.py - Updated for new login system

import os
import sqlite3
import secrets
from datetime import datetime, timedelta
from flask import request, jsonify, session
import traceback

# Google Auth imports
try:
    from google.auth.transport import requests
    from google.oauth2 import id_token

    GOOGLE_AUTH_AVAILABLE = True
except ImportError:
    print(
        "⚠️ Google Auth libraries not installed. Run: pip install google-auth google-auth-oauthlib google-auth-httplib2")
    GOOGLE_AUTH_AVAILABLE = False

# Configuration
DATABASE = 'usc_portal.db'
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID',
                             '890006312213-3k7f200g3a94je1j9trfjru716v3kidc.apps.googleusercontent.com')

print(f"🔍 Auth routes loaded with Client ID: {GOOGLE_CLIENT_ID[:20]}...")


def create_user_session(user_id, email):
    """Create a new user session"""
    session_token = secrets.token_urlsafe(32)
    expires_at = datetime.now() + timedelta(days=7)  # 7-day session

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # Remove old sessions for this user (keep only latest)
    cursor.execute('DELETE FROM user_sessions WHERE user_id = ?', (user_id,))

    # Create new session
    cursor.execute('''
        INSERT INTO user_sessions (session_token, user_id, user_email, expires_at, created_at)
        VALUES (?, ?, ?, ?, ?)
    ''', (session_token, user_id, email, expires_at, datetime.now()))

    # Update last login
    cursor.execute('UPDATE users SET last_login = ? WHERE id = ?',
                   (datetime.now(), user_id))

    conn.commit()
    conn.close()

    print(f"✅ Session created for user {user_id}: {session_token[:20]}...")
    return session_token


def setup_auth_routes(app):
    """Setup authentication routes"""

    @app.route('/login')
    def login_page():
        """Serve the new login page"""
        try:
            # Check if already authenticated
            if session.get('authenticated'):
                print("User already authenticated, redirecting")
                return '''
                <script>
                    window.location.href = "http://localhost:8050/dashboard";
                </script>
                '''

            # Serve the login page
            with open('login.html', 'r', encoding='utf-8') as f:
                return f.read()

        except FileNotFoundError:
            return '''
            <h1>❌ Login Page Not Found</h1>
            <p>Please ensure login.html exists in the project root directory.</p>
            <p>Expected files:</p>
            <ul>
                <li>login.html</li>
                <li>auth_routes.py</li>
                <li>app.py</li>
            </ul>
            '''

    @app.route('/auth/google', methods=['POST'])
    def google_auth():
        """Handle Google OAuth authentication"""
        if not GOOGLE_AUTH_AVAILABLE:
            return jsonify({
                'success': False,
                'message': 'Google authentication not available. Missing dependencies.'
            })

        try:
            data = request.get_json()
            if not data:
                return jsonify({'success': False, 'message': 'No data provided'})

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

            # Validate token issuer
            if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                return jsonify({'success': False, 'message': 'Invalid token issuer'})

            email = idinfo['email']
            name = idinfo['name']
            google_id = idinfo['sub']

            print(f"✅ Google authentication successful for: {email}")

            # Database operations
            conn = sqlite3.connect(DATABASE)
            cursor = conn.cursor()

            # Check if user exists
            cursor.execute('''
                SELECT id, is_active, is_approved, role, full_name 
                FROM users WHERE email = ?
            ''', (email,))
            user_row = cursor.fetchone()

            if user_row:
                user_id, is_active, is_approved, role, full_name = user_row

                # Check user status
                if not is_active:
                    conn.close()
                    return jsonify({
                        'success': False,
                        'message': 'Account is deactivated. Please contact support.'
                    })

                if not is_approved:
                    conn.close()
                    return jsonify({
                        'success': False,
                        'message': 'Account pending approval. Please wait for admin approval.'
                    })

                # Update user info
                cursor.execute('''
                    UPDATE users 
                    SET full_name = ?, google_auth = 1, last_login = ?
                    WHERE id = ?
                ''', (name, datetime.now(), user_id))

                print(f"✅ Updated existing user: {email}")

            else:
                # Create new user
                is_usc = email.endswith('@usc.edu.tt')
                role = 'admin' if is_usc else 'user'
                is_approved = 1 if is_usc else 0  # USC employees auto-approved

                cursor.execute('''
                    INSERT INTO users 
                    (email, username, full_name, role, is_active, is_approved, google_auth, created_at, last_login)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (email, email.split('@')[0], name, role, 1, is_approved, 1,
                      datetime.now(), datetime.now()))

                user_id = cursor.lastrowid
                print(f"✅ Created new user: {email} (USC: {is_usc}, Auto-approved: {is_approved})")

                if not is_approved:
                    conn.commit()
                    conn.close()
                    return jsonify({
                        'success': False,
                        'message': 'Account created but requires admin approval. You will be notified when approved.'
                    })

            conn.commit()
            conn.close()

            # Create session
            session_token = create_user_session(user_id, email)

            # Store in Flask session
            session.permanent = True
            session['authenticated'] = True
            session['user_id'] = user_id
            session['email'] = email
            session['token'] = session_token
            session['full_name'] = name

            print(f"✅ Session stored in Flask: {dict(session)}")

            # Return success response
            return jsonify({
                'success': True,
                'message': 'Authentication successful',
                'redirect': 'http://localhost:8050/dashboard',
                'token': session_token,
                'user': {
                    'id': user_id,
                    'email': email,
                    'name': name,
                    'role': role if 'role' in locals() else 'user'
                }
            })

        except Exception as e:
            print(f"❌ Google auth error: {e}")
            traceback.print_exc()
            return jsonify({
                'success': False,
                'message': f'Authentication failed: {str(e)}'
            })

    @app.route('/auth/status')
    def auth_status():
        """Check authentication status"""
        try:
            if session.get('authenticated'):
                return jsonify({
                    'authenticated': True,
                    'user': {
                        'email': session.get('email'),
                        'name': session.get('full_name'),
                        'id': session.get('user_id')
                    }
                })
            else:
                return jsonify({'authenticated': False})
        except Exception as e:
            return jsonify({'authenticated': False, 'error': str(e)})

    @app.route('/auth/logout', methods=['POST', 'GET'])
    def logout():
        """Handle logout"""
        try:
            token = session.get('token')
            if token:
                # Remove from database
                conn = sqlite3.connect(DATABASE)
                cursor = conn.cursor()
                cursor.execute('DELETE FROM user_sessions WHERE session_token = ?', (token,))
                conn.commit()
                conn.close()
                print(f"✅ Removed session from database: {token[:20]}...")

            # Clear Flask session
            session.clear()
            print("✅ Cleared Flask session")

            if request.method == 'GET':
                return '''
                <script>
                    localStorage.removeItem('auth_token');
                    localStorage.removeItem('user_data');
                    window.location.href = "/login";
                </script>
                '''
            else:
                return jsonify({'success': True, 'redirect': '/login'})

        except Exception as e:
            print(f"❌ Logout error: {e}")
            return jsonify({'success': False, 'message': str(e)})

    @app.route('/debug/auth')
    def debug_auth():
        """Debug endpoint"""
        return f'''
        <h1>🔧 Authentication Debug</h1>
        <h3>Configuration:</h3>
        <ul>
            <li>Google Client ID: {GOOGLE_CLIENT_ID[:30]}...</li>
            <li>Google Auth Available: {GOOGLE_AUTH_AVAILABLE}</li>
            <li>Database: {DATABASE}</li>
        </ul>
        <h3>Current Session:</h3>
        <pre>{dict(session)}</pre>
        <h3>Test Links:</h3>
        <ul>
            <li><a href="/login">Login Page</a></li>
            <li><a href="/auth/status">Auth Status</a></li>
            <li><a href="/auth/logout">Logout</a></li>
        </ul>
        '''

    print("✅ Authentication routes configured")