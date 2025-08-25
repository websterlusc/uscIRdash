import os
import json
import sqlite3
import secrets
from datetime import datetime, timedelta
from flask import request, jsonify, session, redirect
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
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID', '890006312213-jb98t4ftcjgbvalgrrbo46sl9u77e524.apps.googleusercontent.com')

print(f"🔍 Google Client ID configured: {GOOGLE_CLIENT_ID[:20]}...")


def create_user_session(user_id, email):
    """Create a new user session with longer expiry"""
    session_token = secrets.token_urlsafe(32)
    expires_at = datetime.now() + timedelta(days=30)  # 30-day session

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # Remove old sessions for this user (optional - limit concurrent sessions)
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

    return session_token


def validate_session(session_token):
    """Validate session token and return user info"""
    if not session_token:
        return None

    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT u.id, u.email, u.username, u.full_name, u.role, u.is_active, u.is_approved, s.expires_at
            FROM users u
            JOIN user_sessions s ON u.id = s.user_id
            WHERE s.session_token = ?
        ''', (session_token,))

        result = cursor.fetchone()
        conn.close()

        if not result:
            print(f"❌ Session not found: {session_token[:20]}...")
            return None

        user_id, email, username, full_name, role, is_active, is_approved, expires_at = result

        # Check if session expired
        expires_at_dt = datetime.fromisoformat(expires_at)
        if expires_at_dt < datetime.now():
            print(f"❌ Session expired: {session_token[:20]}...")
            # Clean up expired session
            conn = sqlite3.connect(DATABASE)
            cursor = conn.cursor()
            cursor.execute('DELETE FROM user_sessions WHERE session_token = ?', (session_token,))
            conn.commit()
            conn.close()
            return None

        # Check user status
        if not is_active or not is_approved:
            print(f"❌ User inactive or not approved: {email}")
            return None

        return {
            'id': user_id,
            'email': email,
            'username': username,
            'full_name': full_name,
            'role': role
        }

    except Exception as e:
        print(f"❌ Session validation error: {e}")
        return None


def change_user_password(user_id, current_password, new_password):
    """Change user password after verifying current password"""
    import bcrypt

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute('SELECT password_hash FROM users WHERE id = ?', (user_id,))
    result = cursor.fetchone()

    if not result:
        conn.close()
        return {'success': False, 'message': 'User not found'}

    # Verify current password
    if not bcrypt.checkpw(current_password.encode('utf-8'), result[0].encode('utf-8')):
        conn.close()
        return {'success': False, 'message': 'Current password is incorrect'}

    # Update to new password
    new_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    cursor.execute('UPDATE users SET password_hash = ? WHERE id = ?', (new_hash, user_id))
    conn.commit()
    conn.close()

    return {'success': True, 'message': 'Password changed successfully'}


def setup_auth_routes(app):
    """Setup authentication routes with improved flow"""

    @app.route('/login')
    def login_page():
        """Serve the standalone login page"""
        try:
            # Check if already authenticated
            if 'authenticated' in session and session['authenticated']:
                return redirect('/')

            with open('login.html', 'r', encoding='utf-8') as f:
                html_content = f.read()
                # Replace the placeholder with actual Google Client ID
                html_content = html_content.replace('638032897407-f73s5mnqnl5aaeavth6e37bfguhr8e1m.apps.googleusercontent.com', GOOGLE_CLIENT_ID)
                return html_content
        except FileNotFoundError:
            # Fallback if login.html doesn't exist
            return f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>USC IR Login</title>
                <script src="https://accounts.google.com/gsi/client" async defer></script>
                <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
            </head>
            <body class="bg-light">
                <div class="container">
                    <div class="row justify-content-center">
                        <div class="col-md-6">
                            <div class="card mt-5">
                                <div class="card-header text-center bg-success text-white">
                                    <h3>USC IR Login</h3>
                                </div>
                                <div class="card-body">
                                    <div class="alert alert-warning">
                                        <h4>Login Configuration Needed</h4>
                                        <p>Please ensure login.html exists in the project root.</p>
                                        <p>Google Client ID: {GOOGLE_CLIENT_ID[:20]}...</p>
                                    </div>
                                    <a href="/" class="btn btn-primary">Back to Home</a>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </body>
            </html>
            """

    @app.route('/auth/google', methods=['POST'])
    def google_auth():
        """Handle Google OAuth authentication with improved error handling"""
        if not GOOGLE_AUTH_AVAILABLE:
            return jsonify({'success': False, 'message': 'Google Auth not configured'})

        try:
            data = request.get_json()
            credential = data.get('credential')

            if not credential:
                print("❌ No credential provided")
                return jsonify({'success': False, 'message': 'No credential provided'})

            print(f"🔍 Received Google credential: {len(credential)} characters")

            # Verify Google token
            idinfo = id_token.verify_oauth2_token(
                credential,
                requests.Request(),
                GOOGLE_CLIENT_ID
            )

            if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                print("❌ Invalid token issuer")
                return jsonify({'success': False, 'message': 'Invalid token issuer'})

            email = idinfo['email']
            name = idinfo['name']
            google_id = idinfo['sub']

            print(f"✅ Google authentication successful for: {email}")

            # Database operations
            conn = sqlite3.connect(DATABASE)
            cursor = conn.cursor()

            cursor.execute('SELECT id, is_active, is_approved, role FROM users WHERE email = ?', (email,))
            user_row = cursor.fetchone()

            if user_row:
                user_id, is_active, is_approved, role = user_row

                if not is_active:
                    conn.close()
                    print(f"❌ Account deactivated: {email}")
                    return jsonify({'success': False, 'message': 'Account is deactivated'})

                if not is_approved:
                    conn.close()
                    print(f"❌ Account not approved: {email}")
                    return jsonify({'success': False, 'message': 'Account pending approval'})

                # Update user info and last login
                cursor.execute('''
                    UPDATE users 
                    SET full_name = ?, google_auth = 1, last_login = ?, google_id = ?
                    WHERE id = ?
                ''', (name, datetime.now(), google_id, user_id))

                print(f"✅ Updated existing user: {email}")

            else:
                # Create new user
                is_usc = email.endswith('@usc.edu.tt')

                cursor.execute('''
                    INSERT INTO users 
                    (email, username, full_name, role, is_active, is_approved, google_auth, google_id, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (email, email.split('@')[0], name,
                      'admin' if is_usc else 'user', 1, is_usc, 1, google_id, datetime.now()))

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

            # Create session token
            session_token = create_user_session(user_id, email)

            # Store in Flask session for backup
            session['token'] = session_token
            session['user_id'] = user_id
            session['email'] = email
            session['authenticated'] = True
            session.permanent = True  # Make session persistent

            print(f"✅ Session created: {session_token[:20]}...")

            # Return success with all necessary data
            return jsonify({
                'success': True,
                'message': 'Authentication successful',
                'redirect': '/dashboard',
                'token': session_token,
                'user': {
                    'id': user_id,
                    'email': email,
                    'name': name,
                    'role': role
                }
            })

        except Exception as e:
            print(f"❌ Google auth error: {e}")
            traceback.print_exc()
            return jsonify({'success': False, 'message': f'Authentication failed: {str(e)}'})

    @app.route('/auth/logout', methods=['POST'])
    def logout():
        """Handle user logout"""
        try:
            # Clear Flask session
            session.clear()

            # If token provided, remove from database
            data = request.get_json() or {}
            token = data.get('token')

            if token:
                conn = sqlite3.connect(DATABASE)
                cursor = conn.cursor()
                cursor.execute('DELETE FROM user_sessions WHERE session_token = ?', (token,))
                conn.commit()
                conn.close()
                print(f"✅ Session token removed: {token[:20]}...")

            return jsonify({'success': True, 'message': 'Logged out successfully'})

        except Exception as e:
            print(f"❌ Logout error: {e}")
            return jsonify({'success': False, 'message': 'Logout failed'})

    @app.route('/auth/validate', methods=['POST'])
    def validate_token():
        """Validate session token (for AJAX calls)"""
        try:
            data = request.get_json()
            token = data.get('token')

            if not token:
                return jsonify({'valid': False})

            user = validate_session(token)
            if user:
                return jsonify({
                    'valid': True,
                    'user': {
                        'id': user['id'],
                        'email': user['email'],
                        'name': user['full_name'],
                        'role': user['role']
                    }
                })
            else:
                return jsonify({'valid': False})

        except Exception as e:
            print(f"❌ Token validation error: {e}")
            return jsonify({'valid': False})

    @app.route('/auth/status')
    def auth_status():
        """Check current authentication status"""
        try:
            if 'authenticated' in session and session['authenticated']:
                token = session.get('token')
                if token:
                    user = validate_session(token)
                    if user:
                        return jsonify({
                            'authenticated': True,
                            'user': {
                                'id': user['id'],
                                'email': user['email'],
                                'name': user['full_name'],
                                'role': user['role']
                            },
                            'token': token
                        })

            return jsonify({'authenticated': False})

        except Exception as e:
            print(f"❌ Auth status check error: {e}")
            return jsonify({'authenticated': False})

    @app.route('/auth/regular', methods=['POST'])
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
                SELECT id, email, password_hash, is_active, is_approved, full_name, role
                FROM users 
                WHERE (email = ? OR username = ?)
            ''', (username, username))

            user_row = cursor.fetchone()

            if not user_row:
                conn.close()
                return jsonify({'success': False, 'message': 'Invalid credentials'})

            user_id, email, password_hash, is_active, is_approved, full_name, role = user_row

            # Verify password
            import bcrypt
            if not bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8')):
                conn.close()
                return jsonify({'success': False, 'message': 'Invalid credentials'})

            # Check user status
            if not is_active:
                conn.close()
                return jsonify({'success': False, 'message': 'Account is deactivated'})

            if not is_approved:
                conn.close()
                return jsonify({'success': False, 'message': 'Account pending approval'})

            # Update last login
            cursor.execute('UPDATE users SET last_login = ? WHERE id = ?', (datetime.now(), user_id))
            conn.commit()
            conn.close()

            # Create session
            session_token = create_user_session(user_id, email)

            # Store in Flask session
            session['token'] = session_token
            session['user_id'] = user_id
            session['email'] = email
            session['authenticated'] = True
            session.permanent = True

            return jsonify({
                'success': True,
                'message': 'Login successful',
                'redirect': '/dashboard',
                'token': session_token,
                'user': {
                    'id': user_id,
                    'email': email,
                    'name': full_name,
                    'role': role
                }
            })

        except Exception as e:
            print(f"❌ Regular login error: {e}")
            return jsonify({'success': False, 'message': 'Login failed'})

    @app.route('/auth/register', methods=['POST'])
    def register():
        """Handle user registration"""
        try:
            data = request.get_json()
            email = data.get('email')
            username = data.get('username')
            password = data.get('password')
            full_name = data.get('full_name')

            if not all([email, username, password, full_name]):
                return jsonify({'success': False, 'message': 'All fields are required'})

            # Check if user already exists
            conn = sqlite3.connect(DATABASE)
            cursor = conn.cursor()

            cursor.execute('SELECT id FROM users WHERE email = ? OR username = ?', (email, username))
            if cursor.fetchone():
                conn.close()
                return jsonify({'success': False, 'message': 'Email or username already exists'})

            # Hash password
            import bcrypt
            password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

            # Determine if USC employee (auto-approve)
            is_usc = email.endswith('@usc.edu.tt')

            # Insert new user
            cursor.execute('''
                INSERT INTO users 
                (email, username, full_name, password_hash, role, is_active, is_approved, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (email, username, full_name, password_hash,
                  'admin' if is_usc else 'user', 1, is_usc, datetime.now()))

            conn.commit()
            conn.close()

            if is_usc:
                return jsonify({
                    'success': True,
                    'message': 'Account created and approved! You can now log in.'
                })
            else:
                return jsonify({
                    'success': True,
                    'message': 'Account created! Admin approval required before you can log in.'
                })

        except Exception as e:
            print(f"❌ Registration error: {e}")
            return jsonify({'success': False, 'message': 'Registration failed'})

    @app.route('/assets/<path:filename>')
    def serve_assets(filename):
        """Serve static assets"""
        from flask import send_from_directory
        try:
            return send_from_directory('assets', filename)
        except:
            # Return a 404 or placeholder if file not found
            return '', 404

    print("✅ Auth routes configured successfully")
    print(
        f"✅ Google Client ID: {GOOGLE_CLIENT_ID[:20]}..." if GOOGLE_CLIENT_ID != '890006312213-jb98t4ftcjgbvalgrrbo46sl9u77e524.apps.googleusercontent.com' else "⚠️ Google Client ID not configured")