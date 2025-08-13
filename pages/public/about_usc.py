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


def create_about_usc_layout():
    """Create the About USC page layout"""

    return html.Div([
        # Hero Section
        dbc.Container([
            dbc.Row([
                dbc.Col([
                    html.Div([
                        html.H1([
                            "Facts About the University of the Southern Caribbean",
                        ], className="display-4 text-center mb-4",
                            style={"color": USC_COLORS["primary_green"], "fontWeight": "bold"}),

                        html.P([
                            "Transforming ordinary people into extraordinary servants of God to humanity ",
                            "through a holistic tertiary educational experience since 1927."
                        ], className="lead text-center mb-5",
                            style={"fontSize": "1.3rem", "color": USC_COLORS["dark_green"]})
                    ], className="py-5")
                ])
            ])
        ], fluid=True, className="mb-5", style={
            "background": f"linear-gradient(135deg, {USC_COLORS['light_green']} 0%, {USC_COLORS['white']} 100%)"}),

        # Main Content
        dbc.Container([
            # History and Foundation Section
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            html.H3([
                                html.I(className="fas fa-university me-3"),
                                "Our Heritage"
                            ], className="text-white mb-0")
                        ], style={"backgroundColor": USC_COLORS["primary_green"]}),
                        dbc.CardBody([
                            html.P([
                                "Founded in 1927, the University of the Southern Caribbean is a private, ",
                                "co-educational, tertiary-level university with its main campus located in ",
                                "the beautiful Maracas Valley of Trinidad and Tobago."
                            ], className="mb-3", style={"fontSize": "1.1rem"}),

                            html.P([
                                "Our 384-acre campus, nestled ten miles northeast of Port-of-Spain, is covered ",
                                "with beautiful tropical vegetation and borders the Maracas River. This ",
                                "invigorating environment provides a warm and healthy atmosphere conducive to study."
                            ], className="mb-3", style={"fontSize": "1.1rem"}),

                            html.P([
                                "As Trinidad and Tobago's first private, faith-based accredited university, ",
                                "USC received full institutional accreditation by the Accreditation Council ",
                                "of Trinidad and Tobago (ACTT) in May 2012."
                            ], className="mb-0", style={"fontSize": "1.1rem"})
                        ])
                    ], className="shadow-sm mb-4")
                ], width=12)
            ]),

            # Diversity and Community Section
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            html.H3([
                                html.I(className="fas fa-globe-americas me-3"),
                                "Our Diverse Community"
                            ], className="text-white mb-0")
                        ], style={"backgroundColor": USC_COLORS["secondary_green"]}),
                        dbc.CardBody([
                            dbc.Row([
                                dbc.Col([
                                    html.Div([
                                        html.H4("~40", className="display-6 text-center mb-2",
                                                style={"color": USC_COLORS["primary_green"], "fontWeight": "bold"}),
                                        html.P("Countries Represented", className="text-center mb-0",
                                               style={"fontWeight": "500"})
                                    ], className="text-center p-3 border rounded",
                                        style={"backgroundColor": USC_COLORS["light_green"]})
                                ], md=4),
                                dbc.Col([
                                    html.Div([
                                        html.H4("50+", className="display-6 text-center mb-2",
                                                style={"color": USC_COLORS["primary_green"], "fontWeight": "bold"}),
                                        html.P("Denominational Affiliations", className="text-center mb-0",
                                               style={"fontWeight": "500"})
                                    ], className="text-center p-3 border rounded",
                                        style={"backgroundColor": USC_COLORS["light_green"]})
                                ], md=4),
                                dbc.Col([
                                    html.Div([
                                        html.H4("1927", className="display-6 text-center mb-2",
                                                style={"color": USC_COLORS["primary_green"], "fontWeight": "bold"}),
                                        html.P("Year Founded", className="text-center mb-0",
                                               style={"fontWeight": "500"})
                                    ], className="text-center p-3 border rounded",
                                        style={"backgroundColor": USC_COLORS["light_green"]})
                                ], md=4)
                            ], className="mb-3"),

                            html.P([
                                "USC's diverse community of faculty, staff, and students creates a rich ",
                                "multicultural learning environment that prepares graduates for global service."
                            ], className="text-center mt-3", style={"fontSize": "1.1rem"})
                        ])
                    ], className="shadow-sm mb-4")
                ], width=12)
            ]),

            # Regional Presence Section
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            html.H3([
                                html.I(className="fas fa-map-marked-alt me-3"),
                                "Regional Presence"
                            ], className="text-white mb-0")
                        ], style={"backgroundColor": USC_COLORS["primary_green"]}),
                        dbc.CardBody([
                            html.P([
                                "USC extends its educational mission beyond Trinidad and Tobago through ",
                                "strategic partnerships and satellite locations throughout the Caribbean."
                            ], className="mb-4", style={"fontSize": "1.1rem"}),

                            dbc.Row([
                                dbc.Col([
                                    html.H5("Main Campus", className="mb-3",
                                            style={"color": USC_COLORS["primary_green"]}),
                                    html.Ul([
                                        html.Li("Trinidad (Maracas Valley)"),
                                        html.Li("South Campus"),
                                        html.Li("Tobago Campus")
                                    ], style={"fontSize": "1rem"})
                                ], md=6),
                                dbc.Col([
                                    html.H5("Satellite Sites", className="mb-3",
                                            style={"color": USC_COLORS["primary_green"]}),
                                    html.Ul([
                                        html.Li("Antigua"),
                                        html.Li("Barbados"),
                                        html.Li("St. Lucia"),
                                        html.Li("Guyana")
                                    ], style={"fontSize": "1rem"})
                                ], md=6)
                            ])
                        ])
                    ], className="shadow-sm mb-4")
                ], width=12)
            ]),

            # Governance Section
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            html.H3([
                                html.I(className="fas fa-users-cog me-3"),
                                "Governance Structure"
                            ], className="text-white mb-0")
                        ], style={"backgroundColor": USC_COLORS["secondary_green"]}),
                        dbc.CardBody([
                            html.P([
                                "USC operates under the guidance of the Caribbean Union Conference of ",
                                "the Seventh-day Adventist Church, which comprises ten conferences and missions ",
                                "across the Caribbean region."
                            ], className="mb-3", style={"fontSize": "1.1rem"}),

                            html.H5("CARU Member Organizations:", className="mb-3",
                                    style={"color": USC_COLORS["primary_green"]}),

                            dbc.Row([
                                dbc.Col([
                                    html.Ul([
                                        html.Li("North Caribbean Conference"),
                                        html.Li("East Caribbean Conference"),
                                        html.Li("Grenada Conference"),
                                        html.Li("South Leeward Conference"),
                                        html.Li("South Caribbean Conference")
                                    ], style={"fontSize": "1rem"})
                                ], md=6),
                                dbc.Col([
                                    html.Ul([
                                        html.Li("Tobago Conference"),
                                        html.Li("St. Lucia Mission"),
                                        html.Li("St Vincent Mission"),
                                        html.Li("Guyana Conference"),
                                        html.Li("Suriname Mission")
                                    ], style={"fontSize": "1rem"})
                                ], md=6)
                            ])
                        ])
                    ], className="shadow-sm mb-4")
                ], width=12)
            ]),

            # Call to Action Section
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4("Learn More About USC", className="text-center mb-4",
                                    style={"color": USC_COLORS["primary_green"]}),

                            dbc.Row([
                                dbc.Col([
                                    dbc.Button([
                                        html.I(className="fas fa-eye me-2"),
                                        "Vision, Mission & Motto"
                                    ], color="primary", size="lg", className="w-100",
                                        href="/vision-mission-motto",
                                        style={"backgroundColor": USC_COLORS["primary_green"],
                                               "borderColor": USC_COLORS["primary_green"]})
                                ], md=4),
                                dbc.Col([
                                    dbc.Button([
                                        html.I(className="fas fa-sitemap me-2"),
                                        "Governance Structure"
                                    ], color="outline-primary", size="lg", className="w-100",
                                        href="/governance",
                                        style={"borderColor": USC_COLORS["primary_green"],
                                               "color": USC_COLORS["primary_green"]})
                                ], md=4),
                                dbc.Col([
                                    dbc.Button([
                                        html.I(className="fas fa-external-link-alt me-2"),
                                        "Official USC Website"
                                    ], color="outline-secondary", size="lg", className="w-100",
                                        href="https://www.usc.edu.tt", target="_blank")
                                ], md=4)
                            ])
                        ])
                    ], className="shadow-sm",
                        style={"backgroundColor": USC_COLORS["light_green"]})
                ], width=12)
            ])

        ], className="py-5")

    ], style={"minHeight": "100vh", "backgroundColor": "#f8f9fa"})