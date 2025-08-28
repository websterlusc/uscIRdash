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

def create_login_page():
    """Create login page as Dash component"""
    return html.Div([
        dbc.Container([
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H2([
                                html.I(className="fas fa-university me-2"),
                                "USC Institutional Research"
                            ], className="text-center mb-3"),
                            html.P("Sign in to access the portal", className="text-center text-muted mb-4"),

                            # Simple email login for testing
                            html.Div([
                                html.H5("Quick Login (Testing)", className="mb-3"),
                                dbc.InputGroup([
                                    dbc.Input(
                                        id="email-input",
                                        placeholder="Enter your USC email",
                                        type="email",
                                        value="demo@usc.edu.tt"
                                    ),
                                    dbc.Button("Login", id="email-login-btn", color="success")
                                ], className="mb-3"),
                            ]),

                            html.Hr(),

                            # Google OAuth (may need configuration)
                            html.A([
                                dbc.Button([
                                    html.I(className="fab fa-google me-2"),
                                    "Sign in with Google"
                                ], color="primary", size="lg", className="w-100")
                            ], href="/auth/google-redirect", className="d-block mb-3"),

                            # Status messages
                            html.Div(id="login-status", className="text-center"),

                            # Demo login for testing
                            html.Hr(),
                            html.A([
                                dbc.Button([
                                    html.I(className="fas fa-user me-2"),
                                    "Demo Login (Admin)"
                                ], color="outline-secondary", size="sm", className="w-100")
                            ], href="/auth/demo-login"),

                            # Help text
                            html.Small([
                                html.I(className="fas fa-info-circle me-1"),
                                "Use any @usc.edu.tt email for admin access"
                            ], className="text-muted d-block text-center mt-3")
                        ])
                    ], className="shadow-lg")
                ], md=6, lg=4, className="mx-auto")
            ], className="justify-content-center", style={"min-height": "80vh", "align-items": "center"})
        ], fluid=True, style={
            "background": "linear-gradient(135deg, #2E8B57 0%, #1B5E20 100%)",
            "min-height": "100vh"
        })
    ])


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


@server.route('/api/logout', methods=['POST'])
def api_logout():
    """API endpoint for logout"""
    session.clear()
    return jsonify({'success': True, 'redirect': '/'})


# ==================== DASH COMPONENTS ====================

def create_navbar(user=None):
    """Create navigation bar"""
    if user:
        nav_items = [
            dbc.NavItem(dbc.NavLink("Dashboard", href="/dashboard")),
            dbc.NavItem(dbc.NavLink("Factbook", href="/factbook")),
            dbc.DropdownMenu([
                dbc.DropdownMenuItem(f"👋 {user['full_name']}", disabled=True, style={"font-weight": "bold"}),
                dbc.DropdownMenuItem(divider=True),
                dbc.DropdownMenuItem([
                    html.I(className="fas fa-user me-2"),
                    "Profile"
                ], disabled=True),
                dbc.DropdownMenuItem([
                    html.I(className="fas fa-cog me-2"),
                    "Settings"
                ], disabled=True),
                dbc.DropdownMenuItem(divider=True),
                dbc.DropdownMenuItem([
                    html.I(className="fas fa-sign-out-alt me-2"),
                    "Logout"
                ], id="logout-btn", n_clicks=0)
            ], nav=True, in_navbar=True, label=[
                html.I(className="fas fa-user-circle me-2"),
                user['full_name'][:15] if len(user['full_name']) > 15 else user['full_name']
            ], className="ms-auto")
        ]
    else:
        nav_items = [
            dbc.NavItem(dbc.NavLink("About", href="/about")),
            dbc.NavItem(dbc.NavLink([
                html.I(className="fas fa-sign-in-alt me-2"),
                "Sign In"
            ], href="/login", className="btn btn-outline-light ms-2"))
        ]

    return dbc.Navbar([
        dbc.Container([
            dbc.NavbarBrand([
                html.I(className="fas fa-university me-2"),
                "USC Institutional Research"
            ], href="/"),
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
    Output('url', 'pathname'),
    [Input('logout-btn', 'n_clicks')],
    prevent_initial_call=True
)
def handle_logout(n_clicks):
    """Handle logout button click"""
    if n_clicks:
        # Clear Flask session
        session.clear()
        # Redirect to home
        return '/'
    return dash.no_update


@app.callback(
    Output('login-status', 'children'),
    [Input('url', 'search'),
     Input('email-login-btn', 'n_clicks')],
    [State('email-input', 'value')]
)
def handle_login_status(search, n_clicks, email):
    """Handle login status and email login"""
    ctx = callback_context

    if ctx.triggered:
        prop_id = ctx.triggered[0]['prop_id'].split('.')[0]

        if prop_id == 'email-login-btn' and n_clicks and email:
            # Simple email login
            if '@' in email:
                # Create session
                session.permanent = True
                session['authenticated'] = True
                session['user_id'] = hash(email) % 1000  # Simple ID generation
                session['email'] = email
                session['full_name'] = email.split('@')[0].title()
                session['role'] = 'admin' if 'usc.edu.tt' in email else 'user'

                # Redirect to home
                return dbc.Alert([
                    html.I(className="fas fa-check-circle me-2"),
                    f"Welcome {email}! Redirecting...",
                    html.Script('setTimeout(() => window.location.href = "/", 1500);')
                ], color="success")
            else:
                return dbc.Alert("Please enter a valid email address.", color="warning")

    # Handle URL error messages
    if search:
        if 'error=google_unavailable' in search:
            return dbc.Alert("Google authentication is not available. Please contact support.", color="danger")
        elif 'error=no_code' in search:
            return dbc.Alert("Google authentication was cancelled.", color="warning")
        elif 'error=no_client_secret' in search:
            return dbc.Alert("Google Client Secret not configured. Please contact administrator.", color="danger")
        elif 'error=token_exchange_failed' in search:
            return dbc.Alert("Failed to exchange authorization code. Please try again.", color="danger")
        elif 'error=no_access_token' in search:
            return dbc.Alert("Failed to get access token from Google. Please try again.", color="danger")
        elif 'error=userinfo_failed' in search:
            return dbc.Alert("Failed to get user information from Google. Please try again.", color="danger")
        elif 'error=callback_exception' in search:
            return dbc.Alert("An error occurred during authentication. Please try again.", color="danger")
        elif 'error=token_failed' in search:
            return dbc.Alert("Google authentication failed. Please try again.", color="danger")
        elif 'error=no_email' in search:
            return dbc.Alert("Could not get email from Google. Please try again.", color="danger")
        elif 'error=user_creation_failed' in search:
            return dbc.Alert("Account creation failed. Please contact support.", color="danger")
        elif 'error=oauth_failed' in search:
            return dbc.Alert("Authentication failed. Please try again.", color="danger")

    return ""


# Add a demo login for testing
@server.route('/auth/demo-login')
def demo_login():
    """Demo login for testing (remove in production)"""
    session.permanent = True
    session['authenticated'] = True
    session['user_id'] = 999
    session['email'] = 'demo@usc.edu.tt'
    session['full_name'] = 'Demo User'
    session['role'] = 'admin'

    return redirect('/')


@server.route('/auth/google-redirect')
def google_redirect():
    """Redirect to Google OAuth"""
    if not GOOGLE_AUTH_AVAILABLE:
        return redirect('/login?error=google_unavailable')

    # Properly encode the redirect URI
    import urllib.parse

    redirect_uri = "http://localhost:8050/auth/google-callback"

    # Build Google OAuth URL with proper encoding
    params = {
        'client_id': GOOGLE_CLIENT_ID,
        'redirect_uri': redirect_uri,
        'scope': 'email profile',
        'response_type': 'code',
        'access_type': 'offline'
    }

    query_string = urllib.parse.urlencode(params)
    google_oauth_url = f"https://accounts.google.com/o/oauth2/v2/auth?{query_string}"

    print(f"🔍 Redirecting to Google OAuth: {google_oauth_url}")
    return redirect(google_oauth_url)


@server.route('/auth/google-callback')
def google_callback():
    """Handle Google OAuth callback"""
    if not GOOGLE_AUTH_AVAILABLE:
        return redirect('/login?error=google_unavailable')

    code = request.args.get('code')
    error = request.args.get('error')

    if error:
        print(f"❌ Google OAuth error: {error}")
        return redirect(f'/login?error=google_error_{error}')

    if not code:
        print("❌ No authorization code received from Google")
        return redirect('/login?error=no_code')

    try:
        print(f"🔍 Received authorization code: {code[:20]}...")

        # Check if we have the client secret
        client_secret = os.getenv('GOOGLE_CLIENT_SECRET')
        if not client_secret:
            print("❌ GOOGLE_CLIENT_SECRET not found in environment")
            return redirect('/login?error=no_client_secret')

        # Exchange code for token using requests
        import requests as req

        token_data = {
            'client_id': GOOGLE_CLIENT_ID,
            'client_secret': client_secret,
            'code': code,
            'grant_type': 'authorization_code',
            'redirect_uri': 'http://localhost:8050/auth/google-callback'
        }

        print("🔍 Exchanging code for token...")
        token_response = req.post('https://oauth2.googleapis.com/token', data=token_data)

        print(f"🔍 Token response status: {token_response.status_code}")

        if token_response.status_code != 200:
            print(f"❌ Token exchange failed: {token_response.text}")
            return redirect('/login?error=token_exchange_failed')

        token_json = token_response.json()

        if 'access_token' not in token_json:
            print(f"❌ No access token in response: {token_json}")
            return redirect('/login?error=no_access_token')

        access_token = token_json['access_token']
        print(f"✅ Got access token: {access_token[:20]}...")

        # Get user info
        print("🔍 Getting user info from Google...")
        user_response = req.get(
            f"https://www.googleapis.com/oauth2/v2/userinfo?access_token={access_token}"
        )

        if user_response.status_code != 200:
            print(f"❌ User info request failed: {user_response.text}")
            return redirect('/login?error=userinfo_failed')

        user_info = user_response.json()
        print(f"✅ Got user info: {user_info}")

        email = user_info.get('email')
        name = user_info.get('name', email)
        google_id = user_info.get('id')

        if not email:
            print("❌ No email in user info")
            return redirect('/login?error=no_email')

        print(f"✅ User: {name} ({email})")

        # Create or get user
        user_id, role = create_or_get_user(email, name, google_id)

        if not user_id:
            print(f"❌ User creation failed for {email}")
            return redirect('/login?error=user_creation_failed')

        # Create Flask session
        session.permanent = True
        session['authenticated'] = True
        session['user_id'] = user_id
        session['email'] = email
        session['full_name'] = name
        session['role'] = role

        print(f"✅ Session created for {email}")
        return redirect('/')

    except Exception as e:
        print(f"❌ Google OAuth callback error: {e}")
        import traceback
        traceback.print_exc()
        return redirect('/login?error=callback_exception')


@app.callback(
    Output('page-content', 'children'),
    [Input('url', 'pathname'),
     Input('user-store', 'data')]
)
def display_page(pathname, user):
    """Main page router"""
    # Handle login page specially (no navbar)
    if pathname == '/login':
        if user:
            # Already logged in, redirect to home
            return html.Div([
                dbc.Alert("You are already logged in. Redirecting...", color="info"),
                html.Script('setTimeout(() => window.location.href = "/", 2000);')
            ])
        else:
            # Show login page
            return create_login_page()

    # For all other pages, include navbar
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