import dash_bootstrap_components as dbc
from dash import html

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

def create_change_password_page(user):
    """Create change password page for logged-in users"""
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.H3([
                            html.I(className="fas fa-lock me-2"),
                            "Change Password"
                        ], className="text-white mb-0")
                    ], style={'backgroundColor': USC_COLORS['primary_green']}),
                    
                    dbc.CardBody([
                        # User Info
                        html.Div([
                            html.P([
                                "Change password for: ",
                                html.Strong(f"{user['full_name']} ({user['username']})")
                            ], className="mb-4", style={"fontSize": "1.1rem"})
                        ]),

                        # Password change alert (for feedback)
                        html.Div(id="change-pwd-alert", className="mb-3"),

                        # Security Notice
                        dbc.Alert([
                            html.I(className="fas fa-shield-alt me-2"),
                            html.Strong("Security Requirements:"),
                            html.Ul([
                                html.Li("Password must be at least 8 characters long"),
                                html.Li("Include a mix of uppercase and lowercase letters"),
                                html.Li("Include at least one number"),
                                html.Li("Consider using special characters for extra security"),
                                html.Li("Avoid using personal information or common words")
                            ], className="mb-0 mt-2")
                        ], color="info", className="mb-4"),

                        # Change Password Form
                        dbc.Form([
                            dbc.Row([
                                dbc.Col([
                                    dbc.Label("Current Password *", className="fw-bold"),
                                    dbc.Input(
                                        id="current-password", 
                                        type="password",
                                        placeholder="Enter your current password"
                                    ),
                                    dbc.FormText("Enter the password you currently use to login", color="muted")
                                ])
                            ], className="mb-3"),

                            dbc.Row([
                                dbc.Col([
                                    dbc.Label("New Password *", className="fw-bold"),
                                    dbc.Input(
                                        id="new-password", 
                                        type="password",
                                        placeholder="Enter your new password (minimum 8 characters)"
                                    ),
                                    dbc.FormText("Choose a strong password following the security requirements above", color="muted")
                                ])
                            ], className="mb-3"),

                            dbc.Row([
                                dbc.Col([
                                    dbc.Label("Confirm New Password *", className="fw-bold"),
                                    dbc.Input(
                                        id="confirm-new-password", 
                                        type="password",
                                        placeholder="Re-enter your new password"
                                    ),
                                    dbc.FormText("Must match the new password entered above", color="muted")
                                ])
                            ], className="mb-4"),

                            # Submit Button
                            dbc.Row([
                                dbc.Col([
                                    dbc.Button([
                                        html.I(className="fas fa-save me-2"),
                                        "Change Password"
                                    ], 
                                        id="change-pwd-submit", 
                                        color="primary", 
                                        size="lg",
                                        className="w-100", 
                                        n_clicks=0, 
                                        style={"borderRadius": "8px", "fontWeight": "600"}
                                    )
                                ])
                            ], className="mb-3"),

                            # Cancel Button
                            dbc.Row([
                                dbc.Col([
                                    dbc.Button([
                                        html.I(className="fas fa-arrow-left me-2"),
                                        "Back to Profile"
                                    ], 
                                        href="/profile",
                                        color="secondary", 
                                        size="sm",
                                        className="w-100", 
                                        outline=True,
                                        style={"borderRadius": "8px"}
                                    )
                                ])
                            ])
                        ])
                    ])
                ], className="shadow-lg")
            ], md=6, className="mx-auto")
        ]),

        # Help Section
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H5([
                            html.I(className="fas fa-question-circle me-2"),
                            "Need Help?"
                        ], className="mb-3", style={"color": USC_COLORS["primary_green"]}),
                        
                        html.P("If you're having trouble changing your password or have forgotten your current password, please contact our support team:"),
                        
                        dbc.Row([
                            dbc.Col([
                                html.Div([
                                    html.H6("Technical Support"),
                                    html.P([
                                        html.I(className="fas fa-user me-2"),
                                        html.Strong("Liam Webster"),
                                        html.Br(),
                                        "Web Developer, IR",
                                        html.Br(),
                                        html.I(className="fas fa-envelope me-2"),
                                        html.A("websterl@usc.edu.tt", href="mailto:websterl@usc.edu.tt"),
                                        html.Br(),
                                        html.I(className="fas fa-phone me-2"),
                                        "(868) 662-2241 Ext. 1003"
                                    ], className="mb-0")
                                ])
                            ], md=6),
                            dbc.Col([
                                html.Div([
                                    html.H6("Administrative Support"),
                                    html.P([
                                        html.I(className="fas fa-user me-2"),
                                        html.Strong("Nordian C. Swaby Robinson"),
                                        html.Br(),
                                        "Director, IR",
                                        html.Br(),
                                        html.I(className="fas fa-envelope me-2"),
                                        html.A("ir@usc.edu.tt", href="mailto:ir@usc.edu.tt"),
                                        html.Br(),
                                        html.I(className="fas fa-phone me-2"),
                                        "(868) 662-2241 Ext. 1004"
                                    ], className="mb-0")
                                ])
                            ], md=6)
                        ])
                    ])
                ], className="shadow-sm mt-4")
            ], md=6, className="mx-auto")
        ])
    ], className="py-5")