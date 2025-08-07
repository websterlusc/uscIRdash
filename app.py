import dash
from dash import dcc, html, Input, Output, callback
import dash_bootstrap_components as dbc
from datetime import datetime

# Initialize the Dash app with Bootstrap theme
app = dash.Dash(__name__,
                external_stylesheets=[dbc.themes.BOOTSTRAP],
                use_pages=True,
                suppress_callback_exceptions=True,
                meta_tags=[
                    {"name": "viewport", "content": "width=device-width, initial-scale=1"}
                ])

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

# Inject custom CSS styles
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
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

        .btn-secondary {
            background-color: #FDD835 !important;
            border-color: #FDD835 !important;
            color: #1B5E20 !important;
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
            padding: 4rem 0;
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

        .display-4 {
            font-weight: 700 !important;
        }

        .lead {
            color: #666666 !important;
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
                    dbc.DropdownMenuItem("About USC", href="/about"),
                    dbc.DropdownMenuItem("Vision & Mission", href="/vision-mission"),
                    dbc.DropdownMenuItem("Governance", href="/governance"),
                    dbc.DropdownMenuItem("Leadership", href="/leadership"),
                ],
                nav=True,
                in_navbar=True,
                label="About Us",
            ),
            dbc.DropdownMenu(
                children=[
                    dbc.DropdownMenuItem("Student Enrollment", href="/enrollment"),
                    dbc.DropdownMenuItem("Graduation Data", href="/graduation"),
                    dbc.DropdownMenuItem("Academic Programs", href="/programs"),
                    dbc.DropdownMenuItem("Faculty Statistics", href="/faculty"),
                ],
                nav=True,
                in_navbar=True,
                label="Academic Data",
            ),
            dbc.DropdownMenu(
                children=[
                    dbc.DropdownMenuItem("Financial Overview", href="/financial"),
                    dbc.DropdownMenuItem("Subsidies & Funding", href="/funding"),
                    dbc.DropdownMenuItem("Income Sources", href="/income"),
                    dbc.DropdownMenuItem("Scholarships", href="/scholarships"),
                ],
                nav=True,
                in_navbar=True,
                label="Financial Data",
            ),
            dbc.DropdownMenu(
                children=[
                    dbc.DropdownMenuItem("Student Services", href="/student-services"),
                    dbc.DropdownMenuItem("Counselling", href="/counselling"),
                    dbc.DropdownMenuItem("Spiritual Development", href="/spiritual"),
                    dbc.DropdownMenuItem("Campus Life", href="/campus-life"),
                ],
                nav=True,
                in_navbar=True,
                label="Student Life",
            ),
            dbc.NavItem(dbc.NavLink("Factbook", href="/factbook")),
            dbc.NavItem(dbc.NavLink("Reports", href="/reports")),
            dbc.NavItem(dbc.NavLink("Contact", href="/contact")),
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
                        "Phone: (868) 645-3265",
                        html.Br(),
                        "Email: info@usc.edu.tt"
                    ], className="text-white-50")
                ], md=4),
                dbc.Col([
                    html.H6("Quick Links", className="text-white mb-3"),
                    html.Ul([
                        html.Li(dcc.Link("USC Website", href="https://www.usc.edu.tt", className="text-white-50")),
                        html.Li(dcc.Link("Student Portal", href="#", className="text-white-50")),
                        html.Li(dcc.Link("Faculty Resources", href="#", className="text-white-50")),
                        html.Li(dcc.Link("Alumni", href="#", className="text-white-50")),
                    ], className="list-unstyled")
                ], md=4),
                dbc.Col([
                    html.H6("Institutional Research", className="text-white mb-3"),
                    html.P("Nordian C. Swaby Robinson", className="text-white-50 mb-1"),
                    html.P("Director, Institutional Research", className="text-white-50 mb-3"),
                    html.P([
                        "Phone: (868) 645-3265 Ext. 2245",
                        html.Br(),
                        "Email: nrobinson@usc.edu.tt"
                    ], className="text-white-50")
                ], md=4)
            ]),
            html.Hr(className="my-4", style={"borderColor": "rgba(255,255,255,0.2)"}),
            dbc.Row([
                dbc.Col([
                    html.P([
                        f"© {datetime.now().year} University of the Southern Caribbean. ",
                        "All rights reserved. | ",
                        dcc.Link("Privacy Policy", href="#", className="text-white-50"),
                        " | ",
                        dcc.Link("Terms of Use", href="#", className="text-white-50")
                    ], className="text-center text-white-50 mb-0")
                ])
            ])
        ], fluid=True)
    ], className="footer")

# Main app layout
app.layout = html.Div([
    create_navbar(),
    html.Div(
        dash.page_container,
        className="page-content"
    ),
    create_footer()
])

# Import and register pages after app is created
from pages import home
home.register_page()

if __name__ == "__main__":
    app.run_server(debug=True, host='127.0.0.1', port=8050)