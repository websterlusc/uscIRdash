import dash
from dash import dcc, html, Input, Output, State, callback, ctx, dash_table
import dash_bootstrap_components as dbc
from datetime import datetime, timedelta
import pandas as pd
import sqlite3
import hashlib
import secrets
import os
import re
import jwt
import json
from pages.public.about_usc import create_about_usc_layout
from pages.public.vision_mission_motto import create_vision_mission_motto_layout
from pages.public.governance import create_governance_layout
# Configuration
SECRET_KEY = os.environ.get('SECRET_KEY', 'usc-ir-secret-key-2025-change-in-production')
DATABASE = 'usc_ir_new.db'
TOKEN_EXPIRY_HOURS = 8
BASE_URL = os.environ.get('BASE_URL', 'http://localhost')

# Initialize the Dash app
app = dash.Dash(__name__,
                external_stylesheets=[dbc.themes.BOOTSTRAP],
                suppress_callback_exceptions=True,
                meta_tags=[
                    {"name": "viewport", "content": "width=device-width, initial-scale=1"}
                ])

server = app.server

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

# Inject custom CSS styles (keeping original look)
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
        /* USC Brand Custom Styles - Original Look */
        .navbar-brand {
            font-weight: bold !important;
            font-size: 1.2rem !important;
        }

        .nav-link {
            font-weight: 500 !important;
            transition: all 0.3s ease !important;
        }

        .nav-link:hover {
            color: #FDD835 !important;
            background-color: rgba(255, 255, 255, 0.1) !important;
            border-radius: 0 !important;
        }

        .btn-primary {
            background-color: #1B5E20 !important;
            border-color: #1B5E20 !important;
            border-radius: 0 !important;
            font-weight: 500 !important;
        }

        .btn-primary:hover {
            background-color: #4CAF50 !important;
            border-color: #4CAF50 !important;
        }

        .btn-warning {
            background-color: #FDD835 !important;
            border-color: #FDD835 !important;
            color: #1B5E20 !important;
            border-radius: 0 !important;
            font-weight: 500 !important;
        }

        .btn-outline-light, .btn-outline-primary, .btn-outline-secondary {
            border-radius: 0 !important;
            font-weight: 500 !important;
        }

        .card {
            border-radius: 0 !important;
            border: none !important;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1) !important;
        }

        .card-header {
            background-color: #1B5E20 !important;
            color: white !important;
            border-radius: 0 !important;
            font-weight: 600 !important;
        }

        .hero-section {
            background: linear-gradient(135deg, #1B5E20 0%, #4CAF50 100%);
            color: white;
            padding: 5rem 0;
        }

        .feature-card {
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }

        .feature-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 25px rgba(0,0,0,0.15) !important;
        }

        .stats-card {
            background: linear-gradient(45deg, #FDD835, #FFF59D);
            color: #1B5E20;
            border-radius: 0 !important;
        }

        .footer {
            background-color: #1B5E20;
            color: white;
            padding: 2rem 0;
            margin-top: 3rem;
        }

        .page-content {
            min-height: calc(100vh - 200px);
        }

        h1, h2, h3, h4, h5, h6 {
            color: #1B5E20 !important;
            font-weight: 600 !important;
        }

        .display-3 {
            font-weight: 700 !important;
        }

        .lead {
            color: #666666 !important;
        }

        .text-white h1, .text-white h2, .text-white h3 {
            color: white !important;
        }

        .navbar {
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            border-radius: 0 !important;
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


# ==================== DATABASE SETUP ====================

def init_database():
    """Initialize all required database tables"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # Users table with approval status
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            full_name TEXT NOT NULL,
            department TEXT,
            position TEXT,
            role TEXT DEFAULT 'user',
            is_active INTEGER DEFAULT 1,
            is_approved INTEGER DEFAULT 0,
            approved_by INTEGER,
            approved_at DATETIME,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            last_login DATETIME,
            password_reset_token TEXT,
            password_reset_expires DATETIME,
            FOREIGN KEY (approved_by) REFERENCES users (id)
        )
    ''')

    # Sessions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            token TEXT UNIQUE NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            expires_at DATETIME NOT NULL,
            ip_address TEXT,
            user_agent TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    # Access logs table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS access_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            action TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            ip_address TEXT,
            details TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    # Check if we need to create default admin
    cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'admin'")
    admin_count = cursor.fetchone()[0]

    if admin_count == 0:
        print("Creating default admin user...")
        admin_password = hash_password('admin123')
        cursor.execute('''
            INSERT INTO users (email, username, password_hash, full_name, department, position, role, is_active, is_approved)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', ('ir@usc.edu.tt', 'admin', admin_password, 'System Administrator',
              'Institutional Research', 'Director', 'admin', 1, 1))
        print("Default admin created - Username: admin, Password: admin123")

    conn.commit()
    conn.close()


# ==================== AUTHENTICATION FUNCTIONS ====================

def hash_password(password):
    """Hash password with salt"""
    salt = secrets.token_hex(16)
    password_hash = hashlib.pbkdf2_hmac('sha256',
                                        password.encode('utf-8'),
                                        salt.encode('utf-8'),
                                        100000)
    return f"{salt}:{password_hash.hex()}"


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


def generate_token(user_id):
    """Generate JWT token for user"""
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(hours=TOKEN_EXPIRY_HOURS),
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')


def decode_token(token):
    """Decode and validate JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload
    except:
        return None


def authenticate_user(email_or_username, password):
    """Authenticate user with email or username"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute('''
        SELECT id, email, username, password_hash, full_name, department, position, role, is_active, is_approved
        FROM users 
        WHERE (email = ? OR username = ?) AND is_active = 1
    ''', (email_or_username, email_or_username))

    user = cursor.fetchone()

    if user and verify_password(password, user[3]):
        if not user[9]:  # Check if approved
            conn.close()
            return {'success': False, 'message': 'Your account is pending approval. Please wait for admin approval.'}

        # Update last login
        cursor.execute('UPDATE users SET last_login = ? WHERE id = ?',
                       (datetime.now(), user[0]))
        conn.commit()

        # Create session token
        token = generate_token(user[0])

        # Store session
        expires_at = datetime.now() + timedelta(hours=TOKEN_EXPIRY_HOURS)
        cursor.execute('''
            INSERT INTO sessions (user_id, token, expires_at)
            VALUES (?, ?, ?)
        ''', (user[0], token, expires_at))
        conn.commit()

        conn.close()

        return {
            'success': True,
            'token': token,
            'user': {
                'id': user[0],
                'email': user[1],
                'username': user[2],
                'full_name': user[4],
                'department': user[5],
                'position': user[6],
                'role': user[7]
            }
        }

    conn.close()
    return {'success': False, 'message': 'Invalid credentials'}


def validate_session(token):
    """Validate user session"""
    if not token:
        return None

    payload = decode_token(token)
    if not payload:
        return None

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute('''
        SELECT u.id, u.email, u.username, u.full_name, u.department, u.position, u.role
        FROM sessions s
        JOIN users u ON s.user_id = u.id
        WHERE s.token = ? AND s.expires_at > ? AND u.is_active = 1 AND u.is_approved = 1
    ''', (token, datetime.now()))

    user = cursor.fetchone()
    conn.close()

    if user:
        return {
            'id': user[0],
            'email': user[1],
            'username': user[2],
            'full_name': user[3],
            'department': user[4],
            'position': user[5],
            'role': user[6]
        }
    return None


def logout_user(token):
    """Logout user by removing session"""
    if not token:
        return

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM sessions WHERE token = ?', (token,))
    conn.commit()
    conn.close()


def register_user(email, username, password, full_name, department=None, position=None):
    """Register new user (requires admin approval)"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute('SELECT id FROM users WHERE email = ? OR username = ?',
                   (email, username))
    if cursor.fetchone():
        conn.close()
        return {'success': False, 'message': 'Email or username already exists'}

    password_hash = hash_password(password)
    try:
        cursor.execute('''
            INSERT INTO users (email, username, password_hash, full_name, department, position, role, is_active, is_approved)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (email, username, password_hash, full_name, department, position, 'user', 1, 0))

        conn.commit()
        conn.close()

        return {'success': True, 'message': 'Registration successful! Your account is pending admin approval.'}
    except Exception as e:
        conn.close()
        return {'success': False, 'message': str(e)}


def change_user_password(user_id, current_password, new_password):
    """Change user's own password"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # Get current password hash
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


# ==================== UI COMPONENTS (Original Style) ====================

def create_navbar(user=None):
    """Create the main navigation bar with original styling"""
    nav_items = [
        dbc.NavItem(dbc.NavLink("Home", href="/", active="exact")),
        dbc.DropdownMenu(
            children=[
                dbc.DropdownMenuItem("About USC", href="#about"),
                dbc.DropdownMenuItem("Vision & Mission", href="#vision-mission"),
                dbc.DropdownMenuItem("Governance", href="#governance"),
                dbc.DropdownMenuItem("Leadership", href="#leadership"),
            ],
            nav=True,
            in_navbar=True,
            label="About Us",
        ),
    ]

    if user:
        nav_items.extend([
            dbc.DropdownMenu(
                children=[
                    dbc.DropdownMenuItem("Student Enrollment", href="#enrollment"),
                    dbc.DropdownMenuItem("Graduation Data", href="#graduation"),
                    dbc.DropdownMenuItem("Academic Programs", href="#programs"),
                    dbc.DropdownMenuItem("Faculty Statistics", href="#faculty"),
                ],
                nav=True,
                in_navbar=True,
                label="Academic Data",
            ),
            dbc.DropdownMenu(
                children=[
                    dbc.DropdownMenuItem("Financial Overview", href="#financial"),
                    dbc.DropdownMenuItem("Subsidies & Funding", href="#funding"),
                    dbc.DropdownMenuItem("Income Sources", href="#income"),
                    dbc.DropdownMenuItem("Scholarships", href="#scholarships"),
                ],
                nav=True,
                in_navbar=True,
                label="Financial Data",
            ),
            dbc.NavItem(dbc.NavLink("Factbook", href="#factbook")),
        ])

        if user['role'] == 'admin':
            nav_items.append(
                dbc.NavItem(dbc.NavLink("Admin", href="/admin", className="text-warning"))
            )

        # User menu with profile options
        nav_items.append(
            dbc.DropdownMenu(
                children=[
                    dbc.DropdownMenuItem(f"Signed in as: {user['full_name']}", disabled=True),
                    dbc.DropdownMenuItem(divider=True),
                    dbc.DropdownMenuItem("Profile", href="/profile"),
                    dbc.DropdownMenuItem("Change Password", href="/change-password"),
                    dbc.DropdownMenuItem(divider=True),
                    dbc.DropdownMenuItem("Logout", id="logout-btn"),
                ],
                nav=True,
                in_navbar=True,
                label=user['username'],
            )
        )
    else:
        nav_items.extend([
            dbc.NavItem(dbc.NavLink("Request Access", href="/request")),
            dbc.NavItem(dbc.NavLink("Contact", href="#contact")),
            dbc.NavItem(dbc.NavLink("Login", href="/login")),
        ])

    return dbc.NavbarSimple(
        children=nav_items,
        brand=html.Div([
            html.Div([
                html.Div("Institutional Research", style={
                    "fontWeight": "700",
                    "fontSize": "1.1rem",
                    "lineHeight": "1.1",
                    "color": "white"
                }),
                html.Div("University of the Southern Caribbean", style={
                    "fontSize": "0.85rem",
                    "fontWeight": "500",
                    "color": "white"
                })
            ])
        ]),
        brand_href="/",
        color=USC_COLORS['primary_green'],
        dark=True,
        fluid=True,
        className="mb-0"
    )


def create_hero_section():
    """Create the hero section with USC branding"""
    return html.Div([
        dbc.Container([
            dbc.Row([
                dbc.Col([
                    html.Div([
                        html.H1("Institutional Research",
                                className="display-3 text-white mb-4",
                                style={"fontWeight": "700", "textShadow": "2px 2px 4px rgba(0,0,0,0.3)"}),
                        html.P(
                            "Empowering data-driven decision making through comprehensive analysis and transparent reporting",
                            className="text-white mb-4",
                            style={"fontSize": "1.3rem", "textShadow": "1px 1px 2px rgba(0,0,0,0.3)"}),
                        html.P(
                            "Supporting USC's mission of transforming ordinary people into extraordinary servants of God through evidence-based insights",
                            className="text-white mb-5",
                            style={"fontSize": "1.1rem", "opacity": "0.95"}),
                        html.Div([
                            dbc.Button([
                                html.I(className="fas fa-key me-2"),
                                "Request Access"
                            ],
                                href="/request",
                                color="warning",
                                size="lg",
                                className="me-3 mb-3",
                                style={"borderRadius": "0", "fontWeight": "600", "padding": "12px 30px"}),
                            dbc.Button([
                                html.I(className="fas fa-info-circle me-2"),
                                "Learn More"
                            ],
                                href="#about",
                                color="outline-light",
                                size="lg",
                                className="mb-3",
                                style={"borderRadius": "0", "fontWeight": "600", "padding": "12px 30px"})
                        ])
                    ], className="text-center")
                ], lg=10, className="mx-auto"),
            ])
        ], fluid=True)
    ], className="hero-section")


def create_quick_stats():
    """Quick statistics cards"""
    stats = [
        {"title": "Total Enrollment", "value": "3,110", "subtitle": "As of May 2025", "icon": "fas fa-user-graduate"},
        {"title": "Alumni Network", "value": "15,000+", "subtitle": "Graduates Worldwide",
         "icon": "fas fa-globe-americas"},
        {"title": "Years of Excellence", "value": "97+", "subtitle": "Since 1927", "icon": "fas fa-award"},
        {"title": "Countries Represented", "value": "40+", "subtitle": "International Diversity", "icon": "fas fa-flag"}
    ]

    cards = []
    for stat in stats:
        card = dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.Div([
                        html.I(className=f"{stat['icon']} fa-2x mb-3",
                               style={"color": USC_COLORS["primary_green"]}),
                        html.H3(stat["value"], className="mb-2",
                                style={"color": USC_COLORS["primary_green"], "fontWeight": "700"}),
                        html.H6(stat["title"], className="mb-1",
                                style={"fontWeight": "600", "color": USC_COLORS["primary_green"]}),
                        html.P(stat["subtitle"], className="text-muted mb-0",
                               style={"fontSize": "0.9rem"})
                    ], className="text-center")
                ])
            ], className="h-100 stats-card")
        ], md=3, sm=6, className="mb-4")
        cards.append(card)

    return dbc.Container([
        html.H2("USC at a Glance", className="text-center mb-5",
                style={"color": USC_COLORS["primary_green"], "fontWeight": "700"}),
        dbc.Row(cards)
    ], className="py-5")


def create_feature_cards():
    """Create feature cards for main sections"""
    features = [
        {
            "title": "Academic Excellence",
            "description": "Comprehensive data on enrollment trends, graduation rates, and academic program performance.",
            "icon": "fas fa-graduation-cap",
            "info": "Available in full interactive dashboard"
        },
        {
            "title": "Financial Transparency",
            "description": "Detailed financial reports, funding sources, scholarships, and budget analysis.",
            "icon": "fas fa-chart-line",
            "info": "Contact IR for detailed financial reports"
        },
        {
            "title": "Alumni Network",
            "description": "Connect with USC graduates worldwide, explore career opportunities.",
            "icon": "fas fa-users-cog",
            "info": "Alumni portal available for registered users"
        },
        {
            "title": "Interactive Factbook",
            "description": "Dynamic visualizations and comprehensive reports providing three-year trends.",
            "icon": "fas fa-book-open",
            "info": "Full factbook system with live data"
        }
    ]

    cards = []
    for feature in features:
        card = dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.Div([
                        html.I(className=f"{feature['icon']} fa-3x text-primary mb-3"),
                        html.H5(feature["title"], className="card-title text-center mb-3",
                                style={"fontWeight": "600", "color": USC_COLORS["primary_green"]}),
                        html.P(feature["description"], className="card-text text-center mb-3",
                               style={"color": USC_COLORS["text_gray"]}),
                        html.P(feature["info"], className="text-center text-muted mb-4",
                               style={"fontSize": "0.85rem", "fontStyle": "italic"}),
                        html.Div([
                            dbc.Button("Request Access", href="/request", color="primary",
                                       className="w-100", style={"borderRadius": "0"})
                        ])
                    ])
                ])
            ], className="h-100 feature-card")
        ], md=6, lg=3, className="mb-4")
        cards.append(card)

    return dbc.Container([
        html.H2("Explore Our Data", className="text-center mb-5",
                style={"color": USC_COLORS["primary_green"], "fontWeight": "700"}),
        dbc.Row(cards)
    ], className="py-5")
def create_mission_section():
    """Create mission and about section"""
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.H3("About the Department",
                            className="mb-4", id="about",
                            style={"color": USC_COLORS["primary_green"], "fontWeight": "700"}),
                    html.P([
                        "The Department of Institutional Research takes great pride in supporting ",
                        html.Strong("data-driven decision making", style={"color": USC_COLORS["primary_green"]}),
                        " at the University of the Southern Caribbean. We provide comprehensive reports, ",
                        "trend analysis, and strategic insights to facilitate excellence in education ",
                        "and administration."
                    ], className="mb-3", style={"fontSize": "1.1rem", "lineHeight": "1.6"}),
                    html.P([
                        "Our work directly supports USC's mission of transforming ordinary people into ",
                        "extraordinary servants of God through transparent reporting and ",
                        "evidence-based planning for our centennial vision toward 2027."
                    ], className="mb-4", style={"fontSize": "1.1rem", "lineHeight": "1.6"}),
                    html.Blockquote([
                        html.P([
                            html.I(className="fas fa-quote-left me-2"),
                            '"The University of the Southern Caribbean seeks to transform ordinary people into extraordinary servants of God to humanity through a holistic tertiary educational experience."'
                        ], className="mb-2", style={"fontStyle": "italic", "color": USC_COLORS["primary_green"]}),
                        html.Footer("USC Mission Statement", className="blockquote-footer")
                    ], className="mb-4"),
                    dbc.Button([
                        html.I(className="fas fa-info-circle me-2"),
                        "Learn More About USC"
                    ],
                        href="https://www.usc.edu.tt",
                        target="_blank",
                        color="outline-primary",
                        size="lg",
                        style={"borderRadius": "0", "fontWeight": "500"})
                ])
            ], md=6),
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.H5([
                            html.I(className="fas fa-bullseye me-2"),
                            "Strategic Priorities"
                        ], className="text-white mb-0")
                    ]),
                    dbc.CardBody([
                        html.P("Guiding USC toward excellence in five key areas:", className="mb-3",
                               style={"fontWeight": "500"}),
                        html.Ul([
                            html.Li([
                                html.I(className="fas fa-cross me-2", style={"color": USC_COLORS["primary_green"]}),
                                html.Strong("Spiritual Ethos"),
                                " - Supporting our Christian mission and values"
                            ], className="mb-3"),
                            html.Li([
                                html.I(className="fas fa-trophy me-2", style={"color": USC_COLORS["primary_green"]}),
                                html.Strong("Academic Success"),
                                " - Enhancing educational outcomes and excellence"
                            ], className="mb-3"),
                            html.Li([
                                html.I(className="fas fa-chalkboard-teacher me-2",
                                       style={"color": USC_COLORS["primary_green"]}),
                                html.Strong("Faculty Development"),
                                " - Supporting and empowering our educators"
                            ], className="mb-3"),
                            html.Li([
                                html.I(className="fas fa-chart-line me-2",
                                       style={"color": USC_COLORS["primary_green"]}),
                                html.Strong("Financial Sustainability"),
                                " - Responsible stewardship and fiscal management"
                            ], className="mb-3"),
                            html.Li([
                                html.I(className="fas fa-cogs me-2", style={"color": USC_COLORS["primary_green"]}),
                                html.Strong("Operational Efficiency"),
                                " - Continuous improvement and innovation"
                            ])
                        ], className="list-unstyled mb-3"),
                        html.Hr(),
                        html.Div([
                            html.I(className="fas fa-calendar-alt me-2"),
                            html.Strong("Vision 2027: "),
                            "Celebrating our centennial year of excellence"
                        ], className="text-muted", style={"fontSize": "0.95rem"})
                    ])
                ])
            ], md=6)
        ], className="align-items-center"),
    ], className="py-5", style={"backgroundColor": USC_COLORS["light_gray"]})

def create_contact_section():
    """Create contact section"""
    return dbc.Container([
        html.H2("Department Leadership & Contact", className="text-center mb-5",
                style={"color": USC_COLORS["primary_green"], "fontWeight": "700"}),

        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H5("Nordian C. Swaby Robinson",
                                style={"fontWeight": "600", "color": USC_COLORS["primary_green"]}),
                        html.P("Director, Institutional Research", className="text-muted mb-3"),
                        html.P([html.I(className="fas fa-phone me-2"),
                                "1 (868) 662-2241 Ext. 1004"], className="mb-2"),
                        html.P([html.I(className="fas fa-envelope me-2"),
                                html.A("ir@usc.edu.tt", href="mailto:ir@usc.edu.tt")], className="mb-0")
                    ])
                ])
            ], md=6),

            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H5("Liam Webster",
                                style={"fontWeight": "600", "color": USC_COLORS["primary_green"]}),
                        html.P("Web Developer, Institutional Research", className="text-muted mb-3"),
                        html.P([html.I(className="fas fa-phone me-2"),
                                "1 (868) 662-2241 Ext. 1003"], className="mb-2"),
                        html.P([html.I(className="fas fa-envelope me-2"),
                                html.A("websterl@usc.edu.tt", href="mailto:websterl@usc.edu.tt")], className="mb-0")
                    ])
                ])
            ], md=6)
        ])
    ], className="py-5")


def create_footer():
    """Create footer section"""
    return html.Footer([
        dbc.Container([
            dbc.Row([
                dbc.Col([
                    html.H5("University of the Southern Caribbean", className="text-white mb-3"),
                    html.P("Maracas Royal Road, Maracas Valley, St. Joseph, Trinidad and Tobago",
                           className="text-white-50")
                ], md=4),
                dbc.Col([
                    html.H6("Quick Links", className="text-white mb-3"),
                    html.Ul([
                        html.Li(html.A("USC Website", href="https://www.usc.edu.tt",
                                       className="text-white-50", target="_blank")),
                        html.Li(html.A("Request Access", href="/request", className="text-white-50")),
                        html.Li(html.A("Contact IR", href="mailto:ir@usc.edu.tt", className="text-white-50"))
                    ], className="list-unstyled")
                ], md=4),
                dbc.Col([
                    html.H6("Institutional Research", className="text-white mb-3"),
                    html.P("Nordian C. Swaby Robinson", className="text-white-50 mb-1"),
                    html.P("Director, Institutional Research", className="text-white-50")
                ], md=4)
            ]),
            html.Hr(className="my-4", style={"borderColor": "rgba(255,255,255,0.2)"}),
            html.P(f"© {datetime.now().year} University of the Southern Caribbean. All rights reserved.",
                   className="text-center text-white-50 mb-0")
        ], fluid=True)
    ], className="footer")


def create_change_password_page(user):
    """Create change password page for logged-in users"""
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.H3([
                            html.I(className="fas fa-lock me-2"),
                            "Change Password"
                        ], className="text-white mb-0")
                    ]),
                    dbc.CardBody([
                        html.P(f"Change password for: {user['full_name']} ({user['username']})",
                               className="mb-4"),

                        html.Div(id="change-pwd-alert", className="mb-3"),

                        dbc.Form([
                            dbc.Row([
                                dbc.Col([
                                    dbc.Label("Current Password", className="fw-bold"),
                                    dbc.Input(id="current-password", type="password",
                                              placeholder="Enter current password")
                                ])
                            ], className="mb-3"),

                            dbc.Row([
                                dbc.Col([
                                    dbc.Label("New Password", className="fw-bold"),
                                    dbc.Input(id="new-password", type="password",
                                              placeholder="Enter new password (min 8 characters)"),
                                    dbc.FormText("Must be at least 8 characters")
                                ])
                            ], className="mb-3"),

                            dbc.Row([
                                dbc.Col([
                                    dbc.Label("Confirm New Password", className="fw-bold"),
                                    dbc.Input(id="confirm-new-password", type="password",
                                              placeholder="Re-enter new password")
                                ])
                            ], className="mb-4"),

                            dbc.Button([
                                html.I(className="fas fa-save me-2"),
                                "Change Password"
                            ], id="change-pwd-submit", color="primary", size="lg",
                                className="w-100", n_clicks=0, style={"borderRadius": "0"})
                        ])
                    ])
                ])
            ], md=6, className="mx-auto")
        ])
    ], className="py-5")


def create_profile_page(user):
    """Create user profile page"""
    return dbc.Container([
        html.H2("My Profile"),
        html.Hr(),
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Account Information"),
                    dbc.CardBody([
                        html.P([html.Strong("Username: "), user['username']]),
                        html.P([html.Strong("Email: "), user['email']]),
                        html.P([html.Strong("Full Name: "), user['full_name']]),
                        html.P([html.Strong("Department: "), user['department'] or "Not specified"]),
                        html.P([html.Strong("Position: "), user['position'] or "Not specified"]),
                        html.P([html.Strong("Account Type: "),
                                dbc.Badge(user['role'].upper(),
                                          color="danger" if user['role'] == "admin" else "primary")]),
                        html.Hr(),
                        dbc.ButtonGroup([
                            dbc.Button("Change Password", href="/change-password", color="primary"),
                            dbc.Button("Edit Profile", color="secondary", disabled=True)
                        ])
                    ])
                ])
            ], md=6),
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Available Systems"),
                    dbc.CardBody([
                        html.H5("Your Access:"),
                        html.Ul([
                            html.Li("Interactive Factbook (Coming Soon)"),
                            html.Li("Reports Generator (Coming Soon)"),
                            html.Li("Alumni Portal (Coming Soon)"),
                        ]),
                        html.Hr(),
                        html.P("Need additional access? Contact the IR team.", className="text-muted")
                    ])
                ])
            ], md=6)
        ])
    ], className="py-5")


def create_admin_dashboard(user):
    """Create admin dashboard with user management"""
    if user['role'] != 'admin':
        return dbc.Alert("Access denied", color="danger")

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # Get pending approvals count
    cursor.execute('SELECT COUNT(*) FROM users WHERE is_approved = 0 AND is_active = 1')
    pending_count = cursor.fetchone()[0]

    conn.close()

    return dbc.Container([
        html.H2([html.I(className="fas fa-shield-alt me-2"), "Admin Dashboard"]),
        html.Hr(),

        dbc.Tabs([
            dbc.Tab(label=f"Pending Approvals ({pending_count})", tab_id="pending"),
            dbc.Tab(label="User Management", tab_id="users"),
            dbc.Tab(label="Password Reset", tab_id="reset"),
            dbc.Tab(label="System Stats", tab_id="stats"),
        ], id="admin-tabs", active_tab="pending"),

        html.Div(id="admin-content", className="mt-4")
    ])


def create_login_page():
    """Create login page with original design"""
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.H3([
                            html.I(className="fas fa-sign-in-alt me-2"),
                            "Login to IR Portal"
                        ], className="text-white mb-0")
                    ]),
                    dbc.CardBody([
                        html.Div(id="login-alert", className="mb-3"),
                        dbc.Form([
                            dbc.Row([
                                dbc.Col([
                                    dbc.Label([
                                        html.I(className="fas fa-user me-2"),
                                        "Email or Username"
                                    ], className="fw-bold"),
                                    dbc.Input(id="login-email", type="text",
                                              placeholder="Enter email or username")
                                ])
                            ], className="mb-3"),
                            dbc.Row([
                                dbc.Col([
                                    dbc.Label([
                                        html.I(className="fas fa-lock me-2"),
                                        "Password"
                                    ], className="fw-bold"),
                                    dbc.Input(id="login-password", type="password",
                                              placeholder="Enter password")
                                ])
                            ], className="mb-4"),
                            dbc.Button([
                                html.I(className="fas fa-sign-in-alt me-2"),
                                "Login"
                            ], id="login-submit", color="primary", size="lg",
                                className="w-100", n_clicks=0, style={"borderRadius": "0"}),
                            html.Hr(),
                            html.P([
                                "Don't have an account? ",
                                dcc.Link("Register here", href="/register")
                            ], className="text-center")
                        ])
                    ])
                ])
            ], md=6, lg=5, className="mx-auto")
        ])
    ], className="py-5")


def create_register_page():
    """Create registration page"""
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.H3([
                            html.I(className="fas fa-user-plus me-2"),
                            "Create New Account"
                        ], className="text-white mb-0")
                    ]),
                    dbc.CardBody([
                        dbc.Alert([
                            html.I(className="fas fa-info-circle me-2"),
                            "Note: New accounts require admin approval before you can login."
                        ], color="info", className="mb-4"),

                        html.Div(id="register-alert", className="mb-3"),

                        dbc.Form([
                            dbc.Row([
                                dbc.Col([
                                    dbc.Label("Email *", className="fw-bold"),
                                    dbc.Input(id="register-email", type="email",
                                              placeholder="your.email@usc.edu.tt"),
                                ], md=6),
                                dbc.Col([
                                    dbc.Label("Username *", className="fw-bold"),
                                    dbc.Input(id="register-username", type="text",
                                              placeholder="Choose username"),
                                ], md=6)
                            ], className="mb-3"),

                            dbc.Row([
                                dbc.Col([
                                    dbc.Label("Full Name *", className="fw-bold"),
                                    dbc.Input(id="register-fullname", type="text",
                                              placeholder="Enter your full name"),
                                ])
                            ], className="mb-3"),

                            dbc.Row([
                                dbc.Col([
                                    dbc.Label("Department", className="fw-bold"),
                                    dbc.Input(id="register-department", type="text",
                                              placeholder="e.g., Finance, Academic Affairs"),
                                ], md=6),
                                dbc.Col([
                                    dbc.Label("Position", className="fw-bold"),
                                    dbc.Input(id="register-position", type="text",
                                              placeholder="e.g., Analyst, Manager"),
                                ], md=6)
                            ], className="mb-3"),

                            dbc.Row([
                                dbc.Col([
                                    dbc.Label("Password *", className="fw-bold"),
                                    dbc.Input(id="register-password", type="password",
                                              placeholder="Minimum 8 characters"),
                                    dbc.FormText("Must be at least 8 characters")
                                ], md=6),
                                dbc.Col([
                                    dbc.Label("Confirm Password *", className="fw-bold"),
                                    dbc.Input(id="register-confirm", type="password",
                                              placeholder="Re-enter password"),
                                ], md=6)
                            ], className="mb-4"),

                            dbc.Button([
                                html.I(className="fas fa-user-plus me-2"),
                                "Register"
                            ], id="register-submit", color="success", size="lg",
                                className="w-100", n_clicks=0, style={"borderRadius": "0"})
                        ])
                    ])
                ])
            ], md=8, className="mx-auto")
        ])
    ], className="py-5")


def create_home_page(user=None):
    """Create home page with original design"""
    if user:
        return dbc.Container([
            html.H2(f"Welcome, {user['full_name']}!"),
            html.P("You now have access to the USC Institutional Research systems."),
            html.Hr(),
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4("Factbook Access"),
                            html.P("Interactive data visualizations and reports"),
                            dbc.Button("Coming Soon", disabled=True)
                        ])
                    ])
                ], md=4),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4("Reports"),
                            html.P("Generate custom reports and analytics"),
                            dbc.Button("Coming Soon", disabled=True)
                        ])
                    ])
                ], md=4),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4("Alumni Portal"),
                            html.P("Connect with USC alumni network"),
                            dbc.Button("Coming Soon", disabled=True)
                        ])
                    ])
                ], md=4)
            ])
        ], className="py-5")
    else:
        return html.Div([
            create_hero_section(),
            create_quick_stats(),
            create_feature_cards(),
            create_mission_section(),
            create_contact_section(),
            create_footer()
        ])


def create_request_form():
    """Create access request form"""
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.H3([html.I(className="fas fa-key me-2"), "Request System Access"],
                                className="text-white mb-0")
                    ]),
                    dbc.CardBody([
                        html.P("Complete this form to request access. Admin approval required.", className="mb-4"),

                        dbc.Alert([
                            html.I(className="fas fa-info-circle me-2"),
                            "Note: You can also ", dcc.Link("register for an account", href="/register"),
                            " which will require admin approval."
                        ], color="info"),

                        html.P("For immediate assistance, please contact:"),
                        html.Ul([
                            html.Li("Nordian C. Swaby Robinson - ir@usc.edu.tt"),
                            html.Li("Liam Webster - websterl@usc.edu.tt")
                        ])
                    ])
                ])
            ], lg=8, className="mx-auto")
        ])
    ], className="py-5")


# ==================== MAIN APP LAYOUT ====================

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    dcc.Store(id='session-store', storage_type='session'),
    html.Div(id='navbar-container'),
    html.Div(id='page-content'),
    html.Div(id='hidden-div', style={'display': 'none'})
])


# ==================== CALLBACKS ====================

@app.callback(
    [Output('navbar-container', 'children'),
     Output('page-content', 'children')],
    [Input('url', 'pathname')],
    [State('session-store', 'data')]
)
def display_page(pathname, session_data):
    """Main router callback"""
    user = None
    if session_data and 'token' in session_data:
        user = validate_session(session_data['token'])

    navbar = create_navbar(user)
    if pathname == '/about-usc':
        return navbar, create_about_usc_layout()
    elif pathname == '/vision-mission-motto':
        return navbar, create_vision_mission_motto_layout()
    elif pathname == '/governance':
        return navbar, create_governance_layout()
    # Public pages
    elif pathname == '/login':
        return navbar, create_login_page()
    elif pathname == '/register':
        return navbar, create_register_page()
    elif pathname == '/request':
        return navbar, create_request_form()

    # Protected pages - require login
    if pathname == '/admin':
        if user and user['role'] == 'admin':
            return navbar, create_admin_dashboard(user)
        else:
            return navbar, dbc.Alert("Access denied. Admin privileges required.", color="danger")
    elif pathname == '/profile':
        if user:
            return navbar, create_profile_page(user)
        else:
            return navbar, dbc.Alert("Please login to view your profile.", color="warning")
    elif pathname == '/change-password':
        if user:
            return navbar, create_change_password_page(user)
        else:
            return navbar, dbc.Alert("Please login to change password.", color="warning")

    # Default to home
    return navbar, create_home_page(user)


@app.callback(
    Output('admin-content', 'children'),
    [Input('admin-tabs', 'active_tab')],
    [State('session-store', 'data')]
)
def render_admin_tab(active_tab, session_data):
    """Render admin tab content"""
    if not session_data or 'token' not in session_data:
        return dbc.Alert("Session expired", color="danger")

    user = validate_session(session_data['token'])
    if not user or user['role'] != 'admin':
        return dbc.Alert("Access denied", color="danger")

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    if active_tab == "pending":
        cursor.execute('''
            SELECT id, email, username, full_name, department, position, created_at
            FROM users 
            WHERE is_approved = 0 AND is_active = 1
            ORDER BY created_at DESC
        ''')
        pending = cursor.fetchall()
        conn.close()

        if not pending:
            return dbc.Alert("No pending approvals", color="info")

        cards = []
        for p in pending:
            card = dbc.Card([
                dbc.CardBody([
                    html.H5(p[3]),
                    html.P([html.Strong("Email: "), p[1]]),
                    html.P([html.Strong("Username: "), p[2]]),
                    html.P([html.Strong("Department: "), p[4] or "N/A"]),
                    html.P([html.Strong("Position: "), p[5] or "N/A"]),
                    html.P([html.Strong("Requested: "), p[6]], className="text-muted"),
                    dbc.ButtonGroup([
                        dbc.Button("Approve", id={"type": "approve-btn", "index": p[0]},
                                   color="success", size="sm"),
                        dbc.Button("Reject", id={"type": "reject-btn", "index": p[0]},
                                   color="danger", size="sm")
                    ])
                ])
            ], className="mb-3")
            cards.append(card)

        return html.Div(cards)

    elif active_tab == "users":
        cursor.execute('''
            SELECT id, email, username, full_name, department, role, is_approved, is_active
            FROM users 
            ORDER BY created_at DESC
        ''')
        users = cursor.fetchall()
        conn.close()

        table_data = []
        for u in users:
            table_data.append({
                'ID': u[0],
                'Email': u[1],
                'Username': u[2],
                'Name': u[3],
                'Department': u[4] or 'N/A',
                'Role': u[5],
                'Approved': '✅' if u[6] else '❌',
                'Active': '✅' if u[7] else '❌'
            })

        return dash_table.DataTable(
            data=table_data,
            columns=[{"name": i, "id": i} for i in table_data[0].keys()],
            style_cell={'textAlign': 'left'},
            style_data_conditional=[
                {
                    'if': {'column_id': 'Role', 'filter_query': '{Role} = admin'},
                    'backgroundColor': '#fff3cd'
                }
            ],
            page_size=10
        )

    elif active_tab == "reset":
        cursor.execute('SELECT id, username, email, full_name FROM users WHERE is_active = 1')
        users = cursor.fetchall()
        conn.close()

        return dbc.Card([
            dbc.CardBody([
                html.H5("Reset User Password"),
                dbc.Form([
                    dbc.Label("Select User"),
                    dbc.Select(
                        id="reset-user-select",
                        options=[{"label": f"{u[3]} ({u[1]})", "value": u[0]} for u in users]
                    ),
                    dbc.Label("New Password", className="mt-3"),
                    dbc.Input(id="reset-new-password", type="password", placeholder="Enter new password"),
                    dbc.Button("Reset Password", id="reset-password-btn", color="warning",
                               className="mt-3", n_clicks=0),
                    html.Div(id="reset-result", className="mt-3")
                ])
            ])
        ])

    elif active_tab == "stats":
        cursor.execute("SELECT COUNT(*) FROM users WHERE is_active = 1")
        total_users = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM users WHERE is_approved = 0 AND is_active = 1")
        pending = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM sessions WHERE expires_at > ?", (datetime.now(),))
        active = cursor.fetchone()[0]

        conn.close()

        return dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H1(total_users, className="text-center text-primary"),
                        html.P("Total Users", className="text-center")
                    ])
                ])
            ], md=4),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H1(pending, className="text-center text-warning"),
                        html.P("Pending Approvals", className="text-center")
                    ])
                ])
            ], md=4),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H1(active, className="text-center text-success"),
                        html.P("Active Sessions", className="text-center")
                    ])
                ])
            ], md=4)
        ])

    return html.Div()


@app.callback(
    Output('hidden-div', 'children'),
    [Input({'type': 'approve-btn', 'index': dash.dependencies.ALL}, 'n_clicks'),
     Input({'type': 'reject-btn', 'index': dash.dependencies.ALL}, 'n_clicks')],
    [State('session-store', 'data')]
)
def handle_approval(approve_clicks, reject_clicks, session_data):
    """Handle user approval/rejection"""
    if not ctx.triggered:
        return ""

    user = validate_session(session_data['token'])
    if not user or user['role'] != 'admin':
        return ""

    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    button_info = json.loads(button_id)
    user_id = button_info['index']
    action = button_info['type']

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    if action == 'approve-btn':
        cursor.execute('''
            UPDATE users 
            SET is_approved = 1, approved_by = ?, approved_at = ? 
            WHERE id = ?
        ''', (user['id'], datetime.now(), user_id))
    else:
        cursor.execute('UPDATE users SET is_active = 0 WHERE id = ?', (user_id,))

    conn.commit()
    conn.close()

    return ""


@app.callback(
    [Output('change-pwd-alert', 'children'),
     Output('url', 'pathname', allow_duplicate=True)],
    [Input('change-pwd-submit', 'n_clicks')],
    [State('current-password', 'value'),
     State('new-password', 'value'),
     State('confirm-new-password', 'value'),
     State('session-store', 'data')],
    prevent_initial_call=True
)
def handle_change_password(n_clicks, current_pwd, new_pwd, confirm_pwd, session_data):
    """Handle user password change"""
    if not n_clicks:
        return "", dash.no_update

    user = validate_session(session_data['token'])
    if not user:
        return dbc.Alert("Session expired. Please login again.", color="danger"), "/login"

    if not all([current_pwd, new_pwd, confirm_pwd]):
        return dbc.Alert("Please fill all fields", color="warning"), dash.no_update

    if new_pwd != confirm_pwd:
        return dbc.Alert("New passwords do not match", color="danger"), dash.no_update

    if len(new_pwd) < 8:
        return dbc.Alert("Password must be at least 8 characters", color="warning"), dash.no_update

    result = change_user_password(user['id'], current_pwd, new_pwd)

    if result['success']:
        return dbc.Alert(result['message'], color="success"), "/profile"
    else:
        return dbc.Alert(result['message'], color="danger"), dash.no_update


@app.callback(
    Output('reset-result', 'children'),
    [Input('reset-password-btn', 'n_clicks')],
    [State('reset-user-select', 'value'),
     State('reset-new-password', 'value'),
     State('session-store', 'data')]
)
def handle_password_reset(n_clicks, user_id, new_password, session_data):
    """Handle password reset by admin"""
    if not n_clicks or not user_id or not new_password:
        return ""

    user = validate_session(session_data['token'])
    if not user or user['role'] != 'admin':
        return dbc.Alert("Unauthorized", color="danger")

    if len(new_password) < 8:
        return dbc.Alert("Password must be at least 8 characters", color="warning")

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    password_hash = hash_password(new_password)
    cursor.execute('UPDATE users SET password_hash = ? WHERE id = ?', (password_hash, user_id))

    conn.commit()
    conn.close()

    return dbc.Alert("Password reset successfully!", color="success")

import traceback

@app.callback(
    [Output('session-store', 'data'),
     Output('login-alert', 'children'),
     Output('url', 'pathname', allow_duplicate=True)],
    [Input('login-submit', 'n_clicks')],
    [State('login-email', 'value'),
     State('login-password', 'value')],
    prevent_initial_call=True
)
def handle_login(n_clicks, email_or_username, password):
    try:
        if not n_clicks:
            return dash.no_update, "", dash.no_update

        if not email_or_username or not password:
            return dash.no_update, dbc.Alert("Please enter credentials", color="warning"), dash.no_update

        result = authenticate_user(email_or_username, password)

        if result['success']:
            session_data = {'token': result['token'], 'user': result['user']}
            return session_data, dbc.Alert("Login successful!", color="success"), "/"
        else:
            return dash.no_update, dbc.Alert(result['message'], color="danger"), dash.no_update

    except Exception as e:
        print("Error in handle_login callback:")
        traceback.print_exc()
        return dash.no_update, dbc.Alert(f"Unexpected error: {str(e)}", color="danger"), dash.no_update



@app.callback(
    [Output('register-alert', 'children'),
     Output('url', 'pathname', allow_duplicate=True)],
    [Input('register-submit', 'n_clicks')],
    [State('register-email', 'value'),
     State('register-username', 'value'),
     State('register-password', 'value'),
     State('register-confirm', 'value'),
     State('register-fullname', 'value'),
     State('register-department', 'value'),
     State('register-position', 'value')],
    prevent_initial_call=True
)
def handle_register(n_clicks, email, username, password, confirm, fullname, department, position):
    """Handle registration"""
    if not n_clicks:
        return "", dash.no_update

    if not all([email, username, password, fullname]):
        return dbc.Alert("Please fill all required fields", color="warning"), dash.no_update

    if password != confirm:
        return dbc.Alert("Passwords do not match", color="danger"), dash.no_update

    if len(password) < 8:
        return dbc.Alert("Password must be at least 8 characters", color="warning"), dash.no_update

    result = register_user(email, username, password, fullname, department, position)

    if result['success']:
        return dbc.Alert(result['message'], color="success"), "/login"
    else:
        return dbc.Alert(result['message'], color="danger"), dash.no_update


@app.callback(
    [Output('session-store', 'data', allow_duplicate=True),
     Output('url', 'pathname', allow_duplicate=True)],
    [Input('logout-btn', 'n_clicks')],
    [State('session-store', 'data')],
    prevent_initial_call=True
)
def handle_logout(n_clicks, session_data):
    """Handle logout"""
    if n_clicks and session_data and 'token' in session_data:
        logout_user(session_data['token'])
        return {}, "/login"
    return dash.no_update, dash.no_update


# Initialize database on startup
if __name__ == '__main__':
    print("=" * 60)
    print("USC INSTITUTIONAL RESEARCH PORTAL")
    print("=" * 60)
    init_database()
    print("Default admin: username='admin', password='admin123'")
    print("-" * 60)
    print("Server running on http://localhost:8050")
    print("=" * 60)
    app.run_server(debug=True, port=8050)