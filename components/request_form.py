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

def create_request_form():
    """Create access request form"""
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.H3([
                            html.I(className="fas fa-key me-2"), 
                            "Request System Access"
                        ], className="text-white mb-0")
                    ], style={'backgroundColor': USC_COLORS['primary_green']}),
                    
                    dbc.CardBody([
                        # Introduction
                        html.P([
                            "Complete this form to request access to the USC Institutional Research system. ",
                            "Our team will review your request and contact you within 2-3 business days."
                        ], className="mb-4", style={"fontSize": "1.1rem"}),

                        # Important Information Alert
                        dbc.Alert([
                            html.H5([
                                html.I(className="fas fa-info-circle me-2"),
                                "Before You Apply"
                            ], className="alert-heading mb-3"),
                            html.P("Please note the following:", className="mb-2"),
                            html.Ul([
                                html.Li("USC employees (@usc.edu.tt) typically receive faster approval"),
                                html.Li("External researchers may require additional verification"),
                                html.Li("Students should have faculty sponsor information ready"),
                                html.Li("All users must agree to data usage policies")
                            ], className="mb-3"),
                            html.P([
                                "Alternatively, you can ",
                                html.A("register for a full account", href="/register", 
                                       style={"color": USC_COLORS["primary_green"], "fontWeight": "bold"}),
                                " which provides additional features after admin approval."
                            ], className="mb-0")
                        ], color="info"),

                        # Request Form Alert (for feedback)
                        html.Div(id="request-alert", className="mb-3"),

                        # Access Request Form
                        dbc.Form([
                            # Personal Information Section
                            html.H5("Personal Information", 
                                    style={"color": USC_COLORS["primary_green"], "borderBottom": f"2px solid {USC_COLORS['primary_green']}"}, 
                                    className="mb-3 pb-2"),

                            dbc.Row([
                                dbc.Col([
                                    dbc.Label("Full Name *", className="fw-bold"),
                                    dbc.Input(
                                        id="request-name", 
                                        type="text",
                                        placeholder="Enter your full name"
                                    )
                                ], md=6),
                                dbc.Col([
                                    dbc.Label("Email Address *", className="fw-bold"),
                                    dbc.Input(
                                        id="request-email", 
                                        type="email",
                                        placeholder="your.email@domain.com"
                                    )
                                ], md=6)
                            ], className="mb-3"),

                            dbc.Row([
                                dbc.Col([
                                    dbc.Label("Phone Number", className="fw-bold"),
                                    dbc.Input(
                                        id="request-phone", 
                                        type="tel",
                                        placeholder="(868) 123-4567"
                                    )
                                ], md=6),
                                dbc.Col([
                                    dbc.Label("Affiliation *", className="fw-bold"),
                                    dbc.Select(
                                        id="request-affiliation",
                                        options=[
                                            {"label": "Select your affiliation...", "value": "", "disabled": True},
                                            {"label": "USC Faculty", "value": "USC Faculty"},
                                            {"label": "USC Staff", "value": "USC Staff"},
                                            {"label": "USC Student (Graduate)", "value": "USC Student (Graduate)"},
                                            {"label": "USC Student (Undergraduate)", "value": "USC Student (Undergraduate)"},
                                            {"label": "USC Alumni", "value": "USC Alumni"},
                                            {"label": "External Researcher", "value": "External Researcher"},
                                            {"label": "Government Official", "value": "Government Official"},
                                            {"label": "Media/Journalist", "value": "Media/Journalist"},
                                            {"label": "Other Educational Institution", "value": "Other Educational Institution"},
                                            {"label": "Other", "value": "Other"}
                                        ],
                                        value=""
                                    )
                                ], md=6)
                            ], className="mb-3"),

                            # USC Connection (if applicable)
                            html.Div([
                                dbc.Row([
                                    dbc.Col([
                                        dbc.Label("Department/School (if USC affiliated)", className="fw-bold"),
                                        dbc.Input(
                                            id="request-department", 
                                            type="text",
                                            placeholder="e.g., School of Business, Human Resources"
                                        )
                                    ], md=6),
                                    dbc.Col([
                                        dbc.Label("Position/Title", className="fw-bold"),
                                        dbc.Input(
                                            id="request-position", 
                                            type="text",
                                            placeholder="e.g., Professor, Analyst, Student"
                                        )
                                    ], md=6)
                                ], className="mb-3")
                            ], id="usc-fields"),

                            # Access Requirements Section
                            html.H5("Access Requirements", 
                                    style={"color": USC_COLORS["primary_green"], "borderBottom": f"2px solid {USC_COLORS['primary_green']}"}, 
                                    className="mb-3 pb-2 mt-4"),

                            dbc.Row([
                                dbc.Col([
                                    dbc.Label("Type of Data Needed *", className="fw-bold"),
                                    dbc.Checklist(
                                        id="request-data-types",
                                        options=[
                                            {"label": "Enrollment Statistics", "value": "enrollment"},
                                            {"label": "Academic Performance Data", "value": "academic"},
                                            {"label": "Financial Information", "value": "financial"},
                                            {"label": "Alumni Data", "value": "alumni"},
                                            {"label": "Research & Publications", "value": "research"},
                                            {"label": "Governance Information", "value": "governance"},
                                            {"label": "General Statistics", "value": "general"},
                                            {"label": "Other (specify below)", "value": "other"}
                                        ],
                                        value=[],
                                        inline=False
                                    )
                                ])
                            ], className="mb-3"),

                            dbc.Row([
                                dbc.Col([
                                    dbc.Label("Purpose of Access *", className="fw-bold"),
                                    dbc.Select(
                                        id="request-purpose",
                                        options=[
                                            {"label": "Select purpose...", "value": "", "disabled": True},
                                            {"label": "Academic Research", "value": "Academic Research"},
                                            {"label": "Institutional Planning", "value": "Institutional Planning"},
                                            {"label": "Media/Publication", "value": "Media/Publication"},
                                            {"label": "Government Reporting", "value": "Government Reporting"},
                                            {"label": "Student Project", "value": "Student Project"},
                                            {"label": "Thesis/Dissertation", "value": "Thesis/Dissertation"},
                                            {"label": "Benchmarking Study", "value": "Benchmarking Study"},
                                            {"label": "Grant Application", "value": "Grant Application"},
                                            {"label": "Other", "value": "Other"}
                                        ],
                                        value=""
                                    )
                                ], md=6),
                                dbc.Col([
                                    dbc.Label("Duration of Access Needed", className="fw-bold"),
                                    dbc.Select(
                                        id="request-duration",
                                        options=[
                                            {"label": "Select duration...", "value": "", "disabled": True},
                                            {"label": "One-time access", "value": "One-time"},
                                            {"label": "1 month", "value": "1 month"},
                                            {"label": "3 months", "value": "3 months"},
                                            {"label": "6 months", "value": "6 months"},
                                            {"label": "1 year", "value": "1 year"},
                                            {"label": "Ongoing", "value": "Ongoing"}
                                        ],
                                        value=""
                                    )
                                ], md=6)
                            ], className="mb-3"),

                            # Detailed Request Section
                            html.H5("Detailed Request", 
                                    style={"color": USC_COLORS["primary_green"], "borderBottom": f"2px solid {USC_COLORS['primary_green']}"}, 
                                    className="mb-3 pb-2 mt-4"),

                            dbc.Row([
                                dbc.Col([
                                    dbc.Label("Detailed Description *", className="fw-bold"),
                                    dbc.Textarea(
                                        id="request-description",
                                        placeholder="Please provide a detailed description of:\n• What specific data you need\n• How you plan to use the data\n• Any relevant deadlines\n• Your research methodology (if applicable)",
                                        style={"minHeight": "120px"}
                                    ),
                                    dbc.FormText("Be as specific as possible to help us process your request faster", color="muted")
                                ])
                            ], className="mb-3"),

                            # Faculty Sponsor (for students)
                            html.Div([
                                dbc.Row([
                                    dbc.Col([
                                        dbc.Label("Faculty Sponsor Information (Required for Students)", className="fw-bold"),
                                        dbc.Input(
                                            id="request-sponsor", 
                                            type="text",
                                            placeholder="Faculty name, department, and email"
                                        ),
                                        dbc.FormText("Students must provide faculty supervisor contact information", color="muted")
                                    ])
                                ], className="mb-3")
                            ], id="sponsor-field", style={"display": "none"}),

                            # Additional Information
                            dbc.Row([
                                dbc.Col([
                                    dbc.Label("Additional Comments", className="fw-bold"),
                                    dbc.Textarea(
                                        id="request-comments",
                                        placeholder="Any additional information that might be relevant to your request...",
                                        style={"minHeight": "80px"}
                                    )
                                ])
                            ], className="mb-4"),

                            # Agreement Section
                            html.H5("Data Usage Agreement", 
                                    style={"color": USC_COLORS["primary_green"], "borderBottom": f"2px solid {USC_COLORS['primary_green']}"}, 
                                    className="mb-3 pb-2 mt-4"),

                            dbc.Row([
                                dbc.Col([
                                    dbc.Checklist(
                                        id="request-agreements",
                                        options=[
                                            {
                                                "label": "I agree to use the data responsibly and in accordance with privacy regulations", 
                                                "value": "privacy_agreement"
                                            },
                                            {
                                                "label": "I will not share or redistribute the data without explicit permission", 
                                                "value": "sharing_agreement"
                                            },
                                            {
                                                "label": "I will acknowledge USC as the data source in any publications or presentations", 
                                                "value": "attribution_agreement"
                                            },
                                            {
                                                "label": "I understand that access may be revoked if terms are not followed", 
                                                "value": "terms_agreement"
                                            }
                                        ],
                                        value=[],
                                        inline=False
                                    )
                                ])
                            ], className="mb-4"),

                            # Submit Button
                            dbc.Row([
                                dbc.Col([
                                    dbc.Button([
                                        html.I(className="fas fa-paper-plane me-2"),
                                        "Submit Request"
                                    ], 
                                        id="request-submit", 
                                        color="success", 
                                        size="lg",
                                        className="w-100", 
                                        n_clicks=0, 
                                        style={"borderRadius": "8px", "fontWeight": "600"}
                                    )
                                ])
                            ], className="mb-4"),

                            # Alternative Options
                            html.Hr(),
                            html.Div([
                                html.H6("Alternative Options:", className="mb-3", 
                                        style={"color": USC_COLORS["primary_green"]}),
                                html.P([
                                    html.I(className="fas fa-user-plus me-2"),
                                    html.A("Create a full user account", href="/register", 
                                           style={"color": USC_COLORS["primary_green"]}) + 
                                    " for additional features and easier future access"
                                ], className="mb-2"),
                                html.P([
                                    html.I(className="fas fa-envelope me-2"),
                                    "Email us directly at ",
                                    html.A("ir@usc.edu.tt", href="mailto:ir@usc.edu.tt",
                                           style={"color": USC_COLORS["primary_green"]})
                                ], className="mb-0")
                            ])
                        ])
                    ])
                ], className="shadow-lg")
            ], lg=8, className="mx-auto")
        ]),

        # Contact Information Section
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H5("Contact Information", className="mb-3",
                                style={"color": USC_COLORS["primary_green"]}),
                        html.P("For immediate assistance or questions about data access, please contact our team:"),
                        
                        dbc.Row([
                            dbc.Col([
                                html.Div([
                                    html.H6([
                                        html.I(className="fas fa-user me-2"),
                                        "Nordian C. Swaby Robinson"
                                    ]),
                                    html.P("Director, Institutional Research", className="text-muted mb-1"),
                                    html.P([
                                        html.I(className="fas fa-envelope me-2"),
                                        html.A("ir@usc.edu.tt", href="mailto:ir@usc.edu.tt")
                                    ], className="mb-1"),
                                    html.P([
                                        html.I(className="fas fa-phone me-2"),
                                        "(868) 662-2241 Ext. 1004"
                                    ], className="mb-0")
                                ])
                            ], md=6),
                            dbc.Col([
                                html.Div([
                                    html.H6([
                                        html.I(className="fas fa-user me-2"),
                                        "Liam Webster"
                                    ]),
                                    html.P("Web Developer, Institutional Research", className="text-muted mb-1"),
                                    html.P([
                                        html.I(className="fas fa-envelope me-2"),
                                        html.A("websterl@usc.edu.tt", href="mailto:websterl@usc.edu.tt")
                                    ], className="mb-1"),
                                    html.P([
                                        html.I(className="fas fa-phone me-2"),
                                        "(868) 662-2241 Ext. 1003"
                                    ], className="mb-0")
                                ])
                            ], md=6)
                        ])
                    ])
                ], className="shadow-sm mt-4")
            ], lg=8, className="mx-auto")
        ])
    ], className="py-5")