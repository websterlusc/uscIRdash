# main_app.py - Fixed version with all issues resolved

import dash
from dash import dcc, html, Input, Output, State, callback_context, ALL
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import sqlite3
import secrets
from datetime import datetime, timedelta
import traceback
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import components (with fallbacks for missing ones)
try:
    from components.navbar import create_navbar
except ImportError:
    print("⚠️ components.navbar not found, using built-in navbar")
    create_navbar = None

try:
    from components.home_page import create_home_page
except ImportError:
    print("⚠️ components.home_page not found, using built-in home page")
    create_home_page = None

try:
    from pages.public.about_usc import create_about_usc_layout
except ImportError:
    create_about_usc_layout = None

try:
    from pages.public.vision_mission_motto import create_vision_mission_motto_layout
except ImportError:
    create_vision_mission_motto_layout = None

try:
    from pages.public.governance import create_governance_layout
except ImportError:
    create_governance_layout = None

try:
    from components.dashboard import create_dashboard
except ImportError:
    create_dashboard = None

try:
    from components.admin_dashboard import create_admin_dashboard
except ImportError:
    create_admin_dashboard = None

try:
    from components.factbook import create_factbook_layout
except ImportError:
    create_factbook_layout = None

# USC Brand Colors
USC_COLORS = {
    'primary_green': '#1B5E20',
    'secondary_green': '#4CAF50',
    'accent_yellow': '#FDD835',
    'white': '#FFFFFF',
    'light_gray': '#F5F5F5',
    'dark_gray': '#424242',
    'text_gray': '#666666'
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


# Initialize Dash app
app = dash.Dash(__name__,
                external_stylesheets=[dbc.themes.BOOTSTRAP],
                suppress_callback_exceptions=True,
                meta_tags=[
                    {"name": "viewport", "content": "width=device-width, initial-scale=1"}
                ])

server = app.server

# Custom CSS for better styling
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>USC Institutional Research</title>
        {%favicon%}
        {%css%}
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
        <style>
        :root {
            --usc-green: #1B5E20;
            --usc-light-green: #4CAF50;
            --usc-yellow: #FDD835;
        }

        .navbar-brand {
            font-weight: bold !important;
            font-size: 1.3rem !important;
            color: white !important;
        }

        .navbar-brand:hover {
            color: #FDD835 !important;
        }

        .nav-link {
            font-weight: 500 !important;
            transition: all 0.3s ease !important;
            color: rgba(255,255,255,0.9) !important;
        }

        .nav-link:hover {
            color: #FDD835 !important;
            transform: translateY(-1px);
        }

        .btn-outline-light:hover {
            background-color: #FDD835 !important;
            border-color: #FDD835 !important;
            color: var(--usc-green) !important;
        }

        .card {
            border: none !important;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1) !important;
            transition: transform 0.2s ease !important;
        }

        .card:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 6px 12px rgba(0,0,0,0.15) !important;
        }

        .btn-primary {
            background-color: var(--usc-green) !important;
            border-color: var(--usc-green) !important;
        }

        .btn-primary:hover {
            background-color: var(--usc-light-green) !important;
            border-color: var(--usc-light-green) !important;
        }

        .alert {
            border-left: 4px solid var(--usc-green) !important;
        }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''


# ==================== UI COMPONENTS ====================

def create_navbar_builtin(user=None):
    """Built-in navbar function"""

    if user:
        # Authenticated user navbar
        user_dropdown = dbc.DropdownMenu([
            dbc.DropdownMenuItem(f"Welcome, {user.get('full_name', user.get('email', 'User'))}", disabled=True),
            dbc.DropdownMenuItem(divider=True),
            dbc.DropdownMenuItem([
                html.I(className="fas fa-user me-2"),
                "Profile"
            ], href="/profile"),
            dbc.DropdownMenuItem([
                html.I(className="fas fa-cog me-2"),
                "Settings"
            ], href="/settings"),
            dbc.DropdownMenuItem(divider=True),
            dbc.DropdownMenuItem([
                html.I(className="fas fa-sign-out-alt me-2"),
                "Logout"
            ], href="http://localhost:5000/auth/logout", external_link=True)
        ],
            nav=True,
            in_navbar=True,
            label=[
                html.I(className="fas fa-user-circle me-2"),
                user.get('full_name', user.get('email', 'User'))[:15]
            ],
            color="light",
            className="ms-2")

        nav_items = [
            dbc.NavItem(dbc.NavLink("Dashboard", href="/dashboard", className="nav-link")),
            dbc.NavItem(dbc.NavLink("Factbook", href="/factbook", className="nav-link")),
            dbc.NavItem(dbc.NavLink("Data Management", href="/data-management", className="nav-link")),
        ]

        if user.get('role') == 'admin':
            nav_items.append(dbc.NavItem(dbc.NavLink("Admin", href="/admin", className="nav-link")))

        nav_items.append(user_dropdown)

    else:
        # Public navbar
        nav_items = [
            dbc.NavItem(dbc.NavLink("Home", href="/", className="nav-link")),
            dbc.NavItem(dbc.NavLink("About USC", href="/about-usc", className="nav-link")),
            dbc.NavItem(dbc.NavLink("Vision & Mission", href="/vision-mission-motto", className="nav-link")),
            dbc.NavItem(dbc.NavLink("Governance", href="/governance", className="nav-link")),
            dbc.NavItem(dbc.NavLink("Request Access", href="/request", className="nav-link")),
            dbc.NavItem(dbc.NavLink([
                html.I(className="fas fa-sign-in-alt me-2"),
                "Sign In"
            ], href="http://localhost:5000/login", external_link=True, className="btn btn-outline-light ms-3"))
        ]

    return dbc.Navbar([
        dbc.Container([
            dbc.Row([
                dbc.Col([
                    dbc.NavbarBrand([
                        html.I(className="fas fa-university me-2"),
                        "USC Institutional Research"
                    ], href="/", className="navbar-brand")
                ], width="auto"),
                dbc.Col([
                    dbc.Nav(nav_items, navbar=True, className="ms-auto")
                ], width=True)
            ], align="center", className="w-100")
        ], fluid=True)
    ],
        color=USC_COLORS['primary_green'],
        dark=True,
        className="mb-0 shadow-sm",
        style={"minHeight": "70px"})


def create_home_page_builtin():
    """Built-in home page function"""
    return dbc.Container([
        # Hero Section
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.H1("USC Institutional Research",
                            className="display-4 fw-bold text-center mb-4",
                            style={"color": USC_COLORS['primary_green']}),
                    html.P("University of the Southern Caribbean",
                           className="lead text-center mb-4 text-muted"),
                    html.Hr(className="my-4"),
                    html.P("Welcome to the USC Institutional Research Portal. Access comprehensive data, "
                           "analytics, and insights about our university's academic and operational performance.",
                           className="text-center mb-4"),

                    dbc.Row([
                        dbc.Col([
                            dbc.Button([
                                html.I(className="fas fa-chart-bar me-2"),
                                "Explore Factbook"
                            ], color="primary", size="lg", href="/factbook", className="w-100")
                        ], md=4),
                        dbc.Col([
                            dbc.Button([
                                html.I(className="fas fa-info-circle me-2"),
                                "About USC"
                            ], color="outline-primary", size="lg", href="/about-usc", className="w-100")
                        ], md=4),
                        dbc.Col([
                            dbc.Button([
                                html.I(className="fas fa-key me-2"),
                                "Request Access"
                            ], color="outline-secondary", size="lg", href="/request", className="w-100")
                        ], md=4)
                    ], className="text-center")
                ], className="py-5")
            ])
        ], className="mb-5"),

        # Features Section
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.I(className="fas fa-graduation-cap fa-3x text-primary mb-3"),
                        html.H4("Academic Excellence", className="card-title"),
                        html.P("Comprehensive data on student enrollment, graduation rates, "
                               "academic programs, and institutional performance metrics.")
                    ])
                ], className="text-center h-100")
            ], md=4),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.I(className="fas fa-chart-line fa-3x text-success mb-3"),
                        html.H4("Data-Driven Insights", className="card-title"),
                        html.P("Advanced analytics and visualization tools to understand "
                               "trends, patterns, and opportunities for institutional growth.")
                    ])
                ], className="text-center h-100")
            ], md=4),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.I(className="fas fa-users fa-3x text-info mb-3"),
                        html.H4("Stakeholder Access", className="card-title"),
                        html.P("Secure, role-based access for faculty, staff, administrators, "
                               "and authorized external stakeholders.")
                    ])
                ], className="text-center h-100")
            ], md=4)
        ], className="mb-5"),

        # Quick Stats Section
        dbc.Row([
            dbc.Col([
                html.H3("Quick Facts", className="text-center mb-4"),
                dbc.Row([
                    dbc.Col([
                        html.H2("3,000+", className="text-primary fw-bold"),
                        html.P("Students Enrolled")
                    ], className="text-center"),
                    dbc.Col([
                        html.H2("50+", className="text-success fw-bold"),
                        html.P("Academic Programs")
                    ], className="text-center"),
                    dbc.Col([
                        html.H2("95+", className="text-info fw-bold"),
                        html.P("Years of Excellence")
                    ], className="text-center"),
                    dbc.Col([
                        html.H2("100+", className="text-warning fw-bold"),
                        html.P("Faculty & Staff")
                    ], className="text-center")
                ])
            ])
        ], className="py-5", style={"backgroundColor": USC_COLORS['light_gray']})

    ], fluid=True, className="px-0")


def create_dashboard_builtin():
    """Built-in dashboard function"""
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H1("Dashboard", className="mb-4"),
                dbc.Alert("Welcome to the USC Institutional Research Dashboard!", color="success"),

                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                html.H4("Factbook", className="card-title"),
                                html.P("Access institutional facts and figures"),
                                dbc.Button("View Factbook", color="primary", href="/factbook")
                            ])
                        ])
                    ], md=4),
                    dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                html.H4("Data Management", className="card-title"),
                                html.P("Manage and analyze institutional data"),
                                dbc.Button("Manage Data", color="primary", href="/data-management")
                            ])
                        ])
                    ], md=4),
                    dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                html.H4("Reports", className="card-title"),
                                html.P("Generate comprehensive reports"),
                                dbc.Button("View Reports", color="primary", disabled=True)
                            ])
                        ])
                    ], md=4)
                ])
            ])
        ])
    ], fluid=True)


def create_data_management_layout():
    """Built-in data management layout"""
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H1("Data Management", className="mb-4"),
                dbc.Alert("Data management tools will be available soon!", color="info"),

                dbc.Card([
                    dbc.CardHeader("Available Tools"),
                    dbc.CardBody([
                        html.Ul([
                            html.Li("Student enrollment data"),
                            html.Li("Financial information"),
                            html.Li("Academic program statistics"),
                            html.Li("Faculty and staff data"),
                            html.Li("Graduation and retention rates")
                        ])
                    ])
                ])
            ])
        ])
    ], fluid=True)


def create_about_usc_layout_builtin():
    """Built-in about USC layout"""
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H1("About USC", className="mb-4"),
                html.P("The University of the Southern Caribbean (USC) is a premier institution "
                       "of higher education in the Caribbean region."),
                html.P("Founded in 1927, USC has been providing quality education for over 95 years."),
            ])
        ])
    ], fluid=True)


def create_request_form_builtin():
    """Built-in request form"""
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H1("Request Access", className="mb-4"),
                dbc.Alert([
                    html.I(className="fas fa-envelope me-2"),
                    "To request access to the USC Institutional Research Portal, "
                    "please contact us at: ir@usc.edu.tt"
                ], color="info")
            ], lg=8, className="mx-auto")
        ])
    ], fluid=True)


# Use built-in functions as fallbacks
if create_navbar is None:
    create_navbar = create_navbar_builtin
if create_home_page is None:
    create_home_page = create_home_page_builtin
if create_dashboard is None:
    create_dashboard = create_dashboard_builtin
if create_about_usc_layout is None:
    create_about_usc_layout = create_about_usc_layout_builtin

# ==================== APP LAYOUT ====================

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    dcc.Store(id='session-store', storage_type='session'),
    html.Div(id='navbar-container'),
    html.Div(id='page-content')
])


# ==================== CALLBACKS ====================

# REPLACE your callbacks in main_app.py with this SINGLE COMBINED callback:

# REMOVE both old callbacks and replace with this ONE callback:
@app.callback(
    [Output('navbar-container', 'children'),
     Output('page-content', 'children'),
     Output('session-store', 'data')],  # No allow_duplicate needed!
    [Input('url', 'pathname')],
    [State('session-store', 'data')],
    prevent_initial_call=False
)
def display_page_with_session_sync(pathname, session_data):
    """COMBINED: Session sync + page routing in one callback"""
    try:
        print(f"🔍 COMBINED: pathname={pathname}, existing_session={session_data is not None}")

        # STEP 1: Sync with Flask session
        synced_session_data = {}

        try:
            import urllib.request
            import urllib.error
            import json

            req = urllib.request.Request('http://localhost:5000/auth/session-data')

            with urllib.request.urlopen(req, timeout=3) as response:
                if response.status == 200:
                    flask_session_data = json.loads(response.read().decode())

                    print(f"📡 FLASK: {flask_session_data}")

                    # Strict validation - must have ALL required fields
                    if (flask_session_data.get('authenticated') and
                            flask_session_data.get('token') and
                            flask_session_data.get('user_id') and
                            flask_session_data.get('email')):

                        synced_session_data = {
                            'token': flask_session_data.get('token'),
                            'user_id': flask_session_data.get('user_id'),
                            'email': flask_session_data.get('email'),
                            'full_name': flask_session_data.get('full_name', flask_session_data.get('email')),
                            'role': flask_session_data.get('role', 'user'),
                            'authenticated': True,
                            'synced_at': datetime.now().isoformat()
                        }

                        print(f"✅ FLASK: Valid session for {synced_session_data['email']}")
                    else:
                        print("❌ FLASK: Invalid or incomplete session")
                        synced_session_data = {'authenticated': False}
                else:
                    print(f"❌ FLASK: Session endpoint error: {response.status}")
                    synced_session_data = {'authenticated': False}

        except Exception as e:
            print(f"❌ FLASK: Session sync failed: {e}")
            synced_session_data = {'authenticated': False}

        # STEP 2: Use synced session data (or existing if sync failed)
        final_session_data = synced_session_data if synced_session_data.get('authenticated') else (session_data or {})

        # STEP 3: Determine authentication status
        user = None
        is_authenticated = False

        if (final_session_data and
                final_session_data.get('authenticated') and
                final_session_data.get('email')):

            user = {
                'id': final_session_data.get('user_id'),
                'email': final_session_data.get('email'),
                'full_name': final_session_data.get('full_name', final_session_data.get('email')),
                'role': final_session_data.get('role', 'user')
            }
            is_authenticated = True
            print(f"✅ AUTH: User {user['email']} is authenticated")
        else:
            print("❌ AUTH: User not authenticated")

        # STEP 4: Create navbar
        if create_navbar:
            navbar = create_navbar(user)
        else:
            navbar = create_navbar_builtin(user)

        print(f"🔧 NAVBAR: Created with user={user is not None}")

        # STEP 5: Route handling
        if pathname == '/' or pathname is None:
            if create_home_page:
                content = create_home_page()
            else:
                content = create_home_page_builtin()

        elif pathname in ['/about-usc', '/vision-mission-motto', '/governance', '/request']:
            if pathname == '/about-usc':
                if create_about_usc_layout:
                    content = create_about_usc_layout()
                else:
                    content = create_about_usc_layout_builtin()
            elif pathname == '/vision-mission-motto':
                if create_vision_mission_motto_layout:
                    content = create_vision_mission_motto_layout()
                else:
                    content = html.H1("Vision & Mission - Coming Soon")
            elif pathname == '/governance':
                if create_governance_layout:
                    content = create_governance_layout()
                else:
                    content = html.H1("Governance - Coming Soon")
            elif pathname == '/request':
                content = create_request_form_builtin()

        elif pathname == '/login':
            if is_authenticated:
                content = html.Div([
                    dbc.Alert([
                        html.I(className="fas fa-check-circle me-2"),
                        f"Welcome back, {user['full_name']}! Redirecting to dashboard..."
                    ], color="success"),
                    html.Script('setTimeout(() => window.location.href = "/dashboard", 2000);')
                ])
            else:
                content = html.Div([
                    html.Script('window.location.href = "http://localhost:5000/login";')
                ])

        elif pathname in ['/dashboard', '/factbook', '/data-management', '/admin']:
            if is_authenticated:
                if pathname == '/admin' and user['role'] != 'admin':
                    content = dbc.Alert("Admin access required.", color="danger")
                elif pathname == '/factbook':
                    if create_factbook_layout:
                        content = create_factbook_layout()
                    else:
                        content = html.H1("Factbook - Coming Soon")
                elif pathname == '/data-management':
                    content = create_data_management_layout() if 'create_data_management_layout' in globals() else html.H1(
                        "Data Management - Coming Soon")
                elif pathname == '/admin':
                    if create_admin_dashboard:
                        content = create_admin_dashboard()
                    else:
                        content = html.H1("Admin Dashboard - Coming Soon")
                else:  # dashboard
                    if create_dashboard:
                        content = create_dashboard()
                    else:
                        content = html.H1("Dashboard - Coming Soon")
            else:
                content = html.Div([
                    dbc.Alert([
                        html.I(className="fas fa-lock me-2"),
                        "Please sign in to access this page. ",
                        html.A("Sign In", href="http://localhost:5000/login", className="alert-link")
                    ], color="warning"),
                    html.Script('setTimeout(() => window.location.href = "http://localhost:5000/login", 3000);')
                ])

        else:
            content = html.Div([
                dbc.Alert("Page not found. Redirecting to home...", color="warning"),
                html.Script('setTimeout(() => window.location.href = "/", 2000);')
            ])

        print(f"✅ RETURNING: navbar, content, session_data")
        return navbar, content, synced_session_data

    except Exception as e:
        print(f"❌ COMBINED: Error: {e}")
        import traceback
        traceback.print_exc()

        # Return safe defaults
        error_navbar = create_navbar(None) if create_navbar else create_navbar_builtin(None)
        error_content = dbc.Alert([
            html.I(className="fas fa-exclamation-triangle me-2"),
            f"An error occurred: {str(e)}. Please refresh the page."
        ], color="danger")

        return error_navbar, error_content, {'authenticated': False}
init_database()

if __name__ == '__main__':
    print("🚀 USC Institutional Research Portal Starting...")
    print("✅ Database initialized")
    print("✅ Built-in components loaded")
    print("📍 Server: http://localhost:8050")
    print("🔐 Auth: http://localhost:5000/login")

    app.run_server(debug=True, port=8050)