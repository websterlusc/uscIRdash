# auth_routes.py - Fixed version with better session sync

import os
import sqlite3
import secrets
from datetime import datetime, timedelta
from flask import request, jsonify, session, redirect, make_response
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
MAIN_APP_URL = "http://localhost:8050"

print(f"🔍 Auth routes loaded with Client ID: {GOOGLE_CLIENT_ID[:20]}...")


def create_user_session(user_id, email):
    """Create a new user session"""
    session_token = secrets.token_urlsafe(32)
    expires_at = datetime.now() + timedelta(days=7)

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # Remove old sessions for this user
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
    """Setup authentication routes with fixed session handling"""

    @app.route('/login')
    def login_page():
        """Serve the login page with proper caching headers"""
        try:
            # Check if already authenticated
            if session.get('authenticated'):
                print("User already authenticated, redirecting to main app")
                return redirect(f"{MAIN_APP_URL}/dashboard")

            # Read and serve login page with no-cache headers
            with open('login.html', 'r', encoding='utf-8') as f:
                content = f.read()

            # Create response with no-cache headers to prevent the "small page" issue
            response = make_response(content)
            response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '0'

            return response

        except FileNotFoundError:
            return make_response('''
            <h1>❌ Login Page Not Found</h1>
            <p>Please ensure login.html exists in the project root directory.</p>
            <p><a href="/">Back to Home</a></p>
            ''', 404)

    @app.route('/auth/google', methods=['POST'])
    def google_auth():
        """Handle Google OAuth authentication with better session sync"""
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

            else:
                # Create new user
                is_usc = email.endswith('@usc.edu.tt')
                role = 'admin' if is_usc else 'user'
                is_approved = 1 if is_usc else 0

                cursor.execute('''
                    INSERT INTO users 
                    (email, username, full_name, role, is_active, is_approved, google_auth, created_at, last_login)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (email, email.split('@')[0], name, role, 1, is_approved, 1,
                      datetime.now(), datetime.now()))

                user_id = cursor.lastrowid

                if not is_approved:
                    conn.commit()
                    conn.close()
                    return jsonify({
                        'success': False,
                        'message': 'Account created but requires admin approval.'
                    })

            conn.commit()
            conn.close()

            # Create session token
            session_token = create_user_session(user_id, email)

            # Store comprehensive session data in Flask
            session.permanent = True
            session.clear()  # Clear any old session data
            session['authenticated'] = True
            session['user_id'] = user_id
            session['email'] = email
            session['token'] = session_token
            session['full_name'] = name
            session['role'] = role if 'role' in locals() else 'user'
            session['login_time'] = datetime.now().isoformat()

            print(f"✅ Flask session created: user_id={user_id}, email={email}")

            # Return success with detailed user info for Dash
            return jsonify({
                'success': True,
                'message': 'Authentication successful',
                'redirect': f'{MAIN_APP_URL}/',  # Redirect to root, let Dash handle routing
                'token': session_token,
                'user': {
                    'id': user_id,
                    'email': email,
                    'full_name': name,
                    'role': role if 'role' in locals() else 'user'
                },
                'session_data': {  # Data for Dash session store
                    'token': session_token,
                    'user_id': user_id,
                    'email': email,
                    'full_name': name,
                    'role': role if 'role' in locals() else 'user',
                    'authenticated': True
                }
            })

        except Exception as e:
            print(f"❌ Google auth error: {e}")
            traceback.print_exc()
            return jsonify({
                'success': False,
                'message': f'Authentication failed: {str(e)}'
            })

    @app.route('/auth/session-data')
    def get_session_data():
        """Get current session data for Dash synchronization"""
        try:
            if session.get('authenticated'):
                return jsonify({
                    'authenticated': True,
                    'token': session.get('token'),
                    'user_id': session.get('user_id'),
                    'email': session.get('email'),
                    'full_name': session.get('full_name'),
                    'role': session.get('role', 'user')
                })
            else:
                return jsonify({'authenticated': False})
        except Exception as e:
            print(f"Session data error: {e}")
            return jsonify({'authenticated': False, 'error': str(e)})

    @app.route('/auth/status')
    def auth_status():
        """Check authentication status"""
        return get_session_data()  # Same as session-data endpoint

    @app.route('/auth/logout', methods=['POST', 'GET'])
    def logout():
        """Handle logout with complete session cleanup"""
        try:
            print("🔍 Logout initiated")

            token = session.get('token')
            user_id = session.get('user_id')

            if token:
                # Remove from database
                conn = sqlite3.connect(DATABASE)
                cursor = conn.cursor()
                cursor.execute('DELETE FROM user_sessions WHERE session_token = ?', (token,))
                rows_affected = cursor.rowcount
                conn.commit()
                conn.close()
                print(f"✅ Removed {rows_affected} sessions from database")

            # Clear Flask session completely
            session.clear()
            print("✅ Cleared Flask session")

            if request.method == 'GET':
                # For direct logout links
                response = make_response(f'''
                <html>
                <head><title>Logged Out</title></head>
                <body>
                    <h2>✅ Logged Out Successfully</h2>
                    <p>You have been logged out. Redirecting to login page...</p>
                    <script>
                        // Clear any client-side storage
                        localStorage.removeItem('auth_token');
                        localStorage.removeItem('user_data');
                        sessionStorage.clear();

                        // Redirect after clearing
                        setTimeout(() => {{
                            window.location.href = "{MAIN_APP_URL}/";
                        }}, 2000);
                    </script>
                </body>
                </html>
                ''')

                # Clear cookies
                response.set_cookie('session', '', expires=0, domain=None, path='/')
                return response
            else:
                # For AJAX requests
                return jsonify({
                    'success': True,
                    'message': 'Logged out successfully',
                    'redirect': f'{MAIN_APP_URL}/'
                })

        except Exception as e:
            print(f"❌ Logout error: {e}")
            return jsonify({'success': False, 'message': str(e)})

    @app.route('/debug/auth')
    def debug_auth():
        """Enhanced debug endpoint"""
        try:
            # Check database sessions
            conn = sqlite3.connect(DATABASE)
            cursor = conn.cursor()

            cursor.execute('''
                SELECT COUNT(*) as total_sessions,
                       COUNT(CASE WHEN expires_at > datetime('now') THEN 1 END) as active_sessions
                FROM user_sessions
            ''')
            session_stats = cursor.fetchone()

            cursor.execute('''
                SELECT user_email, session_token, expires_at, created_at
                FROM user_sessions 
                WHERE expires_at > datetime('now')
                ORDER BY created_at DESC LIMIT 5
            ''')
            recent_sessions = cursor.fetchall()

            conn.close()

            return f'''
            <html>
            <head><title>Authentication Debug</title></head>
            <body>
                <h1>🔧 Authentication Debug</h1>

                <h3>Configuration:</h3>
                <ul>
                    <li>Google Client ID: {GOOGLE_CLIENT_ID[:30]}...</li>
                    <li>Google Auth Available: {GOOGLE_AUTH_AVAILABLE}</li>
                    <li>Database: {DATABASE}</li>
                    <li>Main App URL: {MAIN_APP_URL}</li>
                </ul>

                <h3>Current Flask Session:</h3>
                <pre>{dict(session)}</pre>

                <h3>Database Sessions:</h3>
                <ul>
                    <li>Total Sessions: {session_stats[0] if session_stats else 0}</li>
                    <li>Active Sessions: {session_stats[1] if session_stats else 0}</li>
                </ul>

                <h3>Recent Active Sessions:</h3>
                <ul>
                    {
            ''.join([f'<li>{s[0]} - {s[1][:20]}... (expires: {s[2]})</li>' for s in recent_sessions])
            if recent_sessions else '<li>No active sessions</li>'
            }
                </ul>

                <h3>Test Links:</h3>
                <ul>
                    <li><a href="/login">Login Page</a></li>
                    <li><a href="/auth/session-data">Session Data</a></li>
                    <li><a href="/auth/logout">Logout</a></li>
                    <li><a href="{MAIN_APP_URL}">Main App</a></li>
                </ul>

                <h3>Clear Session Test:</h3>
                <button onclick="fetch('/auth/logout', {{method: 'POST'}}).then(() => location.reload())">
                    Clear Session
                </button>
            </body>
            </html>
            '''
        except Exception as e:
            return f'<h1>Debug Error: {e}</h1>'

    print("✅ Authentication routes configured with session sync")