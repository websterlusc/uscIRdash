import dash_bootstrap_components as dbc
from dash import html, dcc
from datetime import datetime
import pandas as pd

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

def create_dashboard():
    """Create dashboard page for authenticated users"""
    return dbc.Container([
        # Welcome Header
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.H1([
                        html.I(className="fas fa-tachometer-alt me-3"),
                        "USC Institutional Research Dashboard"
                    ], className="mb-3", style={"color": USC_COLORS["primary_green"]}),
                    html.P("Welcome to your personalized data portal. Access reports, analytics, and insights.",
                           className="lead text-muted mb-4")
                ])
            ])
        ], className="mb-4"),

        # Quick Stats Row
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.Div([
                            html.I(className="fas fa-users fa-2x mb-2", 
                                   style={"color": USC_COLORS["primary_green"]}),
                            html.H3("3,110", className="mb-1", 
                                    style={"color": USC_COLORS["primary_green"], "fontWeight": "700"}),
                            html.P("Current Enrollment", className="mb-0 text-muted")
                        ], className="text-center")
                    ])
                ], className="h-100 shadow-sm")
            ], md=3, sm=6, className="mb-4"),

            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.Div([
                            html.I(className="fas fa-graduation-cap fa-2x mb-2", 
                                   style={"color": USC_COLORS["secondary_green"]}),
                            html.H3("850+", className="mb-1", 
                                    style={"color": USC_COLORS["primary_green"], "fontWeight": "700"}),
                            html.P("2024 Graduates", className="mb-0 text-muted")
                        ], className="text-center")
                    ])
                ], className="h-100 shadow-sm")
            ], md=3, sm=6, className="mb-4"),

            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.Div([
                            html.I(className="fas fa-globe-americas fa-2x mb-2", 
                                   style={"color": USC_COLORS["accent_yellow"]}),
                            html.H3("40+", className="mb-1", 
                                    style={"color": USC_COLORS["primary_green"], "fontWeight": "700"}),
                            html.P("Countries Represented", className="mb-0 text-muted")
                        ], className="text-center")
                    ])
                ], className="h-100 shadow-sm")
            ], md=3, sm=6, className="mb-4"),

            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.Div([
                            html.I(className="fas fa-award fa-2x mb-2", 
                                   style={"color": USC_COLORS["primary_green"]}),
                            html.H3("97", className="mb-1", 
                                    style={"color": USC_COLORS["primary_green"], "fontWeight": "700"}),
                            html.P("Years of Excellence", className="mb-0 text-muted")
                        ], className="text-center")
                    ])
                ], className="h-100 shadow-sm")
            ], md=3, sm=6, className="mb-4")
        ]),

        # Main Dashboard Content
        dbc.Row([
            # Left Column - Quick Access
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.H5([
                            html.I(className="fas fa-rocket me-2"),
                            "Quick Access"
                        ], className="mb-0")
                    ]),
                    dbc.CardBody([
                        dbc.ListGroup([
                            dbc.ListGroupItem([
                                html.Div([
                                    html.I(className="fas fa-book me-2"),
                                    "Interactive Factbook"
                                ], className="d-flex align-items-center"),
                                dbc.Badge("Admin Only", color="warning", className="ms-auto")
                            ], href="/factbook", action=True),

                            dbc.ListGroupItem([
                                html.Div([
                                    html.I(className="fas fa-chart-bar me-2"),
                                    "Enrollment Analytics"
                                ], className="d-flex align-items-center"),
                                dbc.Badge("Coming Soon", color="secondary", className="ms-auto")
                            ], action=True, disabled=True),

                            dbc.ListGroupItem([
                                html.Div([
                                    html.I(className="fas fa-file-alt me-2"),
                                    "Custom Reports"
                                ], className="d-flex align-items-center"),
                                dbc.Badge("Coming Soon", color="secondary", className="ms-auto")
                            ], action=True, disabled=True),

                            dbc.ListGroupItem([
                                html.Div([
                                    html.I(className="fas fa-users-cog me-2"),
                                    "Alumni Portal"
                                ], className="d-flex align-items-center"),
                                dbc.Badge("Coming Soon", color="secondary", className="ms-auto")
                            ], action=True, disabled=True),

                            dbc.ListGroupItem([
                                html.Div([
                                    html.I(className="fas fa-download me-2"),
                                    "Data Exports"
                                ], className="d-flex align-items-center"),
                                dbc.Badge("Coming Soon", color="secondary", className="ms-auto")
                            ], action=True, disabled=True)
                        ], flush=True)
                    ])
                ], className="shadow-sm mb-4")
            ], md=4),

            # Right Column - Recent Activity & Announcements
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.H5([
                            html.I(className="fas fa-bullhorn me-2"),
                            "Announcements"
                        ], className="mb-0")
                    ]),
                    dbc.CardBody([
                        html.Div([
                            dbc.Alert([
                                html.H6([
                                    html.I(className="fas fa-star me-2"),
                                    "USC Factbook 2024 Released!"
                                ], className="alert-heading mb-2"),
                                html.P("The comprehensive 2024 factbook is now available with updated enrollment, financial, and operational data.", className="mb-2"),
                                html.Small("Published: December 2024", className="text-muted")
                            ], color="success", className="mb-3"),

                            dbc.Alert([
                                html.H6([
                                    html.I(className="fas fa-calendar-alt me-2"),
                                    "Vision 2027 Planning"
                                ], className="alert-heading mb-2"),
                                html.P("Strategic planning continues for USC's centennial celebration and future goals.", className="mb-2"),
                                html.Small("Ongoing Initiative", className="text-muted")
                            ], color="info", className="mb-3"),

                            dbc.Alert([
                                html.H6([
                                    html.I(className="fas fa-tools me-2"),
                                    "System Updates"
                                ], className="alert-heading mb-2"),
                                html.P("New features and improvements are being added regularly to enhance your experience.", className="mb-2"),
                                html.Small("Last Updated: January 2025", className="text-muted")
                            ], color="light", className="mb-0")
                        ])
                    ])
                ], className="shadow-sm")
            ], md=8)
        ]),

        # Bottom Section - Help & Support
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.H5([
                            html.I(className="fas fa-question-circle me-2"),
                            "Need Help?"
                        ], className="mb-0")
                    ]),
                    dbc.CardBody([
                        dbc.Row([
                            dbc.Col([
                                html.H6("Contact Information", className="mb-3"),
                                html.P([
                                    html.I(className="fas fa-user me-2"),
                                    html.Strong("Nordian C. Swaby Robinson"),
                                    html.Br(),
                                    "Director, Institutional Research",
                                    html.Br(),
                                    html.I(className="fas fa-envelope me-2"),
                                    html.A("ir@usc.edu.tt", href="mailto:ir@usc.edu.tt"),
                                    html.Br(),
                                    html.I(className="fas fa-phone me-2"),
                                    "(868) 662-2241 Ext. 1004"
                                ], className="mb-0")
                            ], md=6),
                            dbc.Col([
                                html.H6("Technical Support", className="mb-3"),
                                html.P([
                                    html.I(className="fas fa-user me-2"),
                                    html.Strong("Liam Webster"),
                                    html.Br(),
                                    "Web Developer, Institutional Research",
                                    html.Br(),
                                    html.I(className="fas fa-envelope me-2"),
                                    html.A("websterl@usc.edu.tt", href="mailto:websterl@usc.edu.tt"),
                                    html.Br(),
                                    html.I(className="fas fa-phone me-2"),
                                    "(868) 662-2241 Ext. 1003"
                                ], className="mb-0")
                            ], md=6)
                        ])
                    ])
                ], className="shadow-sm")
            ])
        ], className="mt-4"),

        # Session Debug Info (only shown for testing)
        html.Div([
            dbc.Card([
                dbc.CardHeader("Session Information"),
                dbc.CardBody([
                    html.P(id="session-debug-info", className="small text-muted mb-1"),
                    html.Div(id="session-details")
                ])
            ], className="mt-4")
        ], id="debug-section", style={"display": "none"})  # Hidden by default

    ], className="py-4")