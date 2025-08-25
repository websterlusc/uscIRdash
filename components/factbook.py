"""
Factbook Landing Page for USC Institutional Research Web App

This module provides a centralized hub for accessing all factbook reports and data.
"""

from dash import html, dcc, callback, Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
from config import USC_COLORS
from data_loader import data_loader

def create_factbook_overview_cards():
    """Create overview cards showing key institutional metrics"""

    # Get sample data for overview
    student_labour_data = data_loader.load_student_labour_data()
    enrollment_data = data_loader.load_enrollment_data()
    graduation_data = data_loader.load_graduation_data()
    financial_data = data_loader.load_financial_data()

    # Calculate overview metrics
    if student_labour_data and 'employment' in student_labour_data:
        latest_employment = student_labour_data['employment'].iloc[-1]
        total_employment = latest_employment['Academic Employment'] + latest_employment['Non-Academic Employment']
    else:
        total_employment = 155  # Fallback

    if enrollment_data and 'total_enrollment' in enrollment_data:
        current_enrollment = enrollment_data['total_enrollment'].iloc[-1]['Total Students']
    else:
        current_enrollment = 3110  # Fallback

    if graduation_data and 'graduates' in graduation_data:
        total_graduates = graduation_data['graduates']['Graduates'].sum()
    else:
        total_graduates = 143  # Fallback

    cards = [
        dbc.Card([
            dbc.CardBody([
                html.Div([
                    html.I(className="fas fa-user-graduate fa-3x text-primary mb-3"),
                    html.H3(f"{current_enrollment:,}", className="text-primary mb-1"),
                    html.P("Current Enrollment", className="card-text mb-2"),
                    html.Small("Academic Year 2024-2025", className="text-muted")
                ], className="text-center")
            ])
        ], className="h-100"),

        dbc.Card([
            dbc.CardBody([
                html.Div([
                    html.I(className="fas fa-users-cog fa-3x text-success mb-3"),
                    html.H3(f"{total_employment}", className="text-success mb-1"),
                    html.P("Student Employment", className="card-text mb-2"),
                    html.Small("Academic & Non-Academic", className="text-muted")
                ], className="text-center")
            ])
        ], className="h-100"),

        dbc.Card([
            dbc.CardBody([
                html.Div([
                    html.I(className="fas fa-graduation-cap fa-3x text-warning mb-3"),
                    html.H3(f"{total_graduates}", className="text-warning mb-1"),
                    html.P("Recent Graduates", className="card-text mb-2"),
                    html.Small("May 2025 Graduation", className="text-muted")
                ], className="text-center")
            ])
        ], className="h-100"),

        dbc.Card([
            dbc.CardBody([
                html.Div([
                    html.I(className="fas fa-chart-line fa-3x text-info mb-3"),
                    html.H3("25+", className="text-info mb-1"),
                    html.P("Data Reports", className="card-text mb-2"),
                    html.Small("Comprehensive Analytics", className="text-muted")
                ], className="text-center")
            ])
        ], className="h-100")
    ]

    return cards

def create_factbook_sections():
    """Create the main factbook sections with report links"""

    sections = [
        {
            "title": "Student Services",
            "description": "Comprehensive data on student life, employment, and support services",
            "icon": "fas fa-users",
            "color": "primary",
            "reports": [
                {"name": "Student Labour Report", "url": "/student-labour", "icon": "fas fa-users-cog", "description": "Employment statistics and costs"},
                {"name": "Enrollment Data", "url": "/enrollment", "icon": "fas fa-user-graduate", "description": "Student enrollment trends"},
                {"name": "Student Demographics", "url": "/demographics", "icon": "fas fa-chart-pie", "description": "Population breakdown and analysis"},
                {"name": "Student Support Services", "url": "/support-services", "icon": "fas fa-hands-helping", "description": "Counseling and support metrics"},
            ]
        },
        {
            "title": "Academic Affairs",
            "description": "Data on academic programs, faculty, and educational outcomes",
            "icon": "fas fa-graduation-cap",
            "color": "success",
            "reports": [
                {"name": "Graduation Reports", "url": "/graduation", "icon": "fas fa-graduation-cap", "description": "Graduate outcomes and statistics"},
                {"name": "Program Offerings", "url": "/programs", "icon": "fas fa-book-open", "description": "Academic program data"},
                {"name": "Faculty Statistics", "url": "/faculty", "icon": "fas fa-chalkboard-teacher", "description": "Faculty demographics and load"},
                {"name": "Teaching Load Analysis", "url": "/teaching-load", "icon": "fas fa-calendar-alt", "description": "Course and workload distribution"},
            ]
        },
        {
            "title": "Financial Affairs",
            "description": "Financial data, budgets, and institutional funding sources",
            "icon": "fas fa-dollar-sign",
            "color": "warning",
            "reports": [
                {"name": "Financial Overview", "url": "/financial", "icon": "fas fa-chart-bar", "description": "Revenue and expenditure analysis"},
                {"name": "Scholarships & Aid", "url": "/scholarships", "icon": "fas fa-award", "description": "Student financial assistance"},
                {"name": "Subsidies & Grants", "url": "/subsidies", "icon": "fas fa-hand-holding-usd", "description": "External funding sources"},
                {"name": "Debt Management", "url": "/debt", "icon": "fas fa-credit-card", "description": "Institutional debt analysis"},
            ]
        },
        {
            "title": "Operations & Governance",
            "description": "Administrative data, governance metrics, and operational statistics",
            "icon": "fas fa-cogs",
            "color": "info",
            "reports": [
                {"name": "HR Data & Appointments", "url": "/hr-data", "icon": "fas fa-user-tie", "description": "Human resources analytics"},
                {"name": "Governance Structure", "url": "/governance-data", "icon": "fas fa-sitemap", "description": "Administrative organization"},
                {"name": "Outreach Activities", "url": "/outreach", "icon": "fas fa-handshake", "description": "Community engagement metrics"},
                {"name": "Income Generating Units", "url": "/income-units", "icon": "fas fa-industry", "description": "Revenue generating departments"},
            ]
        }
    ]

    return sections

# Create layout as a function that can be called
def create_factbook_layout():
    """Create the layout for the factbook landing page"""
    overview_cards = create_factbook_overview_cards()
    sections = create_factbook_sections()

    return dbc.Container([
        # Header section
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.Img(src="/assets/usc-logo.png", height="80px", className="me-4"),
                    html.Div([
                        html.H1([
                            "USC Factbook"
                        ], className="mb-2", style={"color": USC_COLORS["primary_green"], "fontWeight": "700"}),
                        html.P(
                            "Comprehensive institutional data and analytics for evidence-based decision making",
                            className="lead mb-0", style={"color": USC_COLORS["text_gray"]}
                        )
                    ])
                ], className="d-flex align-items-center mb-4")
            ])
        ]),

        # Overview cards
        dbc.Row([
            dbc.Col([
                html.H3("Institutional Overview", className="mb-4",
                       style={"color": USC_COLORS["primary_green"], "fontWeight": "600"})
            ])
        ]),
        dbc.Row([
            dbc.Col(card, md=3, className="mb-4") for card in overview_cards
        ]),

        # Quick access buttons
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H5("Quick Access", className="card-title mb-3"),
                        dbc.ButtonGroup([
                            dbc.Button([
                                html.I(className="fas fa-download me-2"),
                                "Export All Data"
                            ], color="outline-primary", size="sm"),
                            dbc.Button([
                                html.I(className="fas fa-calendar me-2"),
                                "Academic Calendar"
                            ], color="outline-secondary", size="sm"),
                            dbc.Button([
                                html.I(className="fas fa-chart-line me-2"),
                                "Trends Dashboard"
                            ], color="outline-success", size="sm"),
                            dbc.Button([
                                html.I(className="fas fa-file-pdf me-2"),
                                "Annual Report"
                            ], color="outline-warning", size="sm"),
                        ], className="flex-wrap")
                    ])
                ])
            ], md=12, className="mb-4")
        ]),

        # Main sections
        html.Hr(className="my-5"),

        dbc.Row([
            dbc.Col([
                html.H2("Factbook Sections", className="text-center mb-5",
                       style={"color": USC_COLORS["primary_green"], "fontWeight": "700"})
            ])
        ]),

        # Create section cards
        *[dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        dbc.Row([
                            dbc.Col([
                                html.H4([
                                    html.I(className=f"{section['icon']} me-3",
                                           style={"color": USC_COLORS.get(section['color'], USC_COLORS['primary_green'])}),
                                    section['title']
                                ], className="mb-0", style={"color": USC_COLORS["primary_green"]})
                            ], md=8),
                            dbc.Col([
                                dbc.Badge(f"{len(section['reports'])} Reports",
                                         color=section['color'], className="float-end")
                            ], md=4)
                        ])
                    ]),
                    dbc.CardBody([
                        html.P(section['description'], className="text-muted mb-4"),
                        dbc.Row([
                            dbc.Col([
                                dbc.Card([
                                    dbc.CardBody([
                                        html.Div([
                                            html.I(className=f"{report['icon']} fa-2x mb-3",
                                                   style={"color": USC_COLORS.get(section['color'], USC_COLORS['primary_green'])}),
                                            html.H6(report['name'], className="card-title mb-2"),
                                            html.P(report['description'], className="card-text text-muted small mb-3"),
                                            dbc.Button("View Report", href=report['url'],
                                                     color=section['color'], size="sm", className="w-100")
                                        ], className="text-center")
                                    ])
                                ], className="h-100 shadow-sm")
                            ], md=6, lg=3, className="mb-3") for report in section['reports']
                        ])
                    ])
                ], className="mb-5 shadow")
            ], md=12)
        ]) for section in sections],

        # Footer section
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        dbc.Row([
                            dbc.Col([
                                html.H5("Data Management", className="mb-3"),
                                html.P("All data is updated regularly and reflects the most current institutional information available."),
                                html.P("Last updated: August 14, 2025", className="text-muted small")
                            ], md=4),
                            dbc.Col([
                                html.H5("Contact Information", className="mb-3"),
                                html.P([
                                    "Nordian C. Swaby Robinson", html.Br(),
                                    "Director, Institutional Research", html.Br(),
                                    html.A("ir@usc.edu.tt", href="mailto:ir@usc.edu.tt")
                                ])
                            ], md=4),
                            dbc.Col([
                                html.H5("Technical Support", className="mb-3"),
                                html.P([
                                    "Liam Webster", html.Br(),
                                    "Web Developer", html.Br(),
                                    html.A("websterl@usc.edu.tt", href="mailto:websterl@usc.edu.tt")
                                ])
                            ], md=4)
                        ])
                    ])
                ], className="bg-light")
            ], md=12)
        ])
    ], fluid=True, className="py-4")

# Create the layout by calling the function
layout = create_factbook_layout()