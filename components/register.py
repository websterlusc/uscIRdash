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

def create_register_page():
    """Create registration page"""
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.H3([
                            html.I(className="fas fa-user-plus me-2"),
                            "Create New Account"
                        ], className="text-white mb-0")
                    ], style={'backgroundColor': USC_COLORS['primary_green']}),
                    
                    dbc.CardBody([
                        # Information Alert
                        dbc.Alert([
                            html.I(className="fas fa-info-circle me-2"),
                            "Note: New accounts require admin approval before you can login. USC employees (@usc.edu.tt) are typically approved faster."
                        ], color="info", className="mb-4"),

                        # Registration Alert (for feedback)
                        html.Div(id="register-alert", className="mb-3"),

                        # Registration Form
                        dbc.Form([
                            # Personal Information Section
                            html.H5("Personal Information", 
                                    style={"color": USC_COLORS["primary_green"], "borderBottom": f"2px solid {USC_COLORS['primary_green']}"}, 
                                    className="mb-3 pb-2"),

                            dbc.Row([
                                dbc.Col([
                                    dbc.Label("Email Address *", className="fw-bold"),
                                    dbc.Input(
                                        id="register-email", 
                                        type="email",
                                        placeholder="your.email@usc.edu.tt",
                                        invalid=False
                                    ),
                                    dbc.FormText("Use your USC email for faster approval", color="muted")
                                ], md=6),
                                dbc.Col([
                                    dbc.Label("Username *", className="fw-bold"),
                                    dbc.Input(
                                        id="register-username", 
                                        type="text",
                                        placeholder="Choose a unique username",
                                        invalid=False
                                    ),
                                    dbc.FormText("Will be used for login", color="muted")
                                ], md=6)
                            ], className="mb-3"),

                            dbc.Row([
                                dbc.Col([
                                    dbc.Label("Full Name *", className="fw-bold"),
                                    dbc.Input(
                                        id="register-fullname", 
                                        type="text",
                                        placeholder="Enter your full name as it appears on official documents"
                                    )
                                ])
                            ], className="mb-3"),

                            # Professional Information Section
                            html.H5("Professional Information", 
                                    style={"color": USC_COLORS["primary_green"], "borderBottom": f"2px solid {USC_COLORS['primary_green']}"}, 
                                    className="mb-3 pb-2 mt-4"),

                            dbc.Row([
                                dbc.Col([
                                    dbc.Label("Department", className="fw-bold"),
                                    dbc.Select(
                                        id="register-department",
                                        options=[
                                            {"label": "Select Department...", "value": "", "disabled": True},
                                            {"label": "Academic Affairs", "value": "Academic Affairs"},
                                            {"label": "Administration & Planning", "value": "Administration & Planning"},
                                            {"label": "Admissions & Records", "value": "Admissions & Records"},
                                            {"label": "Business & Finance", "value": "Business & Finance"},
                                            {"label": "Campus Services", "value": "Campus Services"},
                                            {"label": "Human Resources", "value": "Human Resources"},
                                            {"label": "Information Technology", "value": "Information Technology"},
                                            {"label": "Institutional Research", "value": "Institutional Research"},
                                            {"label": "Library Services", "value": "Library Services"},
                                            {"label": "Marketing & Communications", "value": "Marketing & Communications"},
                                            {"label": "Student Affairs", "value": "Student Affairs"},
                                            {"label": "School of Business & Entrepreneurship", "value": "School of Business & Entrepreneurship"},
                                            {"label": "School of Education", "value": "School of Education"},
                                            {"label": "School of Humanities", "value": "School of Humanities"},
                                            {"label": "School of Religion", "value": "School of Religion"},
                                            {"label": "School of Science & Technology", "value": "School of Science & Technology"},
                                            {"label": "School of Social Sciences", "value": "School of Social Sciences"},
                                            {"label": "Other", "value": "Other"}
                                        ],
                                        value=""
                                    )
                                ], md=6),
                                dbc.Col([
                                    dbc.Label("Position/Role", className="fw-bold"),
                                    dbc.Input(
                                        id="register-position", 
                                        type="text",
                                        placeholder="e.g., Analyst, Manager, Professor, Student"
                                    )
                                ], md=6)
                            ], className="mb-3"),

                            # Access Request Section
                            html.H5("Access Request", 
                                    style={"color": USC_COLORS["primary_green"], "borderBottom": f"2px solid {USC_COLORS['primary_green']}"}, 
                                    className="mb-3 pb-2 mt-4"),

                            dbc.Row([
                                dbc.Col([
                                    dbc.Label("Reason for Access", className="fw-bold"),
                                    dbc.Textarea(
                                        id="register-justification",
                                        placeholder="Please explain why you need access to the USC Institutional Research system...",
                                        style={"minHeight": "100px"}
                                    ),
                                    dbc.FormText("Provide details about your intended use of the system", color="muted")
                                ])
                            ], className="mb-3"),

                            # Security Section
                            html.H5("Account Security", 
                                    style={"color": USC_COLORS["primary_green"], "borderBottom": f"2px solid {USC_COLORS['primary_green']}"}, 
                                    className="mb-3 pb-2 mt-4"),

                            dbc.Row([
                                dbc.Col([
                                    dbc.Label("Password *", className="fw-bold"),
                                    dbc.Input(
                                        id="register-password", 
                                        type="password",
                                        placeholder="Enter a strong password (minimum 8 characters)"
                                    ),
                                    dbc.FormText("Must be at least 8 characters with a mix of letters, numbers, and symbols", color="muted")
                                ], md=6),
                                dbc.Col([
                                    dbc.Label("Confirm Password *", className="fw-bold"),
                                    dbc.Input(
                                        id="register-confirm", 
                                        type="password",
                                        placeholder="Re-enter your password"
                                    )
                                ], md=6)
                            ], className="mb-4"),

                            # Terms and Conditions
                            dbc.Row([
                                dbc.Col([
                                    dbc.Checklist(
                                        id="register-terms",
                                        options=[
                                            {
                                                "label": html.Span([
                                                    "I agree to the ",
                                                    html.A("Terms of Service", href="#", target="_blank"),
                                                    " and ",
                                                    html.A("Privacy Policy", href="#", target="_blank")
                                                ]), 
                                                "value": "terms_accepted"
                                            }
                                        ],
                                        value=[],
                                        inline=True
                                    )
                                ])
                            ], className="mb-4"),

                            # Submit Button
                            dbc.Row([
                                dbc.Col([
                                    dbc.Button([
                                        html.I(className="fas fa-user-plus me-2"),
                                        "Create Account"
                                    ], 
                                        id="register-submit", 
                                        color="success", 
                                        size="lg",
                                        className="w-100", 
                                        n_clicks=0, 
                                        style={"borderRadius": "8px", "fontWeight": "600"}
                                    )
                                ])
                            ], className="mb-3"),

                            # Login Link
                            html.Hr(),
                            html.Div([
                                html.P([
                                    "Already have an account? ",
                                    html.A("Login here", href="/login", style={"color": USC_COLORS["primary_green"]})
                                ], className="text-center mb-0")
                            ])
                        ])
                    ])
                ], className="shadow-lg")
            ], md=8, className="mx-auto")
        ])
    ], className="py-5")