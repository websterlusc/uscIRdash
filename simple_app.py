import dash
from dash import dcc, html, Input, Output, callback
import dash_bootstrap_components as dbc
from datetime import datetime
import os

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


# Get base URL for deployment
def get_base_url():
    """Get the base URL for links (local vs deployed)"""
    if os.environ.get('RENDER'):
        # On Render, use the service URL
        return "https://uscirdash.onrender.com/"  # Replace with your actual Render URL
    else:
        # Local development
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
            dbc.NavItem(dbc.NavLink("Contact", href="#contact")),
        ],
        brand=html.Div([
            html.Img(src="/assets/usc-logo.png", height="40", className="me-2"),
            "Institutional Research"
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
                            className="lead text-white mb-4",
                            style={"fontSize": "1.3rem", "textShadow": "1px 1px 2px rgba(0,0,0,0.3)"}),
                        html.P(
                            "Supporting USC's mission of transforming ordinary people into extraordinary servants of God through evidence-based insights",
                            className="text-white mb-5",
                            style={"fontSize": "1.1rem", "opacity": "0.95",
                                   "textShadow": "1px 1px 2px rgba(0,0,0,0.3)"}),
                        html.Div([
                            dbc.Button([
                                html.I(className="fas fa-envelope me-2"),
                                "Contact for Access"
                            ],
                                href="#contact",
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
                                "Contact IR ",
                                html.I(className="fas fa-envelope ms-1")
                            ],
                                href="#contact",
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
                            className="mb-4",
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
        html.Div(id="contact")  # Anchor for contact section
    ], className="py-5", style={"backgroundColor": USC_COLORS["light_gray"]})


def create_contact_section():
    """Create contact and leadership section"""
    return dbc.Container([
        html.H2("Department Leadership & Contact",
                className="text-center mb-5",
                style={"color": USC_COLORS["primary_green"], "fontWeight": "700"}),
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        dbc.Row([
                            dbc.Col([
                                html.Div([
                                    html.I(className="fas fa-user-tie fa-5x mb-3",
                                           style={"color": USC_COLORS["primary_green"]}),
                                    html.H5("Nordian C. Swaby Robinson",
                                            style={"fontWeight": "600", "color": USC_COLORS["primary_green"]}),
                                    html.P("Director, Institutional Research",
                                           className="text-muted mb-3",
                                           style={"fontSize": "1.1rem"})
                                ], className="text-center")
                            ], md=4),
                            dbc.Col([
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
                            ], md=8)
                        ])
                    ])
                ])
            ])
        ]),
        html.Hr(className="my-5"),
        dbc.Row([
            dbc.Col([
                html.H5("Access Our Systems", className="mb-3", style={"color": USC_COLORS["primary_green"]}),
                html.P(
                    "For access to our comprehensive data systems, please contact the Institutional Research department:",
                    className="mb-3"),
                html.Ul([
                    html.Li("Interactive Factbook with live data visualizations"),
                    html.Li("Alumni Portal and networking database"),
                    html.Li("Financial reporting and analytics"),
                    html.Li("Custom reports and analysis")
                ], className="mb-4"),
                html.Div([
                    dbc.Button([
                        html.I(className="fas fa-envelope me-2"),
                        "Request Access"
                    ],
                        href="mailto:ir@usc.edu.tt?subject=IR Systems Access Request",
                        color="primary",
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
                html.Div([
                    dbc.Alert([
                        html.I(className="fas fa-info-circle me-2"),
                        html.Strong("Note: "),
                        "Interactive Factbook and Alumni Portal are available when running locally with the full system."
                    ], color="info", className="mt-3")
                ])
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
                        html.Li(html.A("Contact IR", href="mailto:ir@usc.edu.tt", className="text-white-50")),
                        html.Li(html.A("Student Portal", href="#", className="text-white-50")),
                        html.Li(html.A("Faculty Resources", href="#", className="text-white-50")),
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


# Main app layout
app.layout = html.Div([
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

if __name__ == "__main__":
    # Use different settings for local vs production
    port = int(os.environ.get('PORT', 8050))
    debug = not os.environ.get('RENDER')

    app.run(debug=debug, host='0.0.0.0', port=port)