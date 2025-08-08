import dash_bootstrap_components as dbc
from dash import html
from config import USC_COLORS


def create_access_request_form():
    """Create the access request form page"""
    return html.Div([
        dbc.Container([
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            html.H3([
                                html.I(className="fas fa-key me-2"),
                                "Request System Access"
                            ], className="text-white mb-0")
                        ]),
                        dbc.CardBody([
                            html.P([
                                "Please complete this form to request access to USC's Institutional Research systems. ",
                                "Our team will review your request and respond within 1-2 business days."
                            ], className="mb-4", style={"fontSize": "1.1rem"}),

                            html.Div(id="request-form-alert", className="mb-4"),

                            create_request_form()
                        ])
                    ])
                ], lg=10, className="mx-auto")
            ])
        ], className="py-5"),
        create_access_info_section()
    ])


def create_request_form():
    """Create the main request form"""
    return dbc.Form([
        # Personal Information Section
        html.H5([
            html.I(className="fas fa-user me-2"),
            "Personal Information"
        ], className="mb-3", style={"color": USC_COLORS["primary_green"]}),

        dbc.Row([
            dbc.Col([
                dbc.Label([
                    html.I(className="fas fa-user me-2"),
                    "Full Name *"
                ], className="fw-bold"),
                dbc.Input(
                    id="req-name",
                    type="text",
                    required=True,
                    placeholder="Enter your full name"
                )
            ], md=6),
            dbc.Col([
                dbc.Label([
                    html.I(className="fas fa-envelope me-2"),
                    "Email Address *"
                ], className="fw-bold"),
                dbc.Input(
                    id="req-email",
                    type="email",
                    required=True,
                    placeholder="your.email@domain.com"
                )
            ], md=6)
        ], className="mb-4"),

        # Professional Information Section
        html.H5([
            html.I(className="fas fa-briefcase me-2"),
            "Professional Information"
        ], className="mb-3", style={"color": USC_COLORS["primary_green"]}),

        dbc.Row([
            dbc.Col([
                dbc.Label([
                    html.I(className="fas fa-building me-2"),
                    "Department/Organization *"
                ], className="fw-bold"),
                dbc.Input(
                    id="req-department",
                    type="text",
                    required=True,
                    placeholder="e.g., Finance, Academic Affairs, External Partner"
                )
            ], md=6),
            dbc.Col([
                dbc.Label([
                    html.I(className="fas fa-id-badge me-2"),
                    "Position/Title *"
                ], className="fw-bold"),
                dbc.Input(
                    id="req-position",
                    type="text",
                    required=True,
                    placeholder="e.g., Manager, Director, Analyst"
                )
            ], md=6)
        ], className="mb-4"),

        dbc.Row([
            dbc.Col([
                dbc.Label([
                    html.I(className="fas fa-university me-2"),
                    "USC Employee Status"
                ], className="fw-bold"),
                dbc.RadioItems(
                    id="req-usc-employee",
                    options=[
                        {"label": " Yes - USC Employee/Faculty/Staff", "value": True},
                        {"label": " No - External Partner/Consultant", "value": False}
                    ],
                    value=True,
                    inline=False,
                    className="mt-2"
                )
            ], md=12)
        ], className="mb-4"),

        # Access Requirements Section
        html.H5([
            html.I(className="fas fa-lock me-2"),
            "Access Requirements"
        ], className="mb-3", style={"color": USC_COLORS["primary_green"]}),

        dbc.Row([
            dbc.Col([
                dbc.Label([
                    html.I(className="fas fa-database me-2"),
                    "Systems Access Needed *"
                ], className="fw-bold"),
                dbc.Checklist(
                    id="req-access-type",
                    options=[
                        {
                            "label": " Interactive Factbook (Comprehensive Data Analytics & Reports)",
                            "value": "factbook"
                        },
                        {
                            "label": " Alumni Portal (Graduate Database & Networking)",
                            "value": "alumni"
                        },
                        {
                            "label": " Financial Data System (Budget & Financial Reports)",
                            "value": "financial"
                        },
                        {
                            "label": " Custom Reports Generator",
                            "value": "reports"
                        }
                    ],
                    value=["factbook"],
                    className="mt-2"
                )
            ], md=8),
            dbc.Col([
                dbc.Label([
                    html.I(className="fas fa-calendar-alt me-2"),
                    "Requested Duration"
                ], className="fw-bold"),
                dbc.Select(
                    id="req-duration",
                    options=[
                        {"label": "1 week (7 days)", "value": 7},
                        {"label": "2 weeks (14 days)", "value": 14},
                        {"label": "1 month (30 days)", "value": 30},
                        {"label": "2 months (60 days)", "value": 60},
                        {"label": "3 months (90 days)", "value": 90},
                        {"label": "6 months (180 days)", "value": 180},
                        {"label": "1 year (365 days)", "value": 365}
                    ],
                    value=30,
                    className="mt-2"
                )
            ], md=4)
        ], className="mb-4"),

        # Justification Section
        html.H5([
            html.I(className="fas fa-clipboard-list me-2"),
            "Justification & Purpose"
        ], className="mb-3", style={"color": USC_COLORS["primary_green"]}),

        dbc.Row([
            dbc.Col([
                dbc.Label([
                    html.I(className="fas fa-pen me-2"),
                    "Please provide detailed justification *"
                ], className="fw-bold"),
                dbc.Textarea(
                    id="req-justification",
                    placeholder="""Please explain in detail:
• Why you need access to these systems
• How you will use the data
• What specific information you're looking for
• Any relevant projects or reports you're working on
• Expected deliverables or outcomes

Example: "I am conducting a research study on enrollment trends in Caribbean universities and need access to USC's historical enrollment data to compare with regional benchmarks. The data will be used in a publication for the Caribbean Educational Research Journal."
                    """,
                    rows=8,
                    required=True,
                    className="mt-2"
                )
            ])
        ], className="mb-4"),

        # Terms and Conditions
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H6([
                            html.I(className="fas fa-shield-alt me-2"),
                            "Data Usage Agreement"
                        ], style={"color": USC_COLORS["primary_green"]}),
                        html.P([
                            "By submitting this request, I agree to:"
                        ], className="mb-2"),
                        html.Ul([
                            html.Li("Use the data only for the stated purpose"),
                            html.Li("Maintain confidentiality of sensitive information"),
                            html.Li("Not share access credentials with others"),
                            html.Li("Acknowledge USC as the data source in any publications"),
                            html.Li("Return or destroy data upon completion of authorized use")
                        ], className="mb-3"),
                        dbc.Checklist(
                            id="req-agreement",
                            options=[
                                {
                                    "label": " I agree to the Data Usage Agreement terms above",
                                    "value": "agreed"
                                }
                            ],
                            className="fw-bold"
                        )
                    ])
                ], color="light")
            ])
        ], className="mb-4"),

        # Review Information
        dbc.Row([
            dbc.Col([
                dbc.Alert([
                    html.I(className="fas fa-info-circle me-2"),
                    html.Strong("Review Process: "),
                    "Your request will be reviewed by the Institutional Research team. ",
                    "USC employees typically receive faster approval. You will receive an email ",
                    "notification once your request is processed. Processing time: 1-3 business days."
                ], color="info", className="mb-4")
            ])
        ]),

        # Submit Button
        dbc.Row([
            dbc.Col([
                dbc.Button([
                    html.I(className="fas fa-paper-plane me-2"),
                    "Submit Access Request"
                ],
                    id="submit-access-request",
                    color="primary",
                    size="lg",
                    className="w-100",
                    style={"borderRadius": "0", "fontWeight": "600", "padding": "15px"})
            ], md=8, className="mx-auto")
        ])
    ])


def create_access_info_section():
    """Create information section about access types"""
    return dbc.Container([
        html.H2("Available Systems", className="text-center mb-5",
                style={"color": USC_COLORS["primary_green"], "fontWeight": "700"}),

        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.H5([
                            html.I(className="fas fa-chart-bar me-2"),
                            "Interactive Factbook"
                        ], className="text-white mb-0")
                    ]),
                    dbc.CardBody([
                        html.P("Comprehensive university data with interactive visualizations:", className="mb-2"),
                        html.Ul([
                            html.Li("Student enrollment and demographics"),
                            html.Li("Graduation rates and outcomes"),
                            html.Li("Faculty and staff statistics"),
                            html.Li("Program performance metrics"),
                            html.Li("Three-year trend analysis"),
                            html.Li("Custom dashboard creation")
                        ], className="mb-3"),
                        dbc.Badge("Most Popular", color="success")
                    ])
                ])
            ], md=6, className="mb-4"),

            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.H5([
                            html.I(className="fas fa-users me-2"),
                            "Alumni Portal"
                        ], className="text-white mb-0")
                    ]),
                    dbc.CardBody([
                        html.P("Connect with USC graduates worldwide:", className="mb-2"),
                        html.Ul([
                            html.Li("Graduate database search"),
                            html.Li("Career outcome tracking"),
                            html.Li("Geographic distribution"),
                            html.Li("Industry analysis"),
                            html.Li("Alumni engagement metrics"),
                            html.Li("Networking opportunities")
                        ], className="mb-3"),
                        dbc.Badge("Professional Network", color="info")
                    ])
                ])
            ], md=6, className="mb-4")
        ]),

        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.H5([
                            html.I(className="fas fa-dollar-sign me-2"),
                            "Financial Data System"
                        ], className="text-white mb-0")
                    ]),
                    dbc.CardBody([
                        html.P("Financial transparency and budget analysis:", className="mb-2"),
                        html.Ul([
                            html.Li("Budget and expenditure reports"),
                            html.Li("Revenue source analysis"),
                            html.Li("Scholarship and aid distribution"),
                            html.Li("Financial trend monitoring"),
                            html.Li("Cost per student metrics"),
                            html.Li("Funding source tracking")
                        ], className="mb-3"),
                        dbc.Badge("Restricted Access", color="warning")
                    ])
                ])
            ], md=6, className="mb-4"),

            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.H5([
                            html.I(className="fas fa-file-alt me-2"),
                            "Custom Reports"
                        ], className="text-white mb-0")
                    ]),
                    dbc.CardBody([
                        html.P("Generate tailored reports and analysis:", className="mb-2"),
                        html.Ul([
                            html.Li("Custom data queries"),
                            html.Li("Comparative analysis tools"),
                            html.Li("Export in multiple formats"),
                            html.Li("Scheduled report generation"),
                            html.Li("Data visualization tools"),
                            html.Li("Statistical analysis features")
                        ], className="mb-3"),
                        dbc.Badge("Advanced Users", color="primary")
                    ])
                ])
            ], md=6, className="mb-4")
        ])
    ], className="py-5", style={"backgroundColor": USC_COLORS["light_gray"]})