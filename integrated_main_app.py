# integrated_main_app.py - Single server with built-in authentication

import dash
from dash import dcc, html, Input, Output, State, callback_context
import dash_bootstrap_components as dbc
from flask import Flask, request, session, redirect, jsonify, make_response
import sqlite3
import secrets
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Google Auth imports
try:
    from google.auth.transport import requests as google_requests
    from google.oauth2 import id_token
    GOOGLE_AUTH_AVAILABLE = True
except ImportError:
    print("⚠️ Google Auth not available")
    GOOGLE_AUTH_AVAILABLE = False

# Configuration
DATABASE = 'usc_portal.db'
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID', 'your-google-client-id')

# Create Flask server
server = Flask(__name__)
server.secret_key = os.getenv('SECRET_KEY', 'change-in-production')
server.permanent_session_lifetime = timedelta(days=7)

# Create Dash app using the Flask server
app = dash.Dash(__name__, server=server, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "USC Institutional Research"

# ==================== DATABASE SETUP ====================

def init_database():
    """Initialize database"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            full_name TEXT,
            role TEXT DEFAULT 'user',
            is_active INTEGER DEFAULT 1,
            google_id TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_token TEXT UNIQUE NOT NULL,
            user_id INTEGER NOT NULL,
            user_email TEXT NOT NULL,
            expires_at TIMESTAMP NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

# ==================== AUTHENTICATION FUNCTIONS ====================

def get_current_user():
    """Get current authenticated user from Flask session"""
    if not session.get('authenticated'):
        return None
    
    return {
        'id': session.get('user_id'),
        'email': session.get('email'),
        'full_name': session.get('full_name', session.get('email')),
        'role': session.get('role', 'user')
    }

def create_or_get_user(email, full_name, google_id):
    """Create or get user from database"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Check if user exists
    cursor.execute('SELECT id, role, is_active FROM users WHERE email = ?', (email,))
    result = cursor.fetchone()
    
    if result:
        user_id, role, is_active = result
        if not is_active:
            conn.close()
            return None, "Account is deactivated"
        
        # Update last login
        cursor.execute('UPDATE users SET last_login = ?, full_name = ? WHERE id = ?',
                      (datetime.now(), full_name, user_id))
        conn.commit()
        
    else:
        # Create new user
        role = 'admin' if email.endswith('@usc.edu.tt') else 'user'
        cursor.execute('''
            INSERT INTO users (email, full_name, role, google_id, created_at, last_login)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (email, full_name, role, google_id, datetime.now(), datetime.now()))
        
        user_id = cursor.lastrowid
        conn.commit()
    
    conn.close()
    return user_id, role

# ==================== FLASK ROUTES ====================

@server.route('/login')
def login_page():
    """Serve login page"""
    if session.get('authenticated'):
        return redirect('/')
    
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>USC IR - Login</title>
        <script src="https://accounts.google.com/gsi/client" async defer></script>
        <style>
            body { font-family: Arial, sans-serif; display: flex; justify-content: center; align-items: center; min-height: 100vh; margin: 0; background: linear-gradient(135deg, #2E8B57 0%, #1B5E20 100%); }
            .login-container { background: white; padding: 2rem; border-radius: 15px; text-align: center; max-width: 400px; box-shadow: 0 15px 35px rgba(0,0,0,0.1); }
            .status { margin-top: 1rem; padding: 0.75rem; border-radius: 8px; }
            .status.success { background: #d4edda; color: #155724; }
            .status.error { background: #f8d7da; color: #721c24; }
        </style>
    </head>
    <body>
        <div class="login-container">
            <h2>🏛️ USC Institutional Research</h2>
            <p>Sign in with your USC Google account</p>
            <div id="g_id_signin"></div>
            <div id="status" class="status" style="display:none;"></div>
        </div>
        
        <script>
            const CLIENT_ID = "''' + GOOGLE_CLIENT_ID + '''";
            
            function showStatus(message, isError = false) {
                const status = document.getElementById('status');
                status.textContent = message;
                status.className = 'status ' + (isError ? 'error' : 'success');
                status.style.display = 'block';
            }
            
            async function handleCredentialResponse(response) {
                showStatus('Authenticating...');
                
                try {
                    const authResponse = await fetch('/auth/google', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ credential: response.credential })
                    });
                    
                    const data = await authResponse.json();
                    
                    if (data.success) {
                        showStatus('✅ Success! Redirecting...');
                        setTimeout(() => window.location.href = '/', 1000);
                    } else {
                        showStatus('❌ ' + data.message, true);
                    }
                } catch (error) {
                    showStatus('❌ Network error', true);
                }
            }
            
            // Initialize Google Sign-In
            google.accounts.id.initialize({
                client_id: CLIENT_ID,
                callback: handleCredentialResponse
            });
            
            google.accounts.id.renderButton(
                document.getElementById("g_id_signin"),
                { theme: "filled_blue", size: "large", width: "100%" }
            );
            
            showStatus('✅ Ready to sign in');
        </script>
    </body>
    </html>
    '''

@server.route('/auth/google', methods=['POST'])
def google_auth():
    """Handle Google OAuth"""
    if not GOOGLE_AUTH_AVAILABLE:
        return jsonify({'success': False, 'message': 'Google auth not available'})
    
    try:
        credential = request.json.get('credential')
        
        # Verify the token
        idinfo = id_token.verify_oauth2_token(
            credential, google_requests.Request(), GOOGLE_CLIENT_ID)
        
        email = idinfo.get('email')
        name = idinfo.get('name', email)
        google_id = idinfo.get('sub')
        
        if not email:
            return jsonify({'success': False, 'message': 'No email provided'})
        
        # Create or get user
        user_id, role = create_or_get_user(email, name, google_id)
        
        if not user_id:
            return jsonify({'success': False, 'message': role})  # role contains error message
        
        # Create Flask session
        session.permanent = True
        session['authenticated'] = True
        session['user_id'] = user_id
        session['email'] = email
        session['full_name'] = name
        session['role'] = role
        
        return jsonify({
            'success': True,
            'message': f'Welcome {name}!',
            'user': {'id': user_id, 'email': email, 'name': name, 'role': role}
        })
        
    except Exception as e:
        print(f"Auth error: {e}")
        return jsonify({'success': False, 'message': 'Authentication failed'})

@server.route('/logout')
def logout():
    """Logout user"""
    session.clear()
    return redirect('/')

# ==================== DASH COMPONENTS ====================

def create_navbar(user=None):
    """Create navigation bar"""
    if user:
        nav_items = [
            dbc.NavItem(dbc.NavLink("Dashboard", href="/dashboard")),
            dbc.NavItem(dbc.NavLink("Factbook", href="/factbook")),
            dbc.DropdownMenu([
                dbc.DropdownMenuItem(f"👋 {user['full_name']}", disabled=True),
                dbc.DropdownMenuItem(divider=True),
                dbc.DropdownMenuItem("Logout", href="/logout")
            ], nav=True, in_navbar=True, label="Account", className="ms-auto")
        ]
    else:
        nav_items = [
            dbc.NavItem(dbc.NavLink("About", href="/about")),
            dbc.NavItem(dbc.NavLink("Sign In", href="/login", className="btn btn-outline-light ms-2"))
        ]
    
    return dbc.Navbar([
        dbc.Container([
            dbc.NavbarBrand("🏛️ USC Institutional Research", href="/"),
            dbc.Nav(nav_items, navbar=True, className="ms-auto")
        ])
    ], color="#2E8B57", dark=True, className="mb-4")

def create_home_page():
    """Create home page"""
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H1("Welcome to USC Institutional Research", className="text-center mb-4"),
                html.P("Your gateway to university data and insights.", className="text-center lead"),
                dbc.Card([
                    dbc.CardBody([
                        html.H4("🎓 About Our Portal"),
                        html.P("Access comprehensive institutional data, reports, and analytical tools.")
                    ])
                ])
            ], lg=8, className="mx-auto")
        ])
    ])

# ==================== DASH APP LAYOUT ====================

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    dcc.Store(id='user-store'),
    html.Div(id='page-content')
])

# ==================== DASH CALLBACKS ====================

@app.callback(
    Output('user-store', 'data'),
    [Input('url', 'pathname')]
)
def update_user_store(pathname):
    """Update user store based on Flask session"""
    user = get_current_user()
    return user

@app.callback(
    Output('page-content', 'children'),
    [Input('url', 'pathname'),
     Input('user-store', 'data')]
)
def display_page(pathname, user):
    """Main page router"""
    navbar = create_navbar(user)
    
    if pathname == '/' or pathname is None:
        content = create_home_page()
    elif pathname == '/dashboard':
        if user:
            content = html.H1("Dashboard - Coming Soon")
        else:
            content = dbc.Alert("Please sign in to access the dashboard.", color="warning")
    elif pathname == '/factbook':
        if user:
            content = html.H1("Factbook - Coming Soon")
        else:
            content = dbc.Alert("Please sign in to access the factbook.", color="warning")
    elif pathname == '/about':
        content = dbc.Container([
            html.H1("About USC"),
            html.P("The University of the Southern Caribbean, founded in 1927...")
        ])
    else:
        content = dbc.Alert("Page not found", color="danger")
    
    return html.Div([navbar, content])

# ==================== STARTUP ====================

if __name__ == '__main__':
    print("🚀 Starting USC IR Portal (Integrated Version)")
    init_database()
    print("✅ Database initialized")
    print("🌐 Server running on http://localhost:8050")
    print("🔐 Login at http://localhost:8050/login")
    
    app.run_server(debug=True, port=8050)