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


def create_vision_mission_motto_layout():
    """Create the Vision, Mission & Motto page layout"""

    return html.Div([
        # Hero Section with USC Text
        dbc.Container([
            dbc.Row([
                dbc.Col([
                    html.Div([
                        html.H1([
                            "Our Foundation",
                        ], className="display-3 text-center mb-4",
                            style={"color": USC_COLORS["white"], "fontWeight": "bold",
                                   "textShadow": "2px 2px 4px rgba(0,0,0,0.5)"}),

                        html.Blockquote([
                            html.P([
                                '"And Jesus increased in wisdom and stature, and in favour with God and man."'
                            ], className="blockquote text-center mb-2",
                                style={"fontSize": "1.5rem", "color": USC_COLORS["white"], "fontStyle": "italic"}),
                            html.Footer([
                                "Luke 2:52 - University Text"
                            ], className="blockquote-footer text-center",
                                style={"color": USC_COLORS["gold"], "fontSize": "1.2rem"})
                        ], className="mb-0")
                    ], className="py-5")
                ])
            ])
        ], fluid=True, className="mb-0",
            style={
                "background": f"linear-gradient(135deg, {USC_COLORS['primary_green']} 0%, {USC_COLORS['dark_green']} 100%)",
                "minHeight": "400px", "display": "flex", "alignItems": "center"}),

        # Main Content
        dbc.Container([
            # Mission Statement Section
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            html.H2([
                                html.I(className="fas fa-bullseye me-3"),
                                "Mission Statement"
                            ], className="text-white mb-0", style={"fontSize": "2rem"})
                        ], style={"backgroundColor": USC_COLORS["primary_green"], "padding": "1.5rem"}),
                        dbc.CardBody([
                            html.Blockquote([
                                html.P([
                                    "The University of the Southern Caribbean seeks to transform ordinary people ",
                                    "into extraordinary servants of God to humanity through a holistic tertiary ",
                                    "educational experience."
                                ], className="blockquote text-center mb-0",
                                    style={"fontSize": "1.4rem", "fontWeight": "500", "lineHeight": "1.6",
                                           "color": USC_COLORS["primary_green"]})
                            ], className="border-0 p-4",
                                style={"backgroundColor": USC_COLORS["light_green"], "borderRadius": "10px"})
                        ], className="p-4")
                    ], className="shadow-lg mb-5")
                ], width=12)
            ]),

            # Vision Statement Section
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            html.H2([
                                html.I(className="fas fa-eye me-3"),
                                "Vision Statement"
                            ], className="text-white mb-0", style={"fontSize": "2rem"})
                        ], style={"backgroundColor": USC_COLORS["secondary_green"], "padding": "1.5rem"}),
                        dbc.CardBody([
                            html.Blockquote([
                                html.P([
                                    "A Seventh-day Adventist university fully reflecting the character of God ",
                                    "through spiritual, intellectual, physical, social and cultural development."
                                ], className="blockquote text-center mb-0",
                                    style={"fontSize": "1.4rem", "fontWeight": "500", "lineHeight": "1.6",
                                           "color": USC_COLORS["primary_green"]})
                            ], className="border-0 p-4",
                                style={"backgroundColor": USC_COLORS["light_green"], "borderRadius": "10px"})
                        ], className="p-4")
                    ], className="shadow-lg mb-5")
                ], width=12)
            ]),

            # Motto Section
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.Div([
                                html.H2([
                                    html.I(className="fas fa-star me-3"),
                                    "University Motto"
                                ], className="text-center mb-4",
                                    style={"color": USC_COLORS["primary_green"], "fontSize": "2rem"}),

                                html.H1([
                                    "Beyond Excellence"
                                ], className="display-2 text-center mb-0",
                                    style={"color": USC_COLORS["gold"], "fontWeight": "bold",
                                           "textShadow": f"2px 2px 4px {USC_COLORS['primary_green']}"})
                            ], className="p-4")
                        ], style={"backgroundColor": USC_COLORS["primary_green"], "borderRadius": "15px"})
                    ], className="shadow-lg mb-5")
                ], width=12)
            ]),

            # Strategic Priorities Section (SP100)
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            html.H3([
                                html.I(className="fas fa-road me-3"),
                                "SP100: Strategic Priorities Toward Our Centennial"
                            ], className="text-white mb-0")
                        ], style={"backgroundColor": USC_COLORS["dark_green"]}),
                        dbc.CardBody([
                            html.P([
                                "As we approach USC's centennial in 2027, our journey is guided by SP100, ",
                                "a strategic plan rooted in five essential priorities that drive our mission."
                            ], className="mb-4 text-center", style={"fontSize": "1.2rem", "fontWeight": "500"}),

                            dbc.Row([
                                dbc.Col([
                                    dbc.Card([
                                        dbc.CardBody([
                                            html.I(className="fas fa-cross fa-3x mb-3",
                                                   style={"color": USC_COLORS["primary_green"]}),
                                            html.H5("Spiritual Ethos", className="mb-2",
                                                    style={"color": USC_COLORS["primary_green"]}),
                                            html.P(
                                                "Fostering a campus culture that honors Christian service and values",
                                                className="small mb-0")
                                        ], className="text-center")
                                    ], className="h-100 shadow-sm")
                                ], md=6, lg=2.4, className="mb-3"),

                                dbc.Col([
                                    dbc.Card([
                                        dbc.CardBody([
                                            html.I(className="fas fa-graduation-cap fa-3x mb-3",
                                                   style={"color": USC_COLORS["secondary_green"]}),
                                            html.H5("Academic Success", className="mb-2",
                                                    style={"color": USC_COLORS["primary_green"]}),
                                            html.P("Enhancing academic outcomes and empowering student success",
                                                   className="small mb-0")
                                        ], className="text-center")
                                    ], className="h-100 shadow-sm")
                                ], md=6, lg=2.4, className="mb-3"),

                                dbc.Col([
                                    dbc.Card([
                                        dbc.CardBody([
                                            html.I(className="fas fa-users fa-3x mb-3",
                                                   style={"color": USC_COLORS["gold"]}),
                                            html.H5("Faculty & Staff Development", className="mb-2",
                                                    style={"color": USC_COLORS["primary_green"]}),
                                            html.P("Supporting professional growth and development of our team",
                                                   className="small mb-0")
                                        ], className="text-center")
                                    ], className="h-100 shadow-sm")
                                ], md=6, lg=2.4, className="mb-3"),

                                dbc.Col([
                                    dbc.Card([
                                        dbc.CardBody([
                                            html.I(className="fas fa-chart-line fa-3x mb-3",
                                                   style={"color": USC_COLORS["primary_green"]}),
                                            html.H5("Financial Sustainability", className="mb-2",
                                                    style={"color": USC_COLORS["primary_green"]}),
                                            html.P("Ensuring long-term financial resilience and stability",
                                                   className="small mb-0")
                                        ], className="text-center")
                                    ], className="h-100 shadow-sm")
                                ], md=6, lg=2.4, className="mb-3"),

                                dbc.Col([
                                    dbc.Card([
                                        dbc.CardBody([
                                            html.I(className="fas fa-cogs fa-3x mb-3",
                                                   style={"color": USC_COLORS["secondary_green"]}),
                                            html.H5("Operational Efficiency", className="mb-2",
                                                    style={"color": USC_COLORS["primary_green"]}),
                                            html.P("Strengthening efficiency and quality of our operations",
                                                   className="small mb-0")
                                        ], className="text-center")
                                    ], className="h-100 shadow-sm")
                                ], md=6, lg=2.4, className="mb-3")
                            ])
                        ])
                    ], className="shadow-lg mb-5")
                ], width=12)
            ]),

            # Holistic Development Section
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            html.H3([
                                html.I(className="fas fa-heart me-3"),
                                "Our Holistic Approach"
                            ], className="text-white mb-0")
                        ], style={"backgroundColor": USC_COLORS["secondary_green"]}),
                        dbc.CardBody([
                            html.P([
                                "Following our university text from Luke 2:52, USC is committed to developing ",
                                "the whole person through five key dimensions of growth:"
                            ], className="mb-4 text-center", style={"fontSize": "1.1rem"}),

                            dbc.Row([
                                dbc.Col([
                                    html.Div([
                                        html.I(className="fas fa-brain fa-2x mb-3",
                                               style={"color": USC_COLORS["primary_green"]}),
                                        html.H6("Intellectual", style={"color": USC_COLORS["primary_green"]}),
                                        html.P("Wisdom & Learning", className="small mb-0")
                                    ], className="text-center p-3")
                                ], md=6, lg=2.4),

                                dbc.Col([
                                    html.Div([
                                        html.I(className="fas fa-praying-hands fa-2x mb-3",
                                               style={"color": USC_COLORS["primary_green"]}),
                                        html.H6("Spiritual", style={"color": USC_COLORS["primary_green"]}),
                                        html.P("Favour with God", className="small mb-0")
                                    ], className="text-center p-3")
                                ], md=6, lg=2.4),

                                dbc.Col([
                                    html.Div([
                                        html.I(className="fas fa-running fa-2x mb-3",
                                               style={"color": USC_COLORS["primary_green"]}),
                                        html.H6("Physical", style={"color": USC_COLORS["primary_green"]}),
                                        html.P("Health & Stature", className="small mb-0")
                                    ], className="text-center p-3")
                                ], md=6, lg=2.4),

                                dbc.Col([
                                    html.Div([
                                        html.I(className="fas fa-handshake fa-2x mb-3",
                                               style={"color": USC_COLORS["primary_green"]}),
                                        html.H6("Social", style={"color": USC_COLORS["primary_green"]}),
                                        html.P("Favour with People", className="small mb-0")
                                    ], className="text-center p-3")
                                ], md=6, lg=2.4),

                                dbc.Col([
                                    html.Div([
                                        html.I(className="fas fa-globe fa-2x mb-3",
                                               style={"color": USC_COLORS["primary_green"]}),
                                        html.H6("Cultural", style={"color": USC_COLORS["primary_green"]}),
                                        html.P("Global Understanding", className="small mb-0")
                                    ], className="text-center p-3")
                                ], md=6, lg=2.4)
                            ])
                        ])
                    ], className="shadow-lg")
                ], width=12)
            ])

        ], className="py-5")

    ], style={"minHeight": "100vh", "backgroundColor": "#f8f9fa"})