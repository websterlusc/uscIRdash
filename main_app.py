import dash
from dash import dcc, html, Input, Output, State, callback, ctx
import dash_bootstrap_components as dbc
from datetime import datetime
import os

# Import helper modules
from auth.auth_manager import AuthManager
from components.navbar import create_navbar
from components.homepage import create_homepage
from components.admin_dashboard import create_admin_dashboard
from components.access_request import create_access_request_form
from utils.database import init_database
from config import USC_COLORS, BASE_URL

# Initialize the Dash app
app = dash.Dash(__name__,
                external_stylesheets=[dbc.themes.BOOTSTRAP],
                meta_tags=[
                    {"name": "viewport", "content": "width=device-width, initial-scale=1"}
                ])

# Expose server for deployment
server = app.server

# Initialize database and auth manager
init_database()
auth_manager = AuthManager()

# Inject custom CSS
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>USC Institutional Research</title>
        {%favicon%}
        {%css%}
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
        <style>
        /* USC Brand Custom Styles */
        .navbar-brand {
            font-weight: bold !important;
            font-size: 1.2rem !important;
        }
        .nav-link {
            font-weight: 500 !important;
            transition: all 0.3s ease !important;
        }
        .nav-link:hover {
            color: #FDD835 !important;
            background-color: rgba(255, 255, 255, 0.1) !important;
        }
        .btn-primary {
            background-color: #1B5E20 !important;
            border-color: #1B5E20 !important;
            border-radius: 0 !important;
            font-weight: 500 !important;
        }
        .btn-primary:hover {
            background-color: #4CAF50 !important;
            border-color: #4CAF50 !important;
        }
        .btn-warning {
            background-color: #FDD835 !important;
            border-color: #FDD835 !important;
            color: #1B5E20 !important;
            border-radius: 0 !important;
            font-weight: 500 !important;
        }
        .card {
            border-radius: 0 !important;
            border: none !important;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1) !important;
        }
        .card-header {
            background-color: #1B5E20 !important;
            color: white !important;
            border-radius: 0 !important;
            font-weight: 600 !important;
        }
        .hero-section {
            background: linear-gradient(135deg, #1B5E20 0%, #4CAF50 100%);
            color: white;
            padding: 5rem 0;
        }
        .footer {
            background-color: #1B5E20;
            color: white;
            padding: 2rem 0;
            margin-top: 3rem;
        }
        h1, h2, h3, h4, h5, h6 {
            color: #1B5E20 !important;
            font-weight: 600 !important;
        }
        .text-white h1, .text-white h2, .text-white h3, .text-white h4, .text-white h5, .text-white h6 {
            color: white !important;
        }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

# Main app layout with session storage
app.layout = dbc.Container([
    dcc.Location(id="url", refresh=False),
    dcc.Store(id="session-store", storage_type="session"),
    dcc.Store(id="user-store", storage_type="session"),
    html.Div(id="page-content")
], fluid=True, className="p-0")


# Main callback for page routing
@app.callback(
    Output("page-content", "children"),
    [Input("url", "search"), Input("session-store", "data")],
    [State("user-store", "data")]
)
def display_page(search, session_data, user_data):
    """Main page router"""

    # Check authentication status
    is_authenticated = auth_manager.validate_session(session_data)
    is_admin = auth_manager.is_admin(user_data) if is_authenticated else False

    # Create navbar with auth status
    navbar = create_navbar(is_authenticated, is_admin)

    # Route to different pages
    if search == "?request":
        return [navbar, create_access_request_form()]
    elif search == "?admin" and is_admin:
        return [navbar, create_admin_dashboard()]
    elif search == "?login":
        return [navbar, create_login_form()]
    else:
        # Home page - changes based on authentication
        return [navbar, create_homepage(is_authenticated, is_admin)]


# Login callback
@app.callback(
    [Output("session-store", "data", allow_duplicate=True),
     Output("user-store", "data", allow_duplicate=True),
     Output("login-alert", "children"),
     Output("url", "search", allow_duplicate=True)],
    [Input("login-btn", "n_clicks")],
    [State("login-username", "value"),
     State("login-password", "value")],
    prevent_initial_call=True
)
def handle_login(n_clicks, username, password):
    """Handle login attempts"""
    if not n_clicks:
        return dash.no_update, dash.no_update, "", dash.no_update

    if not username or not password:
        alert = dbc.Alert("Please enter both username and password.", color="danger")
        return dash.no_update, dash.no_update, alert, dash.no_update

    # Authenticate user
    auth_result = auth_manager.authenticate(username, password)

    if auth_result["success"]:
        session_data = auth_manager.create_session(auth_result["user"])
        user_data = auth_result["user"]

        # Redirect based on user type
        redirect_url = "?admin" if user_data.get("is_admin") else ""

        return session_data, user_data, "", redirect_url
    else:
        alert = dbc.Alert(auth_result["message"], color="danger")
        return dash.no_update, dash.no_update, alert, dash.no_update


# Logout callback
@app.callback(
    [Output("session-store", "data", allow_duplicate=True),
     Output("user-store", "data", allow_duplicate=True),
     Output("url", "search", allow_duplicate=True)],
    [Input("logout-btn", "n_clicks")],
    [State("session-store", "data")],
    prevent_initial_call=True
)
def handle_logout(n_clicks, session_data):
    """Handle logout"""
    if n_clicks:
        auth_manager.destroy_session(session_data)
        return {}, {}, ""
    return dash.no_update, dash.no_update, dash.no_update


def create_login_form():
    """Create login form component"""
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.H4([
                            html.I(className="fas fa-sign-in-alt me-2"),
                            "Login to IR Portal"
                        ], className="text-white mb-0")
                    ]),
                    dbc.CardBody([
                        html.Div(id="login-alert", className="mb-3"),
                        dbc.Form([
                            dbc.Row([
                                dbc.Col([
                                    dbc.Label("Username", className="fw-bold"),
                                    dbc.Input(id="login-username", type="text",
                                              placeholder="Enter your username")
                                ])
                            ], className="mb-3"),
                            dbc.Row([
                                dbc.Col([
                                    dbc.Label("Password", className="fw-bold"),
                                    dbc.Input(id="login-password", type="password",
                                              placeholder="Enter your password")
                                ])
                            ], className="mb-4"),
                            dbc.Button([
                                html.I(className="fas fa-sign-in-alt me-2"),
                                "Login"
                            ], id="login-btn", color="primary", className="w-100",
                                style={"borderRadius": "0"})
                        ])
                    ])
                ])
            ], md=6, className="mx-auto")
        ])
    ], className="py-5")


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8050))
    debug = not os.environ.get('RENDER')
    app.run(debug=debug, host='0.0.0.0', port=port)