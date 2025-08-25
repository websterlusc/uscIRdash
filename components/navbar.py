import dash_bootstrap_components as dbc
from dash import html, dcc

# USC Brand Colors
USC_COLORS = {
    'primary_green': '#2E8B57',
    'secondary_green': '#228B22',
    'accent_yellow': '#FFD700',
    'light_gray': '#F8F9FA',
    'dark_gray': '#495057'
}

def create_navbar(user=None):
    """Create the main navigation bar with proper login/logout links"""
    nav_items = [
        dbc.NavItem(dbc.NavLink("Home", href="/", active="exact")),
        dbc.DropdownMenu([
            dbc.DropdownMenuItem(
                dcc.Link("Facts About USC", href="/about-usc", style={"textDecoration": "none", "color": "inherit"})),
            dbc.DropdownMenuItem(dcc.Link("Vision, Mission & Motto", href="/vision-mission-motto",
                                          style={"textDecoration": "none", "color": "inherit"})),
            dbc.DropdownMenuItem(
                dcc.Link("Governance", href="/governance", style={"textDecoration": "none", "color": "inherit"})),
        ], nav=True, in_navbar=True, label="About USC", id="about-dropdown"),
    ]

    if user:
        # Add Dashboard for all authenticated users
        nav_items.append(
            dbc.NavItem(dbc.NavLink("Dashboard", href="/dashboard"))
        )

        # Add Factbook access for admins only
        if user.get('role') == 'admin':
            nav_items.extend([
                dbc.NavItem(dbc.NavLink([
                    html.I(className="fas fa-book me-2"),
                    "Factbook"
                ], href="/factbook", style={"color": USC_COLORS["accent_yellow"]})),
                dbc.NavItem(dbc.NavLink("Admin", href="/admin", className="text-warning"))
            ])

        # User menu with profile options
        nav_items.append(
            dbc.DropdownMenu(
                children=[
                    dbc.DropdownMenuItem(f"Signed in as: {user['full_name']}", disabled=True),
                    dbc.DropdownMenuItem(divider=True),
                    dbc.DropdownMenuItem("Profile", href="/profile"),
                    dbc.DropdownMenuItem("Change Password", href="/change-password"),
                    dbc.DropdownMenuItem(divider=True),
                    dbc.DropdownMenuItem([
                        html.I(className="fas fa-sign-out-alt me-2"),
                        "Logout"
                    ], id="logout-btn"),
                ],
                nav=True,
                in_navbar=True,
                label=[
                    html.I(className="fas fa-user me-1"),
                    user['username']
                ],
            )
        )
    else:
        # For non-authenticated users - proper login button
        nav_items.extend([
            dbc.NavItem(dbc.NavLink("Request Access", href="/request")),
            dbc.NavItem([
                dbc.Button([
                    html.I(className="fas fa-sign-in-alt me-2"),
                    "Login"
                ],
                    href="/login",  # This now works properly with the fixed routing
                    color="warning",
                    size="sm",
                    className="ms-2",
                    external_link=False)  # Important: keeps it within the Dash app
            ])
        ])

    return dbc.NavbarSimple(
        children=nav_items,
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