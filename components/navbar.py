import dash_bootstrap_components as dbc
from dash import html
from config import USC_COLORS


def create_navbar(is_authenticated: bool = False, is_admin: bool = False):
    """Create dynamic navbar based on authentication status"""

    # Base navigation items (always visible)
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
        dbc.NavItem(dbc.NavLink("Contact", href="#contact")),
    ]

    # Add authenticated user items
    if is_authenticated:
        nav_items.extend([
            dbc.DropdownMenu(
                children=[
                    dbc.DropdownMenuItem("Interactive Factbook", href="#factbook"),
                    dbc.DropdownMenuItem("Alumni Portal", href="#alumni"),
                    dbc.DropdownMenuItem("Data Reports", href="#reports"),
                ],
                nav=True,
                in_navbar=True,
                label="Data Systems",
            ),
            dbc.DropdownMenu(
                children=[
                    dbc.DropdownMenuItem("Academic Data", href="#academic"),
                    dbc.DropdownMenuItem("Financial Reports", href="#financial"),
                    dbc.DropdownMenuItem("Student Services", href="#student"),
                ],
                nav=True,
                in_navbar=True,
                label="Analytics",
            ),
        ])

        # Add admin-only items
        if is_admin:
            nav_items.append(
                dbc.NavItem(dbc.NavLink([
                    html.I(className="fas fa-shield-alt me-1"),
                    "Admin"
                ], href="?admin", className="text-warning"))
            )

    # Authentication button
    auth_button = create_auth_button(is_authenticated)

    return dbc.NavbarSimple(
        children=nav_items + [auth_button],
        brand=create_brand_element(),
        brand_href="/",
        color=USC_COLORS['primary_green'],
        dark=True,
        fluid=True,
        className="mb-0 shadow-sm"
    )


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
    """Create login/logout button based on authentication status"""
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
                href="?login",
                color="warning",
                size="sm",
                className="ms-2")
        ])


def create_authenticated_navbar_items():
    """Items only visible to authenticated users"""
    return [
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
    ]


def create_admin_navbar_items():
    """Items only visible to admin users"""
    return [
        dbc.NavItem(dbc.NavLink([
            html.I(className="fas fa-users-cog me-1"),
            "User Management"
        ], href="?admin&tab=users", className="text-info")),
        dbc.NavItem(dbc.NavLink([
            html.I(className="fas fa-database me-1"),
            "Data Management"
        ], href="?admin&tab=data", className="text-info")),
    ]