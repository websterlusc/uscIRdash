import dash
from dash import dcc, html, Input, Output, State, callback_context, ALL
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import sqlite3
import bcrypt
import secrets
from datetime import datetime, timedelta
import traceback
import os
from flask import session
import requests

# Import your existing components and functions
from components.navbar import create_navbar
from components.home_page import create_home_page
from pages.public.about_usc import create_about_usc_layout
from pages.public.vision_mission_motto import create_vision_mission_motto_layout
from pages.public.governance import create_governance_layout
from components.dashboard import create_dashboard
from components.admin_dashboard import create_admin_dashboard
from components.profile import create_profile_page
from components.change_password import create_change_password_page
from components.register import create_register_page
from components.request_form import create_request_form
from components.factbook import create_factbook_layout
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
# USC Brand Colors
USC_COLORS = {
    'primary_green': '#2E8B57',
    'secondary_green': '#228B22',
    'accent_yellow': '#FFD700',
    'light_gray': '#F8F9FA',
    'dark_gray': '#495057'
}

# Database setup
DATABASE = 'usc_portal.db'


def init_database():
    """Initialize the database with required tables"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT,
            full_name TEXT,
            role TEXT DEFAULT 'user',
            is_active INTEGER DEFAULT 1,
            is_approved INTEGER DEFAULT 0,
            google_auth INTEGER DEFAULT 0,
            google_id TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP
        )
    ''')

    # User sessions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_token TEXT UNIQUE NOT NULL,
            user_id INTEGER NOT NULL,
            user_email TEXT NOT NULL,
            expires_at TIMESTAMP NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    conn.commit()
    conn.close()


# Initialize database
init_database()


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


def hash_password(password):
    """Hash a password using bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def verify_password(password, password_hash):
    """Verify a password against its hash"""
    return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))


def change_user_password(user_id, current_password, new_password):
    """Change user password after verifying current password"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute('SELECT password_hash FROM users WHERE id = ?', (user_id,))
    result = cursor.fetchone()

    if not result:
        conn.close()
        return {'success': False, 'message': 'User not found'}

    # Verify current password
    if not verify_password(current_password, result[0]):
        conn.close()
        return {'success': False, 'message': 'Current password is incorrect'}

    # Update to new password
    new_hash = hash_password(new_password)
    cursor.execute('UPDATE users SET password_hash = ? WHERE id = ?', (new_hash, user_id))
    conn.commit()
    conn.close()

    return {'success': True, 'message': 'Password changed successfully'}


# ==================== UI COMPONENTS ====================

def create_google_login_page():
    """Create a Google login page that works within Dash"""
    return dbc.Container([
        dcc.Store(id='google-credential-store', data=None),
        dcc.Store(id='auth-status-store', data=None),

        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.H3("USC Institutional Research Login", className="text-center mb-0")
                    ], style={'backgroundColor': USC_COLORS['primary_green'], 'color': 'white'}),

                    dbc.CardBody([
                        html.Div([
                            html.H5("Sign in with Google", className="text-center mb-3"),
                            html.Div(id="login-status", className="text-center mb-3"),
                            html.Div([
                                html.Div(id="google-signin-button",
                                         style={'minHeight': '50px', 'display': 'flex',
                                                'justifyContent': 'center', 'alignItems': 'center'}),
                            ], className="d-flex justify-content-center mb-4"),

                            html.Div([
                                html.Small([
                                    "Note: USC employees (@usc.edu.tt) are automatically approved. ",
                                    "Others require admin approval."
                                ], className="text-muted text-center")
                            ])
                        ]),

                        html.Div(id="login-alert")
                    ])
                ])
            ], width=12, md=6, lg=4)
        ], justify="center", className="min-vh-100 align-items-center py-5")
    ], fluid=True)


def create_auth_success_page():
    """Page shown after successful authentication"""
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                dbc.Alert([
                    html.I(className="fas fa-check-circle me-2"),
                    "Authentication successful! Redirecting..."
                ], color="success", className="text-center"),

                dbc.Button("Go to Dashboard", href="/dashboard", color="primary", className="w-100 mt-3")
            ], width=6, className="mx-auto")
        ], className="min-vh-100 align-items-center justify-content-center")
    ])


def get_google_signin_script():
    """Generate the Google Sign-In JavaScript for the login page"""
    return html.Script(f"""
        console.log('Loading Google Sign-In script...');

        // Load Google Sign-In API
        if (!window.google) {{
            const script = document.createElement('script');
            script.src = 'https://accounts.google.com/gsi/client';
            script.async = true;
            script.defer = true;
            script.onload = initializeGoogleSignIn;
            document.head.appendChild(script);
        }} else {{
            initializeGoogleSignIn();
        }}

        function initializeGoogleSignIn() {{
            console.log('Initializing Google Sign-In...');

            google.accounts.id.initialize({{
                client_id: "{os.getenv('GOOGLE_CLIENT_ID', 'your-client-id')}",
                callback: handleCredentialResponse,
                auto_select: false,
                cancel_on_tap_outside: false
            }});

            // Render the sign-in button
            const buttonDiv = document.getElementById('google-signin-button');
            if (buttonDiv) {{
                google.accounts.id.renderButton(buttonDiv, {{
                    theme: "filled_blue",
                    size: "large",
                    width: "300",
                    text: "signin_with",
                    logo_alignment: "left"
                }});
                console.log('Google Sign-In button rendered');
            }}
        }}

        function handleCredentialResponse(response) {{
            console.log('Google credential received');

            // Update the status
            const statusDiv = document.getElementById('login-status');
            if (statusDiv) {{
                statusDiv.innerHTML = '<div class="spinner-border spinner-border-sm me-2"></div>Processing...';
            }}

            // Store credential in Dash component
            if (window.dash_clientside) {{
                window.dash_clientside.set_props('google-credential-store', {{
                    data: response.credential
                }});
            }} else {{
                console.error('Dash clientside not available');
            }}
        }}
    """)


# ==================== MAIN APP LAYOUT ====================

# Initialize the Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

# Update your main app layout to include the Google script
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    dcc.Store(id='session-store', storage_type='session'),
    get_google_signin_script(),  # Add Google Sign-In script
    html.Div(id='navbar-container'),
    html.Div(id='page-content'),
    html.Div(id='hidden-div', style={'display': 'none'})
])


# ==================== MAIN CALLBACKS ====================
@app.callback(
    Output('session-store', 'data', allow_duplicate=True),
    [Input('url', 'pathname')],
    prevent_initial_call=True
)
def sync_session_on_page_load(pathname):
    """Sync Flask session with Dash session on every page load"""
    try:
        print(f"🔍 Syncing session for pathname: {pathname}")

        # Make request to Flask to get session data
        import requests

        try:
            response = requests.get('http://localhost:5000/auth/session-data',
                                    cookies=request.cookies if 'request' in globals() else None,
                                    timeout=2)

            if response.status_code == 200:
                flask_session_data = response.json()

                if flask_session_data.get('authenticated'):
                    print(f"✅ Found Flask session: {flask_session_data.get('email')}")
                    return {
                        'token': flask_session_data.get('token'),
                        'user_id': flask_session_data.get('user_id'),
                        'email': flask_session_data.get('email'),
                        'full_name': flask_session_data.get('full_name'),
                        'role': flask_session_data.get('role'),
                        'authenticated': True,
                        'synced': True
                    }
                else:
                    print("❌ No Flask session found")
                    return {}
            else:
                print(f"❌ Flask session request failed: {response.status_code}")
                return {}

        except requests.exceptions.RequestException as e:
            print(f"❌ Failed to connect to Flask auth server: {e}")
            # Fallback: try to use existing session data
            return dash.no_update

    except Exception as e:
        print(f"Session sync error: {e}")
        return {}


@app.callback(
    [Output('navbar-container', 'children'),
     Output('page-content', 'children')],
    [Input('url', 'pathname')],
    [State('session-store', 'data')]
)
def display_page(pathname, session_data):
    """Main router callback with improved session handling"""
    try:
        print(f"🔍 DEBUG: Accessing pathname: {pathname}")
        print(f"🔍 DEBUG: Session data: {session_data}")

        # Determine if user is authenticated
        user = None
        is_authenticated = False

        if session_data and session_data.get('authenticated') and session_data.get('token'):
            user = {
                'id': session_data.get('user_id'),
                'email': session_data.get('email'),
                'full_name': session_data.get('full_name', 'User'),
                'role': session_data.get('role', 'user')
            }
            is_authenticated = True
            print(f"✅ User authenticated: {user['email']}")
        else:
            print("❌ User not authenticated")

        # Create navbar based on auth status
        navbar = create_navbar(user)

        # Route handling
        if pathname in ['/about-usc', '/vision-mission-motto', '/governance', '/request']:
            # Public pages
            if pathname == '/about-usc':
                return navbar, create_about_usc_layout()
            elif pathname == '/vision-mission-motto':
                return navbar, create_vision_mission_motto_layout()
            elif pathname == '/governance':
                return navbar, create_governance_layout()
            elif pathname == '/request':
                return navbar, create_request_form()

        elif pathname == '/login':
            if is_authenticated:
                # Already logged in, redirect to dashboard
                return navbar, html.Div([
                    dbc.Alert([
                        html.I(className="fas fa-check-circle me-2"),
                        f"Welcome back, {user['full_name']}! Redirecting to dashboard..."
                    ], color="success"),
                    html.Script('setTimeout(() => window.location.href = "/dashboard", 2000);')
                ])
            else:
                # Redirect to Flask login page
                return navbar, html.Div([
                    html.Script('window.location.href = "http://localhost:5000/login";')
                ])

        elif pathname in ['/dashboard', '/', '/factbook', '/data-management', '/admin']:
            if is_authenticated:
                # User is authenticated, show requested page
                if pathname == '/admin' and user['role'] != 'admin':
                    return navbar, dbc.Alert("Admin access required.", color="danger")
                elif pathname == '/factbook':
                    return navbar, create_factbook_layout()
                elif pathname == '/data-management':
                    return navbar, create_data_management_layout()
                elif pathname == '/admin':
                    return navbar, create_admin_dashboard()
                else:  # dashboard or home
                    return navbar, create_dashboard()
            else:
                # User not authenticated, show login prompt
                return navbar, html.Div([
                    dbc.Alert([
                        html.I(className="fas fa-lock me-2"),
                        "Please sign in to access this page. ",
                        html.A("Sign In", href="http://localhost:5000/login", className="alert-link")
                    ], color="warning"),
                    html.Script('setTimeout(() => window.location.href = "http://localhost:5000/login", 3000);')
                ])

        else:
            # Default route
            if is_authenticated:
                return navbar, create_dashboard()
            else:
                return navbar, html.Div([
                    html.Script('window.location.href = "http://localhost:5000/login";')
                ])

    except Exception as e:
        print(f"❌ Router error: {e}")
        import traceback
        traceback.print_exc()
        return create_navbar(None), dbc.Alert("An error occurred. Please refresh the page.", color="danger")


# Add this callback to handle Google credential processing within Dash
@app.callback(
    [Output('login-alert', 'children'),
     Output('session-store', 'data'),
     Output('url', 'pathname')],
    [Input('google-credential-store', 'data')],
    [State('session-store', 'data')]
)
def process_google_credential(credential_data, session_data):
    """Process Google credential and update session"""
    if not credential_data:
        return dash.no_update, dash.no_update, dash.no_update

    try:
        print(f"🔍 Processing Google credential in Dash...")

        # Make a request to your Flask auth endpoint
        import requests
        import json

        response = requests.post('http://localhost:8050/auth/google',
                                 json={'credential': credential_data},
                                 headers={'Content-Type': 'application/json'})

        if response.status_code == 200:
            result = response.json()

            if result.get('success'):
                print("✅ Google authentication successful")

                # Update session store with authentication data
                new_session_data = {
                    'token': result['token'],
                    'authenticated': True,
                    'user': result['user']
                }

                # Success message and redirect to dashboard
                success_alert = dbc.Alert([
                    html.I(className="fas fa-check-circle me-2"),
                    "Login successful! Redirecting to dashboard..."
                ], color="success")

                return success_alert, new_session_data, '/dashboard'
            else:
                print(f"❌ Authentication failed: {result.get('message')}")
                error_alert = dbc.Alert([
                    html.I(className="fas fa-exclamation-triangle me-2"),
                    result.get('message', 'Authentication failed')
                ], color="danger")
                return error_alert, session_data, dash.no_update
        else:
            print(f"❌ HTTP error: {response.status_code}")
            error_alert = dbc.Alert([
                html.I(className="fas fa-exclamation-triangle me-2"),
                "Network error. Please try again."
            ], color="danger")
            return error_alert, session_data, dash.no_update

    except Exception as e:
        print(f"❌ Error processing credential: {e}")
        error_alert = dbc.Alert([
            html.I(className="fas fa-exclamation-triangle me-2"),
            f"Error: {str(e)}"
        ], color="danger")
        return error_alert, session_data, dash.no_update


# LOGOUT CALLBACK
@app.callback(
    [Output('session-store', 'data', allow_duplicate=True),
     Output('url', 'pathname', allow_duplicate=True)],
    [Input('logout-btn', 'n_clicks')],
    prevent_initial_call=True
)
def handle_logout(n_clicks):
    """Handle user logout"""
    if n_clicks:
        print("🔍 User logout requested")
        # Clear session data
        return {}, '/'
    return dash.no_update, dash.no_update


if __name__ == '__main__':
    app.run_server(debug=True, port=8050)