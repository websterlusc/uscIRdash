import dash_bootstrap_components as dbc
from dash import html
from config import USC_COLORS


def create_homepage(is_authenticated: bool = False, is_admin: bool = False):
    """Create homepage that changes based on authentication status"""

    if is_authenticated:
        return create_authenticated_homepage(is_admin)
    else:
        return create_public_homepage()


def create_public_homepage():
    """Homepage for non-authenticated users"""
    return html.Div([
        create_hero_section(),
        create_quick_stats(),
        create_feature_cards(),
        create_mission_section(),
        create_contact_section(),
        create_footer()
    ])


def create_authenticated_homepage(is_admin: bool = False):
    """Homepage for authenticated users"""
    return html.Div([
        create_welcome_section(is_admin),
        create_dashboard_overview(),
        create_quick_access_section(is_admin),
        create_recent_activity_section(),
        create_footer()
    ])


def create_hero_section():
    """Hero section for public homepage"""
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
                                html.I(className="fas fa-sign-in-alt me-2"),
                                "Login to Access Data"
                            ],
                                href="?login",
                                color="warning",
                                size="lg",
                                className="me-3 mb-3",
                                style={"borderRadius": "0", "fontWeight": "600", "padding": "12px 30px"}),
                            dbc.Button([
                                html.I(className="fas fa-envelope me-2"),
                                "Request Access"
                            ],
                                href="?request",
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


def create_welcome_section(is_admin: bool = False):
    """Welcome section for authenticated users"""
    role_badge = "Administrator" if is_admin else "User"
    badge_color = "danger" if is_admin else "success"

    return dbc.Container([
        dbc.Row([
            dbc.Col([
                dbc.Alert([
                    html.Div([
                        html.H4([
                            html.I(className="fas fa-user-check me-2"),
                            "Welcome to USC Institutional Research Portal"
                        ], className="mb-2"),
                        html.P([
                            "You are logged in as: ",
                            dbc.Badge(role_badge, color=badge_color, className="ms-2")
                        ], className="mb-0")
                    ])
                ], color="info", className="border-0 shadow-sm")
            ])
        ])
    ], className="py-4")


def create_dashboard_overview():
    """Dashboard overview for authenticated users"""
    return dbc.Container([
        html.H2("Quick Overview", className="mb-4"),
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4([
                            html.I(className="fas fa-users me-2", style={"color": USC_COLORS["primary_green"]}),
                            "3,110"
                        ], className="text-center"),
                        html.P("Current Enrollment", className="text-center text-muted mb-0")
                    ])
                ], className="text-center h-100")
            ], md=3),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4([
                            html.I(className="fas fa-graduation-cap me-2",
                                   style={"color": USC_COLORS["primary_green"]}),
                            "875"
                        ], className="text-center"),
                        html.P("2024 Graduates", className="text-center text-muted mb-0")
                    ])
                ], className="text-center h-100")
            ], md=3),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4([
                            html.I(className="fas fa-globe me-2", style={"color": USC_COLORS["primary_green"]}),
                            "40+"
                        ], className="text-center"),
                        html.P("Countries Represented", className="text-center text-muted mb-0")
                    ])
                ], className="text-center h-100")
            ], md=3),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4([
                            html.I(className="fas fa-award me-2", style={"color": USC_COLORS["primary_green"]}),
                            "97+"
                        ], className="text-center"),
                        html.P("Years of Excellence", className="text-center text-muted mb-0")
                    ])
                ], className="text-center h-100")
            ], md=3)
        ])
    ], className="py-4")


def create_quick_access_section(is_admin: bool = False):
    """Quick access section for authenticated users"""
    access_cards = [
        {
            "title": "Interactive Factbook",
            "description": "Access comprehensive university data with interactive visualizations",
            "icon": "fas fa-chart-bar",
            "href": "#factbook",
            "color": "primary"
        },
        {
            "title": "Alumni Portal",
            "description": "Connect with USC graduates and access alumni database",
            "icon": "fas fa-network-wired",
            "href": "#alumni",
            "color": "success"
        },
        {
            "title": "Data Reports",
            "description": "Generate and download custom reports and analytics",
            "icon": "fas fa-file-alt",
            "href": "#reports",
            "color": "info"
        }
    ]

    if is_admin:
        access_cards.append({
            "title": "Admin Dashboard",
            "description": "Manage users, system settings, and access requests",
            "icon": "fas fa-shield-alt",
            "href": "?admin",
            "color": "danger"
        })

    return dbc.Container([
        html.H2("Quick Access", className="mb-4"),
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.I(className=f"{card['icon']} fa-3x mb-3",
                               style={"color": USC_COLORS["primary_green"]}),
                        html.H5(card["title"], className="mb-3"),
                        html.P(card["description"], className="text-muted mb-3"),
                        dbc.Button("Access", href=card["href"], color=card["color"],
                                   className="w-100", style={"borderRadius": "0"})
                    ], className="text-center")
                ], className="h-100 shadow-sm")
            ], md=6 if is_admin else 4, className="mb-4")
            for card in access_cards
        ])
    ], className="py-4")


def create_recent_activity_section():
    """Recent activity section"""
    return dbc.Container([
        html.H2("Recent Activity", className="mb-4"),
        dbc.Card([
            dbc.CardBody([
                html.P("Recent system activities and updates will appear here.",
                       className="text-muted text-center py-4")
            ])
        ])
    ], className="py-4")


def create_quick_stats():
    """Quick statistics for public homepage"""
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
            ], className="h-100")
        ], md=3, sm=6, className="mb-4")
        cards.append(card)

    return dbc.Container([
        html.H2("USC at a Glance", className="text-center mb-5",
                style={"color": USC_COLORS["primary_green"], "fontWeight": "700"}),
        dbc.Row(cards)
    ], className="py-5")


def create_feature_cards():
    """Feature cards for public homepage"""
    features = [
        {
            "title": "Academic Excellence",
            "description": "Comprehensive data on enrollment trends, graduation rates, and academic program performance.",
            "icon": "fas fa-graduation-cap",
            "info": "Login required for full access"
        },
        {
            "title": "Financial Transparency",
            "description": "Detailed financial reports, funding sources, and budget analysis for responsible stewardship.",
            "icon": "fas fa-chart-line",
            "info": "Contact IR for detailed reports"
        },
        {
            "title": "Alumni Network",
            "description": "Connect with USC graduates worldwide and explore career opportunities.",
            "icon": "fas fa-users-cog",
            "info": "Alumni portal for registered users"
        },
        {
            "title": "Interactive Factbook",
            "description": "Dynamic visualizations and comprehensive reports with three-year trends.",
            "icon": "fas fa-book-open",
            "info": "Full system access required"
        }
    ]

    cards = []
    for feature in features:
        card = dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.I(className=f"{feature['icon']} fa-3x mb-3",
                           style={"color": USC_COLORS["primary_green"]}),
                    html.H5(feature["title"], className="mb-3",
                            style={"fontWeight": "600", "color": USC_COLORS["primary_green"]}),
                    html.P(feature["description"], className="mb-3",
                           style={"color": USC_COLORS["text_gray"]}),
                    html.P(feature["info"], className="text-muted mb-4",
                           style={"fontSize": "0.85rem", "fontStyle": "italic"}),
                    dbc.Button("Request Access", href="?request", color="primary",
                               className="w-100", style={"borderRadius": "0"})
                ], className="text-center")
            ], className="h-100 shadow-sm")
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
                        f"University of the Southern Caribbean. ",
                        "All rights reserved. | ",
                        html.A("Privacy Policy", href="#", className="text-white-50"),
                        " | ",
                        html.A("Terms of Use", href="#", className="text-white-50")
                    ], className="text-center text-white-50 mb-0")
                ])
            ])
        ], fluid=True)
    ], className="footer")