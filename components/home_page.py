import dash_bootstrap_components as dbc
from dash import html, dcc
from datetime import datetime

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
    """Create enhanced hero section with USC ecosystem links"""
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

                        # Action buttons
                        html.Div([
                            dbc.Button([
                                html.I(className="fas fa-chart-line me-2"),
                                "Explore Analytics"
                            ], size="lg", color="warning", className="me-3 mb-3",
                                href="/dashboard"),
                            dbc.Button([
                                html.I(className="fas fa-book me-2"),
                                "View Factbook"
                            ], size="lg", color="outline-light", className="me-3 mb-3",
                                href="/factbook"),
                            dbc.Button([
                                html.I(className="fas fa-key me-2"),
                                "Request Access"
                            ], size="lg", color="outline-light", className="mb-3",
                                href="/request")
                        ], className="mb-5"),

                        # USC Ecosystem Links
                        html.Div([
                            html.H4("USC Digital Ecosystem",
                                    className="text-white mb-4",
                                    style={"fontWeight": "600"}),

                            dbc.Row([
                                dbc.Col([
                                    dbc.Card([
                                        dbc.CardBody([
                                            html.I(className="fas fa-graduation-cap fa-2x mb-3",
                                                   style={"color": USC_COLORS["primary_green"]}),
                                            html.H6("USC Aeorion", className="card-title mb-2"),
                                            html.P("Student Information System", className="card-text small mb-3"),
                                            dbc.Button([
                                                html.I(className="fas fa-external-link-alt me-2"),
                                                "Access Aeorion"
                                            ], size="sm", color="primary",
                                                href="https://aeorion.usc.edu.tt",
                                                target="_blank", className="w-100")
                                        ], className="text-center")
                                    ], className="h-100 shadow-sm")
                                ], md=4, className="mb-3"),

                                dbc.Col([
                                    dbc.Card([
                                        dbc.CardBody([
                                            html.I(className="fas fa-address-book fa-2x mb-3",
                                                   style={"color": USC_COLORS["secondary_green"]}),
                                            html.H6("USC Directory", className="card-title mb-2"),
                                            html.P("Staff & Faculty Directory", className="card-text small mb-3"),
                                            dbc.Button([
                                                html.I(className="fas fa-external-link-alt me-2"),
                                                "View Directory"
                                            ], size="sm", color="success",
                                                href="https://directory.usc.edu.tt",
                                                target="_blank", className="w-100")
                                        ], className="text-center")
                                    ], className="h-100 shadow-sm")
                                ], md=4, className="mb-3"),

                                dbc.Col([
                                    dbc.Card([
                                        dbc.CardBody([
                                            html.I(className="fas fa-laptop fa-2x mb-3",
                                                   style={"color": USC_COLORS["accent_yellow"]}),
                                            html.H6("USC eLearn", className="card-title mb-2"),
                                            html.P("Learning Management System", className="card-text small mb-3"),
                                            dbc.Button([
                                                html.I(className="fas fa-external-link-alt me-2"),
                                                "Access eLearn"
                                            ], size="sm", color="warning",
                                                href="https://elearn.usc.edu.tt",
                                                target="_blank", className="w-100")
                                        ], className="text-center")
                                    ], className="h-100 shadow-sm")
                                ], md=4, className="mb-3")
                            ])
                        ], className="mt-5")

                    ], className="text-center py-5")
                ], width=12)
            ])
        ])
    ], style={
        "background": f"linear-gradient(135deg, {USC_COLORS['primary_green']} 0%, {USC_COLORS['secondary_green']} 100%)",
        "minHeight": "80vh",
        "display": "flex",
        "alignItems": "center"
    })


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


def create_home_page(user=None):
    """Create home page with original design"""
    if user:
        # Authenticated user home page
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
        # Public home page with all sections
        return html.Div([
            create_hero_section(),
            create_quick_stats(),
            create_feature_cards(),
            create_mission_section(),
            create_contact_section(),
            create_footer()
        ])