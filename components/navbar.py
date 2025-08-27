import dash_bootstrap_components as dbc
from dash import html, dcc
import requests

# USC Brand Colors
USC_COLORS = {
    'primary_green': '#2E8B57',
    'secondary_green': '#228B22',
    'accent_yellow': '#FFD700',
    'light_gray': '#F8F9FA',
    'dark_gray': '#495057'
}


def create_navbar(user=None):
    """Create navigation bar with proper logout handling"""

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
            ], href="http://localhost:5000/auth/logout", external_link=True)  # Link to Flask logout
        ],
            nav=True,
            in_navbar=True,
            label=[
                html.I(className="fas fa-user-circle me-2"),
                user.get('full_name', user.get('email', 'User'))[:15]
            ])

        nav_items = [
            dbc.NavItem(dbc.NavLink("Dashboard", href="/dashboard")),
            dbc.NavItem(dbc.NavLink("Factbook", href="/factbook")),
            dbc.NavItem(dbc.NavLink("Data Management", href="/data-management")),
        ]

        if user.get('role') == 'admin':
            nav_items.append(dbc.NavItem(dbc.NavLink("Admin", href="/admin")))

        nav_items.append(user_dropdown)

    else:
        # Public navbar
        nav_items = [
            dbc.NavItem(dbc.NavLink("About USC", href="/about-usc")),
            dbc.NavItem(dbc.NavLink("Vision & Mission", href="/vision-mission-motto")),
            dbc.NavItem(dbc.NavLink("Governance", href="/governance")),
            dbc.NavItem(dbc.NavLink("Request Access", href="/request")),
            dbc.NavItem(dbc.NavLink([
                html.I(className="fas fa-sign-in-alt me-2"),
                "Sign In"
            ], href="http://localhost:5000/login", external_link=True, className="btn btn-outline-light ms-2"))
        ]

    return dbc.Navbar([
        dbc.Container([
            dbc.Row([
                dbc.Col([
                    dbc.NavbarBrand([
                        "USC Institutional Research"
                    ], href="/")
                ], width="auto"),
                dbc.Col([
                    dbc.Nav(nav_items, navbar=True, className="ms-auto")
                ], width=True)
            ], align="center", className="w-100")
        ], fluid=True)
    ],
        color=USC_COLORS['primary_green'],
        dark=True,
        className="mb-4")




def create_brand_element():
    """Create the navbar brand element"""
    return html.Div([
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
                "color": "white",
                "opacity": "0.9"
            })
        ])
    ], className="d-flex align-items-center")


def create_auth_button(is_authenticated: bool):
    """Create login/logout button based on authentication status (legacy function)"""
    if is_authenticated:
        return dbc.NavItem([
            dbc.Button([
                html.I(className="fas fa-sign-out-alt me-2"),
                "Logout"
            ],
                id="logout-btn",
                color="outline-light",
                size="sm",
                className="ms-2")
        ])
    else:
        return dbc.NavItem([
            dbc.Button([
                html.I(className="fas fa-sign-in-alt me-2"),
                "Login"
            ],
                href="/login",
                color="warning",
                size="sm",
                className="ms-2")
        ])