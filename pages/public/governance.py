import dash
from dash import html, dcc
import dash_bootstrap_components as dbc

# USC Brand Colors
USC_COLORS = {
    "primary_green": "#1B5E20",
    "secondary_green": "#4CAF50",
    "gold": "#FFD700",
    "light_green": "#E8F5E8",
    "dark_green": "#0D2C0F",
    "white": "#FFFFFF"
}


def create_governance_layout():
    """Create the Governance & Administration page layout"""

    return html.Div([
        # Hero Section
        dbc.Container([
            dbc.Row([
                dbc.Col([
                    html.Div([
                        html.H1([
                            "Governance & Administration",
                        ], className="display-4 text-center mb-4",
                            style={"color": USC_COLORS["white"], "fontWeight": "bold",
                                   "textShadow": "2px 2px 4px rgba(0,0,0,0.5)"}),

                        html.P([
                            "Transparent leadership and strategic governance guiding USC toward excellence"
                        ], className="lead text-center mb-0",
                            style={"fontSize": "1.3rem", "color": USC_COLORS["gold"]})
                    ], className="py-5")
                ])
            ])
        ], fluid=True, className="mb-0",
            style={
                "background": f"linear-gradient(135deg, {USC_COLORS['primary_green']} 0%, {USC_COLORS['dark_green']} 100%)",
                "minHeight": "300px", "display": "flex", "alignItems": "center"}),

        # Main Content
        dbc.Container([
            # Overview Section
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            html.H3([
                                html.I(className="fas fa-sitemap me-3"),
                                "Governance Structure Overview"
                            ], className="text-white mb-0")
                        ], style={"backgroundColor": USC_COLORS["primary_green"]}),
                        dbc.CardBody([
                            html.P([
                                "The University of the Southern Caribbean operates under a comprehensive ",
                                "governance structure that ensures effective leadership, accountability, ",
                                "and strategic decision-making across all levels of the institution."
                            ], className="mb-4", style={"fontSize": "1.1rem"}),

                            dbc.Row([
                                dbc.Col([
                                    dbc.Card([
                                        dbc.CardBody([
                                            html.I(className="fas fa-users fa-3x mb-3",
                                                   style={"color": USC_COLORS["primary_green"]}),
                                            html.H5("Board of Trustees", className="mb-2"),
                                            html.P("34-member supreme decision-making entity, quinquennially elected",
                                                   className="small")
                                        ], className="text-center")
                                    ], className="h-100 shadow-sm")
                                ], md=6, lg=3, className="mb-3"),

                                dbc.Col([
                                    dbc.Card([
                                        dbc.CardBody([
                                            html.I(className="fas fa-user-tie fa-3x mb-3",
                                                   style={"color": USC_COLORS["secondary_green"]}),
                                            html.H5("President's Cabinet", className="mb-2"),
                                            html.P("Executive oversight of operational activities",
                                                   className="small")
                                        ], className="text-center")
                                    ], className="h-100 shadow-sm")
                                ], md=6, lg=3, className="mb-3"),

                                dbc.Col([
                                    dbc.Card([
                                        dbc.CardBody([
                                            html.I(className="fas fa-users-cog fa-3x mb-3",
                                                   style={"color": USC_COLORS["gold"]}),
                                            html.H5("Administrative Council", className="mb-2"),
                                            html.P("Internal governance with broad cross-section representation",
                                                   className="small")
                                        ], className="text-center")
                                    ], className="h-100 shadow-sm")
                                ], md=6, lg=3, className="mb-3"),

                                dbc.Col([
                                    dbc.Card([
                                        dbc.CardBody([
                                            html.I(className="fas fa-chart-org fa-3x mb-3",
                                                   style={"color": USC_COLORS["primary_green"]}),
                                            html.H5("Organizational Structure", className="mb-2"),
                                            html.P("Clear reporting lines and divisional responsibilities",
                                                   className="small")
                                        ], className="text-center")
                                    ], className="h-100 shadow-sm")
                                ], md=6, lg=3, className="mb-3")
                            ])
                        ])
                    ], className="mb-4")
                ], width=12)
            ]),

            # Board of Trustees Section
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            html.H3([
                                html.I(className="fas fa-gavel me-3"),
                                "Board of Trustees"
                            ], className="text-white mb-0")
                        ], style={"backgroundColor": USC_COLORS["primary_green"]}),
                        dbc.CardBody([
                            html.P([
                                "The Board of Trustees is the supreme decision-making entity for the university. ",
                                "The board is quinquennially elected and comprises thirty-four persons including ",
                                "key leadership from the Caribbean Union Conference of the Seventh-day Adventist Church."
                            ], className="mb-4", style={"fontSize": "1.1rem"}),

                            dbc.Row([
                                dbc.Col([
                                    html.H5("Board Composition", className="mb-3",
                                            style={"color": USC_COLORS["primary_green"]}),
                                    html.Ul([
                                        html.Li("President, Secretary, Treasurer, and Education Director of CARU"),
                                        html.Li("President of USC"),
                                        html.Li("Presidents of Conference and Mission fields of CARU"),
                                        html.Li("Two Education Directors (rotational basis)"),
                                        html.Li("Representation from Adventist church laity in CARU"),
                                        html.Li("University alumni representation")
                                    ], style={"fontSize": "1rem"})
                                ], md=6),
                                dbc.Col([
                                    html.H5("Leadership Structure", className="mb-3",
                                            style={"color": USC_COLORS["primary_green"]}),
                                    dbc.ListGroup([
                                        dbc.ListGroupItem([
                                            html.Strong("Chairman: "), "President of CARU"
                                        ]),
                                        dbc.ListGroupItem([
                                            html.Strong("Vice-Chairman: "), "Secretary of CARU"
                                        ]),
                                        dbc.ListGroupItem([
                                            html.Strong("Secretary: "), "President of USC"
                                        ])
                                    ])
                                ], md=6)
                            ]),

                            html.Hr(),

                            html.H5("Current Board Period: 2022-2028", className="text-center mt-4",
                                    style={"color": USC_COLORS["secondary_green"]})
                        ])
                    ], className="mb-4")
                ], width=12)
            ]),

            # President's Cabinet Section
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            html.H3([
                                html.I(className="fas fa-users-crown me-3"),
                                "The President's Cabinet"
                            ], className="text-white mb-0")
                        ], style={"backgroundColor": USC_COLORS["secondary_green"]}),
                        dbc.CardBody([
                            html.P([
                                "The university's day-to-day operations are the responsibility of the President, ",
                                "the university's Chief Executive Officer. The President's Cabinet has executive ",
                                "oversight over the operational activities of the university."
                            ], className="mb-4", style={"fontSize": "1.1rem"}),

                            dbc.Row([
                                dbc.Col([
                                    html.H5("Cabinet Members", className="mb-3",
                                            style={"color": USC_COLORS["primary_green"]}),
                                    dbc.ListGroup([
                                        dbc.ListGroupItem("President (Chief Executive Officer)"),
                                        dbc.ListGroupItem("Provost (Second-ranking officer)"),
                                        dbc.ListGroupItem("Associate Provost"),
                                        dbc.ListGroupItem("Vice President for Financial Administration"),
                                        dbc.ListGroupItem(
                                            "Vice President for Administration, Advancement and Planning"),
                                        dbc.ListGroupItem(
                                            "Vice President of Student Services and Enrolment Management"),
                                        dbc.ListGroupItem("Vice President for Spiritual Development"),
                                        dbc.ListGroupItem("Director of Human Resources")
                                    ])
                                ])
                            ])
                        ])
                    ], className="mb-4")
                ], width=12)
            ]),

            # Administrative Council Section
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            html.H3([
                                html.I(className="fas fa-users-gear me-3"),
                                "Administrative Council"
                            ], className="text-white mb-0")
                        ], style={"backgroundColor": USC_COLORS["primary_green"]}),
                        dbc.CardBody([
                            html.P([
                                "The central internal governance structure includes an Administrative Council ",
                                "chaired by the President. Its membership includes a broad cross-section of ",
                                "internal university leaders and interest groups."
                            ], className="mb-4", style={"fontSize": "1.1rem"}),

                            dbc.Row([
                                dbc.Col([
                                    html.H5("Core Membership", className="mb-3",
                                            style={"color": USC_COLORS["primary_green"]}),
                                    html.Ul([
                                        html.Li("All Vice Presidents"),
                                        html.Li("Deans of Academic Schools"),
                                        html.Li("Chief Accountant"),
                                        html.Li("Librarian"),
                                        html.Li("Director of Information Technology"),
                                        html.Li("University Registrar"),
                                        html.Li("Director of Quality Assurance"),
                                        html.Li("Director of Security Health and Safety")
                                    ], style={"fontSize": "0.95rem"})
                                ], md=6),
                                dbc.Col([
                                    html.H5("Additional Members", className="mb-3",
                                            style={"color": USC_COLORS["primary_green"]}),
                                    html.Ul([
                                        html.Li("Four other directors (rotational basis)"),
                                        html.Li("University Legal Officer"),
                                        html.Li("Associated Student Body President"),
                                        html.Li("Faculty Senate President"),
                                        html.Li("Staff Senate President"),
                                        html.Li("One faculty member"),
                                        html.Li("One staff member"),
                                        html.Li("One Extension Campus Site Coordinator")
                                    ], style={"fontSize": "0.95rem"})
                                ], md=6)
                            ]),

                            dbc.Alert([
                                html.I(className="fas fa-info-circle me-2"),
                                "Faculty or staff members with specially needed expertise can be invited to sit on the council."
                            ], color="info", className="mt-3")
                        ])
                    ], className="mb-4")
                ], width=12)
            ])

        ], className="py-4")

    ], style={"minHeight": "100vh", "backgroundColor": "#f8f9fa"})