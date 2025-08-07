import dash
from dash import html, dcc, callback, Input, Output
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime

# Register the page
dash.register_page(__name__, path='/', name='Home')

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


def create_hero_section():
    """Create the hero section with USC branding"""
    return html.Div([
        dbc.Container([
            dbc.Row([
                dbc.Col([
                    html.Div([
                        html.H1("Institutional Research",
                                className="display-4 text-white mb-4",
                                style={"fontWeight": "700"}),
                        html.P(
                            "Empowering data-driven decision making through comprehensive analysis and transparent reporting",
                            className="lead text-white mb-4",
                            style={"fontSize": "1.25rem"}),
                        html.P(
                            "Providing strategic insights to support USC's mission of transforming ordinary people into extraordinary servants of God",
                            className="text-white mb-4",
                            style={"fontSize": "1.1rem", "opacity": "0.9"}),
                        html.Div([
                            dbc.Button("Explore Factbook",
                                       href="/factbook",
                                       color="warning",
                                       size="lg",
                                       className="me-3 mb-2",
                                       style={"borderRadius": "0", "fontWeight": "600"}),
                            dbc.Button("View Reports",
                                       href="/reports",
                                       color="outline-light",
                                       size="lg",
                                       className="mb-2",
                                       style={"borderRadius": "0", "fontWeight": "600"})
                        ])
                    ], className="text-center text-md-start")
                ], md=8),
                dbc.Col([
                    html.Div([
                        html.Img(src="/assets/usc-seal.png",
                                 className="img-fluid",
                                 style={"maxHeight": "300px", "opacity": "0.1"})
                    ], className="text-center d-none d-md-block")
                ], md=4)
            ])
        ], fluid=True)
    ], className="hero-section")


def create_quick_stats():
    """Create quick statistics cards"""
    stats = [
        {"title": "Total Enrollment", "value": "3,110", "subtitle": "As of May 2025", "icon": "👨‍🎓"},
        {"title": "Countries Represented", "value": "40+", "subtitle": "International Diversity", "icon": "🌍"},
        {"title": "Years of Excellence", "value": "97+", "subtitle": "Since 1927", "icon": "📚"},
        {"title": "Graduation Rate", "value": "85%", "subtitle": "Class of 2024", "icon": "🎓"}
    ]

    cards = []
    for stat in stats:
        card = dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.Div([
                        html.Div(stat["icon"],
                                 style={"fontSize": "2.5rem"},
                                 className="text-center mb-2"),
                        html.H3(stat["value"],
                                className="text-center mb-2",
                                style={"color": USC_COLORS["primary_green"], "fontWeight": "700"}),
                        html.H6(stat["title"],
                                className="text-center mb-1",
                                style={"fontWeight": "600"}),
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
            "icon": "📈",
            "link": "/enrollment",
            "color": USC_COLORS["primary_green"]
        },
        {
            "title": "Financial Transparency",
            "description": "Detailed financial reports, funding sources, scholarships, and budget analysis to ensure responsible stewardship.",
            "icon": "💰",
            "link": "/financial",
            "color": USC_COLORS["secondary_green"]
        },
        {
            "title": "Student Success",
            "description": "Student services data, counselling statistics, and spiritual development programs supporting holistic education.",
            "icon": "🌟",
            "link": "/student-services",
            "color": USC_COLORS["accent_yellow"]
        },
        {
            "title": "Interactive Factbook",
            "description": "Dynamic visualizations and comprehensive reports providing three-year trends across all university metrics.",
            "icon": "📊",
            "link": "/factbook",
            "color": USC_COLORS["primary_green"]
        }
    ]

    cards = []
    for feature in features:
        card = dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.Div([
                        html.Div(feature["icon"],
                                 style={"fontSize": "3rem"},
                                 className="text-center mb-3"),
                        html.H5(feature["title"],
                                className="card-title text-center mb-3",
                                style={"fontWeight": "600", "color": USC_COLORS["primary_green"]}),
                        html.P(feature["description"],
                               className="card-text text-center mb-4",
                               style={"color": USC_COLORS["text_gray"]}),
                        html.Div([
                            dbc.Button("Explore →",
                                       href=feature["link"],
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
    """Create mission and vision section"""
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.H4("Our Mission", className="text-white mb-0")
                    ]),
                    dbc.CardBody([
                        html.P([
                            "The Department of Institutional Research takes great pride in supporting ",
                            html.Strong("data-driven decision making"),
                            " at the University of the Southern Caribbean. We provide comprehensive reports, ",
                            "trend analysis, and strategic insights to facilitate excellence in education ",
                            "and administration."
                        ], className="mb-3"),
                        html.P([
                            "Our work supports USC's mission of transforming ordinary people into ",
                            "extraordinary servants of God through transparent reporting and ",
                            "evidence-based planning."
                        ], className="mb-0")
                    ])
                ])
            ], md=6, className="mb-4"),
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.H4("Strategic Priorities", className="text-white mb-0")
                    ]),
                    dbc.CardBody([
                        html.Ul([
                            html.Li("Spiritual Ethos - Supporting our Christian mission"),
                            html.Li("Academic Success - Enhancing educational outcomes"),
                            html.Li("Faculty Development - Supporting our educators"),
                            html.Li("Financial Sustainability - Responsible stewardship"),
                            html.Li("Operational Efficiency - Continuous improvement")
                        ], className="mb-3"),
                        html.P([
                            html.Strong("SP100 Strategic Plan:"),
                            " Guiding USC toward our centennial in 2027"
                        ], className="mb-0", style={"fontSize": "0.9rem", "fontStyle": "italic"})
                    ])
                ])
            ], md=6, className="mb-4")
        ])
    ], className="py-5")


def create_latest_updates():
    """Create latest updates section"""
    updates = [
        {
            "title": "2024 USC Factbook Released",
            "date": "November 2024",
            "description": "The comprehensive 2024 factbook featuring three-year trends across all university metrics is now available."
        },
        {
            "title": "Enrollment Reaches 3,110 Students",
            "date": "May 2025",
            "description": "Spring semester enrollment data shows continued growth in student population across all academic programs."
        },
        {
            "title": "Financial Transparency Report",
            "date": "October 2024",
            "description": "Annual financial review demonstrates strong fiscal management and sustainable growth strategies."
        }
    ]

    update_cards = []
    for update in updates:
        card = dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H6(update["title"],
                            className="card-title",
                            style={"color": USC_COLORS["primary_green"], "fontWeight": "600"}),
                    html.P(update["date"],
                           className="text-muted mb-2",
                           style={"fontSize": "0.9rem"}),
                    html.P(update["description"],
                           className="card-text",
                           style={"fontSize": "0.95rem"})
                ])
            ], className="h-100", style={"border": f"1px solid {USC_COLORS['light_gray']}"})
        ], md=4, className="mb-3")
        update_cards.append(card)

    return dbc.Container([
        html.H2("Latest Updates",
                className="text-center mb-4",
                style={"color": USC_COLORS["primary_green"], "fontWeight": "700"}),
        dbc.Row(update_cards)
    ], className="py-5", style={"backgroundColor": USC_COLORS["light_gray"]})


def create_contact_section():
    """Create contact section"""
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.H4("Department of Institutional Research", className="text-white mb-0")
                    ]),
                    dbc.CardBody([
                        dbc.Row([
                            dbc.Col([
                                html.Div([
                                    html.Img(src="/assets/director-ir.jpg",
                                             className="rounded-circle mb-3",
                                             style={"width": "120px", "height": "120px", "objectFit": "cover"}),
                                    html.H6("Nordian C. Swaby Robinson",
                                            style={"fontWeight": "600", "color": USC_COLORS["primary_green"]}),
                                    html.P("Director, Institutional Research",
                                           className="text-muted mb-0",
                                           style={"fontSize": "0.9rem"})
                                ], className="text-center")
                            ], md=4),
                            dbc.Col([
                                html.Div([
                                    html.P([
                                        html.Strong("Phone: "), "(868) 645-3265 Ext. 2245"
                                    ], className="mb-2"),
                                    html.P([
                                        html.Strong("Email: "),
                                        html.A("nrobinson@usc.edu.tt",
                                               href="mailto:nrobinson@usc.edu.tt",
                                               style={"color": USC_COLORS["primary_green"]})
                                    ], className="mb-2"),
                                    html.P([
                                        html.Strong("Office: "), "Administration Building, Room 201"
                                    ], className="mb-2"),
                                    html.P([
                                        html.Strong("Hours: "), "Monday - Friday, 8:00 AM - 4:30 PM"
                                    ], className="mb-0")
                                ])
                            ], md=8)
                        ])
                    ])
                ])
            ])
        ])
    ], className="py-5")


# Main layout for the home page
layout = html.Div([
    create_hero_section(),
    create_quick_stats(),
    create_feature_cards(),
    create_mission_section(),
    create_latest_updates(),
    create_contact_section()
])