import dash
from dash import dcc, html, Input, Output, State, callback, dash_table, ctx
import dash_bootstrap_components as dbc
from datetime import datetime, timedelta
import pandas as pd
import sqlite3
import hashlib
import secrets
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import re

# Initialize the Dash app with Bootstrap theme
app = dash.Dash(__name__,
                external_stylesheets=[dbc.themes.BOOTSTRAP],
                meta_tags=[
                    {"name": "viewport", "content": "width=device-width, initial-scale=1"}
                ])

# Expose server for deployment
server = app.server

# USC Brand Colors (from brand guidelines)
USC_COLORS = {
    'primary_green': '#1B5E20',  # USC Green
    'secondary_green': '#4CAF50',
    'accent_yellow': '#FDD835',
    'white': '#FFFFFF',
    'light_gray': '#F5F5F5',
    'dark_gray': '#424242',
    'text_gray': '#666666'
}


# Database setup
def init_database():
    """Initialize the access requests database"""
    conn = sqlite3.connect('usc_access.db')
    cursor = conn.cursor()

    # Access requests table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS access_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            department TEXT NOT NULL,
            position TEXT NOT NULL,
            is_usc_employee BOOLEAN NOT NULL,
            access_type TEXT NOT NULL,
            justification TEXT,
            requested_duration INTEGER DEFAULT 30,
            status TEXT DEFAULT 'pending',
            approved_by TEXT,
            approved_date DATETIME,
            approved_duration INTEGER,
            access_token TEXT,
            token_expires DATETIME,
            notes TEXT
        )
    ''')

    # Active sessions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS active_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL,
            access_token TEXT NOT NULL,
            access_type TEXT NOT NULL,
            created_date DATETIME DEFAULT CURRENT_TIMESTAMP,
            expires_date DATETIME NOT NULL,
            last_used DATETIME,
            ip_address TEXT,
            notes TEXT
        )
    ''')

    # Admin sessions table (for tracking admin logins)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS admin_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT UNIQUE NOT NULL,
            created_date DATETIME DEFAULT CURRENT_TIMESTAMP,
            expires_date DATETIME NOT NULL,
            ip_address TEXT
        )
    ''')

    conn.commit()
    conn.close()


# Initialize database
init_database()


def generate_session_id():
    """Generate a secure session ID"""
    return secrets.token_urlsafe(32)


def generate_access_token():
    """Generate a secure access token"""
    return secrets.token_urlsafe(32)


def send_email_notification(to_email, subject, body):
    """Send email notification"""
    try:
        # For demo purposes - in production, configure proper SMTP
        print(f"EMAIL TO: {to_email}")
        print(f"SUBJECT: {subject}")
        print(f"BODY: {body}")
        print("-" * 50)
        return True
    except Exception as e:
        print(f"Email error: {e}")
        return False


def create_admin_session(session_id):
    """Create a new admin session"""
    try:
        conn = sqlite3.connect('usc_access.db')
        cursor = conn.cursor()

        expires_date = datetime.now() + timedelta(hours=8)  # 8-hour session

        cursor.execute('''
            INSERT OR REPLACE INTO admin_sessions (session_id, expires_date)
            VALUES (?, ?)
        ''', (session_id, expires_date))

        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Session creation error: {e}")
        return False


def validate_admin_session(session_id):
    """Validate if admin session is still active"""
    if not session_id:
        return False

    try:
        conn = sqlite3.connect('usc_access.db')
        cursor = conn.cursor()

        cursor.execute('''
            SELECT expires_date FROM admin_sessions 
            WHERE session_id = ? AND expires_date > datetime('now')
        ''', (session_id,))

        result = cursor.fetchone()
        conn.close()

        return result is not None
    except Exception as e:
        print(f"Session validation error: {e}")
        return False


def get_requests_data(status_filter=None):
    """Get requests data from database"""
    try:
        conn = sqlite3.connect('usc_access.db')
        if status_filter:
            query = '''
                SELECT id, timestamp, name, email, department, position, 
                       is_usc_employee, access_type, justification, requested_duration, status
                FROM access_requests 
                WHERE status = ?
                ORDER BY timestamp DESC
            '''
            df = pd.read_sql_query(query, conn, params=[status_filter])
        else:
            query = '''
                SELECT id, timestamp, name, email, department, position, 
                       is_usc_employee, access_type, status, approved_by, approved_date, approved_duration
                FROM access_requests 
                ORDER BY timestamp DESC
            '''
            df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    except Exception as e:
        print(f"Database error: {e}")
        return pd.DataFrame()


# Get base URL for deployment
def get_base_url():
    """Get the base URL for links (local vs deployed)"""
    if os.environ.get('RENDER'):
        return "https://uscirdash.onrender.com/"
    else:
        return "http://127.0.0.1"


BASE_URL = get_base_url()

# Inject custom CSS styles
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
        /* USC Brand Custom Styles */
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

        /* Typography */
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

        .text-white h1, .text-white h2, .text-white h3, .text-white h4, .text-white h5, .text-white h6 {
            color: white !important;
        }

        /* Custom navbar styling */
        .navbar {
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            border-radius: 0 !important;
        }

        .navbar-toggler {
            border: none !important;
            border-radius: 0 !important;
        }

        .navbar-toggler:focus {
            box-shadow: none !important;
        }

        /* Dropdown menu styling */
        .dropdown-menu {
            border-radius: 0 !important;
            border: 1px solid #1B5E20 !important;
        }

        .dropdown-item:hover {
            background-color: #F5F5F5 !important;
            color: #1B5E20 !important;
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


def create_navbar():
    """Create the main navigation bar"""
    return dbc.NavbarSimple(
        children=[
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
            dbc.DropdownMenu(
                children=[
                    dbc.DropdownMenuItem("Student Services", href="#student-services"),
                    dbc.DropdownMenuItem("Counselling", href="#counselling"),
                    dbc.DropdownMenuItem("Spiritual Development", href="#spiritual"),
                    dbc.DropdownMenuItem("Campus Life", href="#campus-life"),
                ],
                nav=True,
                in_navbar=True,
                label="Student Life",
            ),
            dbc.NavItem(dbc.NavLink("Factbook", href="#factbook")),
            dbc.NavItem(dbc.NavLink("Alumni Portal", href="#alumni")),
            dbc.NavItem(dbc.NavLink("Request Access", href="?request")),
            dbc.NavItem(dbc.NavLink("Contact", href="#contact")),
        ],
        brand=html.Div([
            html.Img(src="/assets/usc-logo.png", height="40", className="me-2"),
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
        ], className="d-flex align-items-center"),
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
                            style={"fontSize": "1.1rem", "opacity": "0.95",
                                   "textShadow": "1px 1px 2px rgba(0,0,0,0.3)"}),
                        html.Div([
                            dbc.Button([
                                html.I(className="fas fa-key me-2"),
                                "Request Access"
                            ],
                                href="?request",
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
    """Create quick statistics cards"""
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
                        html.Div([
                            html.I(className=f"{stat['icon']} fa-2x mb-3",
                                   style={"color": USC_COLORS["primary_green"]})
                        ], className="text-center"),
                        html.H3(stat["value"],
                                className="text-center mb-2",
                                style={"color": USC_COLORS["primary_green"], "fontWeight": "700"}),
                        html.H6(stat["title"],
                                className="text-center mb-1",
                                style={"fontWeight": "600", "color": USC_COLORS["primary_green"]}),
                        html.P(stat["subtitle"],
                               className="text-center text-muted mb-0",
                               style={"fontSize": "0.9rem"})
                    ])
                ])
            ], className="h-100 stats-card")
        ], md=3, sm=6, className="mb-4")
        cards.append(card)

    return dbc.Container([
        html.H2("USC at a Glance",
                className="text-center mb-5",
                style={"color": USC_COLORS["primary_green"], "fontWeight": "700"}),
        dbc.Row(cards)
    ], className="py-5")


def create_feature_cards():
    """Create feature cards for main sections"""
    features = [
        {
            "title": "Academic Excellence",
            "description": "Comprehensive data on enrollment trends, graduation rates, and academic program performance across all schools and departments.",
            "icon": "fas fa-graduation-cap",
            "info": "Available in full interactive dashboard"
        },
        {
            "title": "Financial Transparency",
            "description": "Detailed financial reports, funding sources, scholarships, and budget analysis to ensure responsible stewardship.",
            "icon": "fas fa-chart-line",
            "info": "Contact IR for detailed financial reports"
        },
        {
            "title": "Alumni Network",
            "description": "Connect with USC graduates worldwide, explore career opportunities, and access alumni services through our comprehensive portal.",
            "icon": "fas fa-users-cog",
            "info": "Alumni portal available for registered users"
        },
        {
            "title": "Interactive Factbook",
            "description": "Dynamic visualizations and comprehensive reports providing three-year trends across all university metrics.",
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
                        html.Div([
                            html.I(className=f"{feature['icon']} fa-3x text-primary mb-3")
                        ], className="text-center"),
                        html.H5(feature["title"],
                                className="card-title text-center mb-3",
                                style={"fontWeight": "600", "color": USC_COLORS["primary_green"]}),
                        html.P(feature["description"],
                               className="card-text text-center mb-3",
                               style={"color": USC_COLORS["text_gray"], "fontSize": "0.95rem"}),
                        html.P(feature["info"],
                               className="text-center text-muted mb-4",
                               style={"fontSize": "0.85rem", "fontStyle": "italic"}),
                        html.Div([
                            dbc.Button([
                                "Request Access ",
                                html.I(className="fas fa-key ms-1")
                            ],
                                href="?request",
                                color="primary",
                                className="w-100",
                                style={"borderRadius": "0", "fontWeight": "500"})
                        ])
                    ])
                ])
            ], className="h-100 feature-card")
        ], md=6, lg=3, className="mb-4")
        cards.append(card)

    return dbc.Container([
        html.H2("Explore Our Data",
                className="text-center mb-5",
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
    """Create contact and leadership section"""
    return dbc.Container([
        html.H2("Department Leadership & Contact",
                className="text-center mb-5", id="contact",
                style={"color": USC_COLORS["primary_green"], "fontWeight": "700"}),

        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H5("Nordian C. Swaby Robinson",
                                style={"fontWeight": "600", "color": USC_COLORS["primary_green"]}),
                        html.P("Director, Institutional Research",
                               className="text-muted mb-3",
                               style={"fontSize": "1.1rem"}),
                        html.H6("Contact Information", className="mb-3",
                                style={"color": USC_COLORS["primary_green"]}),
                        html.P([
                            html.I(className="fas fa-phone me-2"),
                            html.Strong("Phone: "), " 1 (868) 662-2241 Ext. 1004"
                        ], className="mb-2"),
                        html.P([
                            html.I(className="fas fa-envelope me-2"),
                            html.Strong("Email: "),
                            html.A("ir@usc.edu.tt",
                                   href="mailto:ir@usc.edu.tt",
                                   style={"color": USC_COLORS["primary_green"]})
                        ], className="mb-2"),
                        html.P([
                            html.I(className="fas fa-map-marker-alt me-2"),
                            html.Strong("Office: "), "Administration Building"
                        ], className="mb-2"),
                        html.P([
                            html.I(className="fas fa-clock me-2"),
                            html.Strong("Hours: "), "Monday - Thursday, 8:00 AM - 4:00 PM"
                        ], className="mb-0")
                    ])
                ])
            ], md=6),

            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H5("Liam Webster",
                                style={"fontWeight": "600", "color": USC_COLORS["primary_green"]}),
                        html.P("Web Developer, Institutional Research",
                               className="text-muted mb-3",
                               style={"fontSize": "1.1rem"}),
                        html.H6("Contact Information", className="mb-3",
                                style={"color": USC_COLORS["primary_green"]}),
                        html.P([
                            html.I(className="fas fa-phone me-2"),
                            html.Strong("Phone: "), " 1 (868) 662-2241 Ext. 1003"
                        ], className="mb-2"),
                        html.P([
                            html.I(className="fas fa-envelope me-2"),
                            html.Strong("Email: "),
                            html.A("websterl@usc.edu.tt",
                                   href="mailto:websterl@usc.edu.tt",
                                   style={"color": USC_COLORS["primary_green"]})
                        ], className="mb-2"),
                        html.P([
                            html.I(className="fas fa-map-marker-alt me-2"),
                            html.Strong("Office: "), "Administration Building"
                        ], className="mb-2"),
                        html.P([
                            html.I(className="fas fa-clock me-2"),
                            html.Strong("Hours: "), "Monday - Thursday, 8:00 AM - 4:00 PM"
                        ], className="mb-0")
                    ])
                ])
            ], md=6)
        ]),

        html.Hr(className="my-5"),

        dbc.Row([
            dbc.Col([
                html.H5("Access Our Systems", className="mb-3", style={"color": USC_COLORS["primary_green"]}),
                html.P(
                    "For access to our comprehensive data systems, please submit an access request:",
                    className="mb-3"),
                html.Ul([
                    html.Li("Interactive Factbook with live data visualizations"),
                    html.Li("Alumni Portal and networking database"),
                    html.Li("Financial reporting and analytics"),
                    html.Li("Custom reports and analysis")
                ], className="mb-4"),
                html.Div([
                    dbc.Button([
                        html.I(className="fas fa-key me-2"),
                        "Request System Access"
                    ],
                        href="?request",
                        color="primary",
                        size="lg",
                        className="me-2 mb-2",
                        style={"borderRadius": "0"}),
                    dbc.Button([
                        html.I(className="fas fa-external-link-alt me-2"),
                        "USC Website"
                    ],
                        href="https://www.usc.edu.tt",
                        target="_blank",
                        color="outline-secondary",
                        className="mb-2",
                        style={"borderRadius": "0"})
                ])
            ], md=6),

            dbc.Col([
                html.H5("Data Services Available", className="mb-3", style={"color": USC_COLORS["primary_green"]}),
                html.P("Our department provides comprehensive data services:", className="mb-2"),
                html.Ul([
                    html.Li("Custom data analysis and reporting"),
                    html.Li("Alumni tracking and engagement metrics"),
                    html.Li("Historical trend analysis"),
                    html.Li("Benchmarking studies"),
                    html.Li("Survey design and analysis"),
                    html.Li("Strategic planning support")
                ], style={"fontSize": "0.95rem"}),
                dbc.Alert([
                    html.I(className="fas fa-info-circle me-2"),
                    html.Strong("Access Required: "),
                    "Interactive Factbook and Alumni Portal require approved access. ",
                    html.A("Submit a request", href="?request", className="alert-link"),
                    " to get started."
                ], color="info", className="mt-3")
            ], md=6)
        ])
    ], className="py-5")


def create_footer():
    """Create the footer section"""
    return html.Footer([
        dbc.Container([
            dbc.Row([
                dbc.Col([
                    html.H5("University of the Southern Caribbean", className="text-white mb-3"),
                    html.P([
                        "Maracas Royal Road, Maracas Valley,",
                        html.Br(),
                        "St. Joseph, Trinidad and Tobago"
                    ], className="text-white-50"),
                    html.P([
                        "1 (868) 662-2241",
                        html.Br(),
                        "Email: info@usc.edu.tt"
                    ], className="text-white-50")
                ], md=4),
                dbc.Col([
                    html.H6("Quick Links", className="text-white mb-3"),
                    html.Ul([
                        html.Li(html.A("USC Website", href="https://www.usc.edu.tt", className="text-white-50",
                                       target="_blank")),
                        html.Li(html.A("Request Access", href="?request", className="text-white-50")),
                        html.Li(html.A("Contact IR", href="mailto:ir@usc.edu.tt", className="text-white-50")),
                        html.Li(html.A("Student Portal", href="#", className="text-white-50")),
                    ], className="list-unstyled")
                ], md=4),
                dbc.Col([
                    html.H6("Institutional Research", className="text-white mb-3"),
                    html.P("Nordian C. Swaby Robinson", className="text-white-50 mb-1"),
                    html.P("Director, Institutional Research", className="text-white-50 mb-3"),
                    html.P([
                        "Phone: 1 (868) 662-2241 Ext. 1004",
                        html.Br(),
                        "Email: ir@usc.edu.tt"
                    ], className="text-white-50")
                ], md=4)
            ]),
            html.Hr(className="my-4", style={"borderColor": "rgba(255,255,255,0.2)"}),
            dbc.Row([
                dbc.Col([
                    html.P([
                        f"© {datetime.now().year} University of the Southern Caribbean. ",
                        "All rights reserved. | ",
                        html.A("Privacy Policy", href="#", className="text-white-50"),
                        " | ",
                        html.A("Terms of Use", href="#", className="text-white-50")
                    ], className="text-center text-white-50 mb-0")
                ])
            ])
        ], fluid=True)
    ], className="footer")


def create_access_request_form():
    """Create the access request form page"""
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.H3([
                            html.I(className="fas fa-key me-2"),
                            "Request System Access"
                        ], className="text-white mb-0")
                    ]),
                    dbc.CardBody([
                        html.P([
                            "Please complete this form to request access to USC's Institutional Research systems. ",
                            "Our team will review your request and respond within 1-2 business days."
                        ], className="mb-4", style={"fontSize": "1.1rem"}),

                        html.Div(id="request-form-alert", className="mb-4"),

                        dbc.Form([
                            dbc.Row([
                                dbc.Col([
                                    dbc.Label([
                                        html.I(className="fas fa-user me-2"),
                                        "Full Name *"
                                    ], className="fw-bold"),
                                    dbc.Input(id="req-name", type="text", required=True,
                                              placeholder="Enter your full name")
                                ], md=6),
                                dbc.Col([
                                    dbc.Label([
                                        html.I(className="fas fa-envelope me-2"),
                                        "Email Address *"
                                    ], className="fw-bold"),
                                    dbc.Input(id="req-email", type="email", required=True,
                                              placeholder="your.email@domain.com")
                                ], md=6)
                            ], className="mb-4"),

                            dbc.Row([
                                dbc.Col([
                                    dbc.Label([
                                        html.I(className="fas fa-building me-2"),
                                        "Department/Organization *"
                                    ], className="fw-bold"),
                                    dbc.Input(id="req-department", type="text", required=True,
                                              placeholder="e.g., Finance, Academic Affairs, External Partner")
                                ], md=6),
                                dbc.Col([
                                    dbc.Label([
                                        html.I(className="fas fa-id-badge me-2"),
                                        "Position/Title *"
                                    ], className="fw-bold"),
                                    dbc.Input(id="req-position", type="text", required=True,
                                              placeholder="e.g., Manager, Director, Analyst")
                                ], md=6)
                            ], className="mb-4"),

                            dbc.Row([
                                dbc.Col([
                                    dbc.Label([
                                        html.I(className="fas fa-university me-2"),
                                        "USC Employee?"
                                    ], className="fw-bold"),
                                    dbc.RadioItems(
                                        id="req-usc-employee",
                                        options=[
                                            {"label": " Yes - USC Employee/Faculty/Staff", "value": True},
                                            {"label": " No - External Partner/Consultant", "value": False}
                                        ],
                                        value=True,
                                        inline=False,
                                        className="mt-2"
                                    )
                                ], md=12)
                            ], className="mb-4"),

                            dbc.Row([
                                dbc.Col([
                                    dbc.Label([
                                        html.I(className="fas fa-database me-2"),
                                        "Access Needed For *"
                                    ], className="fw-bold"),
                                    dbc.Checklist(
                                        id="req-access-type",
                                        options=[
                                            {"label": " Interactive Factbook (Data Analytics & Reports)",
                                             "value": "factbook"},
                                            {"label": " Alumni Portal (Graduate Database & Networking)",
                                             "value": "alumni"}
                                        ],
                                        value=["factbook"],
                                        className="mt-2"
                                    )
                                ], md=6),
                                dbc.Col([
                                    dbc.Label([
                                        html.I(className="fas fa-calendar-alt me-2"),
                                        "Requested Access Duration"
                                    ], className="fw-bold"),
                                    dbc.Select(
                                        id="req-duration",
                                        options=[
                                            {"label": "1 week (7 days)", "value": 7},
                                            {"label": "2 weeks (14 days)", "value": 14},
                                            {"label": "1 month (30 days)", "value": 30},
                                            {"label": "2 months (60 days)", "value": 60},
                                            {"label": "3 months (90 days)", "value": 90}
                                        ],
                                        value=30,
                                        className="mt-2"
                                    )
                                ], md=6)
                            ], className="mb-4"),

                            dbc.Row([
                                dbc.Col([
                                    dbc.Label([
                                        html.I(className="fas fa-clipboard-list me-2"),
                                        "Justification/Purpose *"
                                    ], className="fw-bold"),
                                    dbc.Textarea(
                                        id="req-justification",
                                        placeholder="Please explain in detail:\n• Why you need access to these systems\n• How you will use the data\n• What specific information you're looking for\n• Any relevant projects or reports you're working on",
                                        rows=6,
                                        required=True,
                                        className="mt-2"
                                    )
                                ])
                            ], className="mb-4"),

                            html.Hr(),

                            dbc.Row([
                                dbc.Col([
                                    dbc.Alert([
                                        html.I(className="fas fa-info-circle me-2"),
                                        html.Strong("Review Process: "),
                                        "Your request will be reviewed by the Institutional Research team. ",
                                        "USC employees typically receive faster approval. You will receive an email ",
                                        "notification once your request is processed."
                                    ], color="info", className="mb-4")
                                ])
                            ]),

                            dbc.Row([
                                dbc.Col([
                                    dbc.Button([
                                        html.I(className="fas fa-paper-plane me-2"),
                                        "Submit Access Request"
                                    ],
                                        id="submit-access-request",
                                        color="primary",
                                        size="lg",
                                        className="w-100",
                                        style={"borderRadius": "0", "fontWeight": "600", "padding": "15px"})
                                ], md=8, className="mx-auto")
                            ])
                        ])
                    ])
                ])
            ], lg=10, className="mx-auto")
        ])
    ], className="py-5")


def create_admin_login():
    """Simple admin login form with session management"""
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.H4([
                            html.I(className="fas fa-shield-alt me-2"),
                            "Admin Login"
                        ], className="text-white mb-0")
                    ]),
                    dbc.CardBody([
                        dbc.Alert([
                            html.I(className="fas fa-lock me-2"),
                            "This area is restricted to authorized IR team members only."
                        ], color="warning", className="mb-4"),

                        dbc.Form([
                            dbc.Row([
                                dbc.Col([
                                    dbc.Label("Admin Password", className="fw-bold"),
                                    dbc.Input(id="admin-password", type="password",
                                              placeholder="Enter admin password",
                                              className="mb-3")
                                ])
                            ]),
                            dbc.Button([
                                html.I(className="fas fa-sign-in-alt me-2"),
                                "Login"
                            ], id="admin-login-btn", color="primary", className="w-100",
                                style={"borderRadius": "0"})
                        ]),
                        html.Div(id="admin-login-alert", className="mt-3")
                    ])
                ])
            ], md=6, className="mx-auto")
        ])
    ], className="py-5")


def create_admin_dashboard():
    """Admin dashboard for managing requests"""
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.H2([
                        html.I(className="fas fa-shield-alt me-2"),
                        "Access Request Management"
                    ], className="mb-2"),
                    html.P("Manage system access requests and generate access links.",
                           className="text-muted mb-4")
                ]),

                dbc.Row([
                    dbc.Col([
                        dbc.Button([
                            html.I(className="fas fa-sign-out-alt me-2"),
                            "Logout"
                        ], id="admin-logout-btn", color="outline-secondary", size="sm",
                            style={"borderRadius": "0"})
                    ], className="text-end mb-4")
                ]),

                dbc.Tabs([
                    dbc.Tab(label="Pending Requests", tab_id="pending-tab"),
                    dbc.Tab(label="All Requests", tab_id="all-tab"),
                    dbc.Tab(label="Generate Access Link", tab_id="generate-tab")
                ], id="admin-tabs", active_tab="pending-tab"),

                html.Div(id="admin-dashboard-content", className="mt-4")
            ])
        ])
    ], className="py-5")


# Main app layout with URL routing and session management
app.layout = html.Div([
    dcc.Location(id="url", refresh=False),
    dcc.Store(id="session-store", storage_type="session"),
    html.Div(id="page-layout")
])


# Main callback for page routing with session validation
@app.callback(
    Output("page-layout", "children"),
    [Input("url", "search")],
    [State("session-store", "data")]
)
def display_page_content(search, session_data):
    if search == "?request":
        return html.Div([
            create_navbar(),
            create_access_request_form(),
            create_footer()
        ])
    elif search == "?admin":
        return html.Div([
            create_navbar(),
            create_admin_login()
        ], style={"backgroundColor": "#f8f9fa", "minHeight": "100vh"})
    elif search == "?dashboard":
        # Check session validation for dashboard access
        session_id = session_data.get("session_id") if session_data else None
        if validate_admin_session(session_id):
            return html.Div([
                create_navbar(),
                create_admin_dashboard()
            ], style={"backgroundColor": "#f8f9fa", "minHeight": "100vh"})
        else:
            # Redirect to login if session invalid
            return html.Div([
                create_navbar(),
                create_admin_login(),
                dbc.Alert([
                    html.I(className="fas fa-exclamation-triangle me-2"),
                    "Session expired. Please login again."
                ], color="warning", dismissable=True)
            ], style={"backgroundColor": "#f8f9fa", "minHeight": "100vh"})
    else:
        # Default home page
        return html.Div([
            create_navbar(),
            html.Div([
                create_hero_section(),
                create_quick_stats(),
                create_feature_cards(),
                create_mission_section(),
                create_contact_section(),
            ], className="page-content"),
            create_footer()
        ])


# Access request form submission callback
@app.callback(
    Output("request-form-alert", "children"),
    [Input("submit-access-request", "n_clicks")],
    [State("req-name", "value"),
     State("req-email", "value"),
     State("req-department", "value"),
     State("req-position", "value"),
     State("req-usc-employee", "value"),
     State("req-access-type", "value"),
     State("req-duration", "value"),
     State("req-justification", "value")]
)
def submit_access_request_form(n_clicks, name, email, department, position, is_usc_employee,
                               access_type, duration, justification):
    if not n_clicks:
        return ""

    if not all([name, email, department, position, access_type, justification]):
        return dbc.Alert([
            html.I(className="fas fa-exclamation-triangle me-2"),
            "Please fill in all required fields."
        ], color="danger", dismissable=True)

    if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
        return dbc.Alert([
            html.I(className="fas fa-exclamation-triangle me-2"),
            "Please enter a valid email address."
        ], color="danger", dismissable=True)

    try:
        # Insert request into database
        conn = sqlite3.connect('usc_access.db')
        cursor = conn.cursor()

        access_type_str = ','.join(access_type) if isinstance(access_type, list) else access_type

        cursor.execute('''
            INSERT INTO access_requests 
            (name, email, department, position, is_usc_employee, access_type, justification, requested_duration)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (name, email, department, position, is_usc_employee, access_type_str, justification, duration))

        request_id = cursor.lastrowid
        conn.commit()
        conn.close()

        # Send email notification to IR team
        employee_type = "USC Employee" if is_usc_employee else "External Partner"
        email_subject = f"New Access Request #{request_id} - {name} ({employee_type})"
        email_body = f"""
New access request received:

Request ID: {request_id}
Name: {name}
Email: {email}
Department: {department}
Position: {position}
Employee Type: {employee_type}
Access Type: {access_type_str}
Requested Duration: {duration} days

Justification:
{justification}

Please review this request in the admin dashboard at:
{BASE_URL}:8050?dashboard
        """

        send_email_notification("ir@usc.edu.tt", email_subject, email_body)

        return dbc.Alert([
            html.I(className="fas fa-check-circle me-2"),
            html.Strong("Request Submitted Successfully!"), html.Br(),
            f"Your access request (ID: {request_id}) has been submitted and the IR team has been notified. ",
            f"You will receive an email at {email} once your request is reviewed. ",
            "USC employees typically receive faster processing."
        ], color="success", dismissable=False)

    except Exception as e:
        return dbc.Alert([
            html.I(className="fas fa-exclamation-triangle me-2"),
            f"Error submitting request: {str(e)}"
        ], color="danger", dismissable=True)


# Admin login callback with session creation
@app.callback(
    [Output("admin-login-alert", "children"),
     Output("session-store", "data")],
    [Input("admin-login-btn", "n_clicks")],
    [State("admin-password", "value"),
     State("session-store", "data")]
)
def handle_admin_login(n_clicks, password, session_data):
    if not n_clicks:
        return "", session_data or {}

    # Check password
    if password == "usc_ir_admin_2025":
        # Generate new session
        session_id = generate_session_id()
        if create_admin_session(session_id):
            new_session_data = {"session_id": session_id, "authenticated": True}
            return dbc.Alert([
                html.I(className="fas fa-check-circle me-2"),
                "Login successful! ",
                html.A("Go to Dashboard", href="?dashboard", className="alert-link")
            ], color="success"), new_session_data
        else:
            return dbc.Alert([
                html.I(className="fas fa-exclamation-triangle me-2"),
                "Session creation failed. Please try again."
            ], color="danger", dismissable=True), session_data or {}
    else:
        return dbc.Alert([
            html.I(className="fas fa-exclamation-triangle me-2"),
            "Invalid password. Please try again."
        ], color="danger", dismissable=True), session_data or {}


# Admin logout callback
@app.callback(
    Output("url", "search"),
    [Input("admin-logout-btn", "n_clicks")],
    [State("session-store", "data")]
)
def handle_admin_logout(n_clicks, session_data):
    if n_clicks and session_data and session_data.get("session_id"):
        # Clear session from database
        try:
            conn = sqlite3.connect('usc_access.db')
            cursor = conn.cursor()
            cursor.execute("DELETE FROM admin_sessions WHERE session_id = ?",
                           (session_data["session_id"],))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Logout error: {e}")

        return "?admin"  # Redirect to login
    return ""


# Admin dashboard content callback
@app.callback(
    Output("admin-dashboard-content", "children"),
    [Input("admin-tabs", "active_tab")],
    [State("session-store", "data")]
)
def update_admin_dashboard(active_tab, session_data):
    # Validate session
    session_id = session_data.get("session_id") if session_data else None
    if not validate_admin_session(session_id):
        return dbc.Alert("Session expired. Please login again.", color="danger")

    if active_tab == "pending-tab":
        df = get_requests_data("pending")
        if df.empty:
            return dbc.Alert([
                html.I(className="fas fa-info-circle me-2"),
                "No pending requests."
            ], color="info")

        # Create cards for each pending request
        cards = []
        for _, row in df.iterrows():
            employee_badge = dbc.Badge("USC Employee" if row['is_usc_employee'] else "External",
                                       color="success" if row['is_usc_employee'] else "warning")

            card = dbc.Card([
                dbc.CardHeader([
                    html.Div([
                        html.H5(f"{row['name']} - {row['email']}", className="mb-0"),
                        employee_badge
                    ], className="d-flex justify-content-between align-items-center")
                ]),
                dbc.CardBody([
                    html.P([
                        html.Strong("Department: "), row['department'], html.Br(),
                        html.Strong("Position: "), row['position'], html.Br(),
                        html.Strong("Access Type: "), row['access_type'], html.Br(),
                        html.Strong("Requested Duration: "), f"{row['requested_duration']} days", html.Br(),
                        html.Strong("Submitted: "), row['timestamp']
                    ]),
                    html.P([
                        html.Strong("Justification: "), html.Br(),
                        html.Small(row['justification'], className="text-muted")
                    ]),
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Approve for (days):"),
                            dbc.Input(id=f"duration-{row['id']}", type="number",
                                      value=row['requested_duration'], min=1, max=365)
                        ], md=4),
                        dbc.Col([
                            dbc.Button([
                                html.I(className="fas fa-check me-2"),
                                "Approve"
                            ], id=f"approve-{row['id']}", color="success", className="me-2",
                                style={"borderRadius": "0"}),
                            dbc.Button([
                                html.I(className="fas fa-times me-2"),
                                "Deny"
                            ], id=f"deny-{row['id']}", color="danger", style={"borderRadius": "0"})
                        ], md=8, className="d-flex align-items-end")
                    ])
                ])
            ], className="mb-3")
            cards.append(card)

        return html.Div([
            html.H4(f"Pending Requests ({len(df)})"),
            html.Div(cards)
        ])

    elif active_tab == "all-tab":
        df = get_requests_data()
        if df.empty:
            return dbc.Alert("No requests found.", color="info")

        return html.Div([
            html.H4(f"All Requests ({len(df)})"),
            dbc.Table.from_dataframe(df, striped=True, bordered=True, hover=True, responsive=True)
        ])

    elif active_tab == "generate-tab":
        return html.Div([
            html.H4("Generate Direct Access Link"),
            dbc.Card([
                dbc.CardBody([
                    dbc.Form([
                        dbc.Row([
                            dbc.Col([
                                dbc.Label("Email Address"),
                                dbc.Input(id="generate-email", type="email", placeholder="user@example.com")
                            ], md=6),
                            dbc.Col([
                                dbc.Label("Access Duration (days)"),
                                dbc.Input(id="generate-duration", type="number", value=30, min=1, max=365)
                            ], md=6)
                        ], className="mb-3"),
                        dbc.Row([
                            dbc.Col([
                                dbc.Label("Access Type"),
                                dbc.Checklist(
                                    id="generate-access-type",
                                    options=[
                                        {"label": "Factbook", "value": "factbook"},
                                        {"label": "Alumni Portal", "value": "alumni"}
                                    ],
                                    value=["factbook"]
                                )
                            ], md=6),
                            dbc.Col([
                                dbc.Label("Notes (optional)"),
                                dbc.Textarea(id="generate-notes", rows=3)
                            ], md=6)
                        ], className="mb-3"),
                        dbc.Button([
                            html.I(className="fas fa-key me-2"),
                            "Generate Access Link"
                        ], id="generate-link-btn", color="primary", style={"borderRadius": "0"})
                    ])
                ])
            ]),
            html.Div(id="generated-link-result", className="mt-3")
        ])


# Generate access link callback
@app.callback(
    Output("generated-link-result", "children"),
    [Input("generate-link-btn", "n_clicks")],
    [State("generate-email", "value"),
     State("generate-duration", "value"),
     State("generate-access-type", "value"),
     State("generate-notes", "value"),
     State("session-store", "data")]
)
def generate_access_link(n_clicks, email, duration, access_type, notes, session_data):
    if not n_clicks or not email:
        return ""

    # Validate session
    session_id = session_data.get("session_id") if session_data else None
    if not validate_admin_session(session_id):
        return dbc.Alert("Session expired. Please login again.", color="danger")

    try:
        # Generate access token
        token = generate_access_token()
        expires_date = datetime.now() + timedelta(days=duration)

        # Store in database
        conn = sqlite3.connect('usc_access.db')
        cursor = conn.cursor()

        access_type_str = ','.join(access_type) if isinstance(access_type, list) else access_type

        cursor.execute('''
            INSERT INTO active_sessions (email, access_token, access_type, expires_date, notes)
            VALUES (?, ?, ?, ?, ?)
        ''', (email, token, access_type_str, expires_date, notes))

        conn.commit()
        conn.close()

        # Create access links
        factbook_link = f"{BASE_URL}:8501?token={token}" if "factbook" in access_type else None
        alumni_link = f"{BASE_URL}:8502?token={token}" if "alumni" in access_type else None

        return dbc.Alert([
            html.H5([
                html.I(className="fas fa-check-circle me-2"),
                "Access Link Generated Successfully!"
            ], className="mb-3"),
            html.P([html.Strong("Email: "), email]),
            html.P([html.Strong("Duration: "), f"{duration} days"]),
            html.P([html.Strong("Expires: "), expires_date.strftime("%Y-%m-%d %H:%M")]),
            html.Hr(),
            html.P(html.Strong("Access Links:")),
            html.Ul([
                html.Li([
                    "Factbook: ",
                    html.A(factbook_link, href=factbook_link, target="_blank")
                ]) if factbook_link else None,
                html.Li([
                    "Alumni Portal: ",
                    html.A(alumni_link, href=alumni_link, target="_blank")
                ]) if alumni_link else None
            ]),
            html.Small([
                html.I(className="fas fa-envelope me-2"),
                "Send these links to the user. They will expire automatically."
            ])
        ], color="success")

    except Exception as e:
        return dbc.Alert(f"Error generating link: {str(e)}", color="danger")


if __name__ == "__main__":
    # Use different settings for local vs production
    port = int(os.environ.get('PORT', 8050))
    debug = not os.environ.get('RENDER')

    app.run(debug=debug, host='0.0.0.0', port=port)