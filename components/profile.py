import dash_bootstrap_components as dbc
from dash import html, dcc

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

def create_profile_page(user):
    """Create user profile page"""
    return dbc.Container([
        # Page Header
        dbc.Row([
            dbc.Col([
                html.H2([
                    html.I(className="fas fa-user-circle me-3"),
                    "My Profile"
                ], style={"color": USC_COLORS["primary_green"]}),
                html.P("Manage your account information and preferences", className="text-muted mb-4")
            ])
        ]),

        dbc.Row([
            # Left Column - Profile Card
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.H5([
                            html.I(className="fas fa-id-card me-2"),
                            "Account Information"
                        ], className="mb-0")
                    ]),
                    dbc.CardBody([
                        html.Div([
                            # Profile Picture Section
                            html.Div([
                                html.Div([
                                    html.I(className="fas fa-user fa-4x",
                                           style={"color": USC_COLORS["primary_green"]})
                                ], className="text-center mb-3",
                                    style={"width": "100px", "height": "100px", 
                                           "borderRadius": "50%", "backgroundColor": USC_COLORS["light_gray"],
                                           "display": "flex", "alignItems": "center", 
                                           "justifyContent": "center", "margin": "0 auto"}),
                                
                                html.H5(user['full_name'], className="text-center mb-1",
                                        style={"color": USC_COLORS["primary_green"], "fontWeight": "600"}),
                                html.P(user['email'], className="text-center text-muted mb-2"),
                                
                                html.Div([
                                    dbc.Badge(
                                        user['role'].title(),
                                        color="danger" if user['role'] == "admin" else "primary",
                                        className="mb-3"
                                    )
                                ], className="text-center")
                            ], className="mb-4"),

                            # Account Details
                            html.Hr(),
                            
                            dbc.Row([
                                dbc.Col([
                                    html.Strong("Username:")
                                ], width=4),
                                dbc.Col([
                                    html.P(user['username'], className="mb-2")
                                ])
                            ]),

                            dbc.Row([
                                dbc.Col([
                                    html.Strong("Email:")
                                ], width=4),
                                dbc.Col([
                                    html.P(user['email'], className="mb-2")
                                ])
                            ]),

                            dbc.Row([
                                dbc.Col([
                                    html.Strong("Full Name:")
                                ], width=4),
                                dbc.Col([
                                    html.P(user['full_name'], className="mb-2")
                                ])
                            ]),

                            dbc.Row([
                                dbc.Col([
                                    html.Strong("Department:")
                                ], width=4),
                                dbc.Col([
                                    html.P(user.get('department', 'Not specified'), className="mb-2")
                                ])
                            ]),

                            dbc.Row([
                                dbc.Col([
                                    html.Strong("Position:")
                                ], width=4),
                                dbc.Col([
                                    html.P(user.get('position', 'Not specified'), className="mb-2")
                                ])
                            ]),

                            dbc.Row([
                                dbc.Col([
                                    html.Strong("Account Type:")
                                ], width=4),
                                dbc.Col([
                                    dbc.Badge(
                                        user['role'].upper(),
                                        color="danger" if user['role'] == "admin" else "primary"
                                    )
                                ])
                            ]),

                            # Action Buttons
                            html.Hr(),
                            html.Div([
                                dbc.Button([
                                    html.I(className="fas fa-key me-2"),
                                    "Change Password"
                                ], href="/change-password", color="primary", className="me-2 mb-2"),
                                dbc.Button([
                                    html.I(className="fas fa-edit me-2"),
                                    "Edit Profile"
                                ], color="secondary", disabled=True, className="mb-2"),
                                html.Br(),
                                html.Small("Profile editing will be available soon", className="text-muted")
                            ], className="text-center")
                        ])
                    ])
                ], className="shadow-sm")
            ], md=6),

            # Right Column - Access & Preferences
            dbc.Col([
                # Access Permissions Card
                dbc.Card([
                    dbc.CardHeader([
                        html.H5([
                            html.I(className="fas fa-shield-alt me-2"),
                            "Access Permissions"
                        ], className="mb-0")
                    ]),
                    dbc.CardBody([
                        html.H6("Your Access Level:", className="mb-3"),
                        
                        dbc.ListGroup([
                            dbc.ListGroupItem([
                                html.Div([
                                    html.I(className="fas fa-home me-2"),
                                    "Home Dashboard"
                                ], className="d-flex align-items-center"),
                                html.I(className="fas fa-check text-success", style={"fontSize": "1.2rem"})
                            ], className="d-flex justify-content-between align-items-center"),

                            dbc.ListGroupItem([
                                html.Div([
                                    html.I(className="fas fa-book me-2"),
                                    "Interactive Factbook"
                                ], className="d-flex align-items-center"),
                                html.I(
                                    className="fas fa-check text-success" if user['role'] == 'admin' 
                                    else "fas fa-times text-danger",
                                    style={"fontSize": "1.2rem"}
                                )
                            ], className="d-flex justify-content-between align-items-center"),

                            dbc.ListGroupItem([
                                html.Div([
                                    html.I(className="fas fa-chart-bar me-2"),
                                    "Financial Data"
                                ], className="d-flex align-items-center"),
                                html.I(
                                    className="fas fa-check text-success" if user['role'] == 'admin' 
                                    else "fas fa-times text-danger",
                                    style={"fontSize": "1.2rem"}
                                )
                            ], className="d-flex justify-content-between align-items-center"),

                            dbc.ListGroupItem([
                                html.Div([
                                    html.I(className="fas fa-users-cog me-2"),
                                    "User Management"
                                ], className="d-flex align-items-center"),
                                html.I(
                                    className="fas fa-check text-success" if user['role'] == 'admin' 
                                    else "fas fa-times text-danger",
                                    style={"fontSize": "1.2rem"}
                                )
                            ], className="d-flex justify-content-between align-items-center"),

                            dbc.ListGroupItem([
                                html.Div([
                                    html.I(className="fas fa-download me-2"),
                                    "Data Export"
                                ], className="d-flex align-items-center"),
                                dbc.Badge("Coming Soon", color="secondary")
                            ], className="d-flex justify-content-between align-items-center")
                        ], flush=True, className="mb-3"),

                        html.Hr(),
                        html.P([
                            html.I(className="fas fa-info-circle me-2"),
                            "Need additional access? Contact the IR team at ",
                            html.A("ir@usc.edu.tt", href="mailto:ir@usc.edu.tt")
                        ], className="text-muted small mb-0")
                    ])
                ], className="shadow-sm mb-4"),

                # Activity Summary Card
                dbc.Card([
                    dbc.CardHeader([
                        html.H5([
                            html.I(className="fas fa-history me-2"),
                            "Recent Activity"
                        ], className="mb-0")
                    ]),
                    dbc.CardBody([
                        html.P("Activity tracking will be available soon.", className="text-muted text-center mb-3"),
                        
                        # Placeholder activity items
                        html.Div([
                            html.Div([
                                html.I(className="fas fa-sign-in-alt me-2"),
                                "Logged in today"
                            ], className="mb-2 text-muted small"),
                            html.Div([
                                html.I(className="fas fa-eye me-2"),
                                "Viewed dashboard"
                            ], className="mb-2 text-muted small"),
                            html.Div([
                                html.I(className="fas fa-user me-2"),
                                "Updated profile"
                            ], className="text-muted small")
                        ])
                    ])
                ], className="shadow-sm")
            ], md=6)
        ]),

        # Support Section
        dbc.Row([
            dbc.Col([
                dbc.Alert([
                    html.H5([
                        html.I(className="fas fa-question-circle me-2"),
                        "Need Help?"
                    ], className="alert-heading"),
                    html.P("If you need assistance with your account or have questions about accessing data, please contact our team:"),
                    html.Ul([
                        html.Li([
                            html.Strong("Nordian C. Swaby Robinson"), " - Director, IR - ",
                            html.A("ir@usc.edu.tt", href="mailto:ir@usc.edu.tt")
                        ]),
                        html.Li([
                            html.Strong("Liam Webster"), " - Web Developer - ",
                            html.A("websterl@usc.edu.tt", href="mailto:websterl@usc.edu.tt")
                        ])
                    ], className="mb-0")
                ], color="info")
            ])
        ], className="mt-4")

    ], className="py-4")