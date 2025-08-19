# Fresh Google Sign-In Frontend Components
# Replace your existing login page and callbacks

import dash
from dash import html, dcc, Input, Output, State, callback_context
import dash_bootstrap_components as dbc

# Google Client Configuration
GOOGLE_CLIENT_ID = "890006312213-jb98t4ftcjgbvalgrrbo46sl9u77e524.apps.googleusercontent.com"

# USC Colors (use your existing USC_COLORS)
USC_COLORS = {
    'primary_green': '#1B5E20',
    'secondary_green': '#4CAF50',
    'accent_yellow': '#FDD835',
    'white': '#FFFFFF',
    'light_gray': '#F5F5F5',
    'dark_gray': '#424242'
}


def create_google_signin_page():
    """Create a clean Google Sign-In page"""
    return dbc.Container([
        dcc.Store(id='google-credential-store', data=None),
        
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.Div([
                            html.Img(src="/assets/usc-logo.png", height="60", className="mb-3"),
                            html.H3("USC Institutional Research", className="mb-1"),
                            html.P("Sign in to access the portal", className="text-muted mb-0")
                        ], className="text-center")
                    ], style={'backgroundColor': USC_COLORS['primary_green'], 'color': 'white'}),
                    
                    dbc.CardBody([
                        # Status display
                        html.Div(id="signin-status", className="mb-3", children=[
                            html.P("Ready to sign in", className="text-center text-muted")
                        ]),
                        
                        # Google Sign-In Button Container
                        html.Div([
                            html.Div(
                                id="google-signin-button",
                                style={
                                    'minHeight': '50px',
                                    'display': 'flex',
                                    'justifyContent': 'center',
                                    'alignItems': 'center',
                                    'border': '1px solid #ddd',
                                    'borderRadius': '8px',
                                    'marginBottom': '20px'
                                }
                            )
                        ]),
                        
                        # Manual trigger button (for debugging)
                        dbc.Button(
                            "Manual Google Sign-In",
                            id="manual-google-btn",
                            color="outline-primary",
                            className="w-100 mb-3",
                            style={'display': 'none'}
                        ),
                        
                        # Information
                        dbc.Alert([
                            html.I(className="fas fa-info-circle me-2"),
                            "USC employees (@usc.edu.tt) are automatically approved. " +
                            "Other users will need admin approval."
                        ], color="info", className="small"),
                        
                        # Alert container
                        html.Div(id="login-alert")
                    ])
                ])
            ], width=12, md=6, lg=4)
        ], justify="center", className="min-vh-100 align-items-center")
    ], fluid=True)


def get_google_signin_javascript():
    """Generate the JavaScript for Google Sign-In"""
    return f"""
    <script src="https://accounts.google.com/gsi/client" async defer></script>
    <script>
        let googleInitialized = false;
        
        function updateStatus(message, isError = false) {{
            const statusEl = document.getElementById('signin-status');
            if (statusEl) {{
                const color = isError ? 'text-danger' : 'text-success';
                const icon = isError ? 'fas fa-exclamation-triangle' : 'fas fa-info-circle';
                statusEl.innerHTML = `<p class="text-center ${color}"><i class="${icon} me-2"></i>${message}</p>`;
            }}
            console.log('Google Sign-In:', message);
        }}
        
        function handleCredentialResponse(response) {{
            updateStatus('Credential received, processing...');
            
            // Store the credential in Dash
            if (window.dash_clientside && window.dash_clientside.set_props) {{
                try {{
                    window.dash_clientside.set_props("google-credential-store", {{
                        data: response.credential
                    }});
                    updateStatus('Redirecting...');
                }} catch (error) {{
                    updateStatus('Error processing credential: ' + error.message, true);
                }}
            }} else {{
                updateStatus('Dash not ready, please refresh the page', true);
            }}
        }}
        
        function initializeGoogleSignIn() {{
            if (typeof google === 'undefined') {{
                updateStatus('Google API not loaded', true);
                return;
            }}
            
            if (googleInitialized) {{
                updateStatus('Already initialized');
                return;
            }}
            
            try {{
                updateStatus('Initializing Google Sign-In...');
                
                google.accounts.id.initialize({{
                    client_id: "{GOOGLE_CLIENT_ID}",
                    callback: handleCredentialResponse,
                    auto_select: false,
                    cancel_on_tap_outside: false
                }});
                
                const buttonDiv = document.getElementById('google-signin-button');
                if (buttonDiv) {{
                    buttonDiv.innerHTML = ''; // Clear any existing content
                    
                    google.accounts.id.renderButton(buttonDiv, {{
                        theme: "filled_blue",
                        size: "large",
                        width: "300",
                        text: "signin_with",
                        logo_alignment: "left"
                    }});
                    
                    googleInitialized = true;
                    updateStatus('Click the button above to sign in');
                }} else {{
                    updateStatus('Button container not found', true);
                }}
                
            }} catch (error) {{
                updateStatus('Initialization error: ' + error.message, true);
            }}
        }}
        
        function manualGoogleSignIn() {{
            if (typeof google !== 'undefined' && google.accounts) {{
                updateStatus('Opening Google Sign-In...');
                google.accounts.id.prompt();
            }} else {{
                updateStatus('Google API not available', true);
            }}
        }}
        
        // Initialize when page loads
        document.addEventListener('DOMContentLoaded', function() {{
            updateStatus('Loading Google API...');
            
            // Wait for Google API to load
            const checkGoogle = setInterval(() => {{
                if (typeof google !== 'undefined' && google.accounts) {{
                    clearInterval(checkGoogle);
                    initializeGoogleSignIn();
                }}
            }}, 100);
            
            // Timeout after 10 seconds
            setTimeout(() => {{
                if (!googleInitialized) {{
                    clearInterval(checkGoogle);
                    updateStatus('Google API failed to load. Please refresh the page.', true);
                    // Show manual button as fallback
                    const manualBtn = document.getElementById('manual-google-btn');
                    if (manualBtn) manualBtn.style.display = 'block';
                }}
            }}, 10000);
        }});
        
        // Manual button click handler
        document.addEventListener('click', function(e) {{
            if (e.target && e.target.id === 'manual-google-btn') {{
                manualGoogleSignIn();
            }}
        }});
    </script>
    """


# Dash Callbacks for Google OAuth
def setup_google_oauth_callbacks(app):
    """Setup all callbacks for Google OAuth"""
    
    @app.callback(
        [Output('session-store', 'data'),
         Output('login-alert', 'children'),
         Output('url', 'pathname')],
        [Input('google-credential-store', 'data')],
        prevent_initial_call=True
    )
    def process_google_credential(credential):
        """Process Google credential from frontend"""
        if not credential:
            return dash.no_update, dash.no_update, dash.no_update
        
        # Import your Google OAuth handler here
        from google_oauth_fresh import handle_google_oauth_callback
        
        # Process the credential
        result = handle_google_oauth_callback(credential)
        
        if result['success']:
            return (
                result['session_data'],
                dbc.Alert(result['alert']['message'], color=result['alert']['color']),
                result['redirect']
            )
        else:
            return (
                dash.no_update,
                dbc.Alert(result['alert']['message'], color=result['alert']['color']),
                dash.no_update
            )


# Alternative simple login page (if you want to keep regular login too)
def create_login_page_with_google():
    """Create login page with both regular and Google sign-in options"""
    return dbc.Container([
        dcc.Store(id='google-credential-store', data=None),
        
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.H3("USC Institutional Research Login", className="text-center mb-0")
                    ], style={'backgroundColor': USC_COLORS['primary_green'], 'color': 'white'}),
                    
                    dbc.CardBody([
                        # Google Sign-In Section
                        html.Div([
                            html.H5("Quick Sign-In", className="text-center mb-3"),
                            html.Div(id="signin-status", className="text-center mb-2"),
                            html.Div(id="google-signin-button", className="mb-3",
                                   style={'minHeight': '50px', 'display': 'flex', 
                                         'justifyContent': 'center', 'alignItems': 'center',
                                         'border': '1px solid #ddd', 'borderRadius': '8px'}),
                        ]),
                        
                        html.Hr(),
                        
                        # Regular Login Form (keep your existing form here if needed)
                        html.Div([
                            html.H5("Regular Login", className="text-center mb-3"),
                            html.P("Coming soon - use Google Sign-In above", 
                                  className="text-center text-muted")
                        ]),
                        
                        # Alert container
                        html.Div(id="login-alert")
                    ])
                ])
            ], width=12, md=6, lg=4)
        ], justify="center", className="min-vh-100 align-items-center")
    ], fluid=True)


# HTML Head injection for Google API
def get_google_head_tags():
    """Get HTML head tags needed for Google Sign-In"""
    return [
        html.Meta(name="google-signin-client_id", content=GOOGLE_CLIENT_ID),
        html.Script(src="https://accounts.google.com/gsi/client", **{"async": True, "defer": True})
    ]


# Instructions for implementation
IMPLEMENTATION_INSTRUCTIONS = """
IMPLEMENTATION INSTRUCTIONS:

1. First, install required packages:
   pip install google-auth google-auth-oauthlib google-auth-httplib2

2. Replace your existing login page function:
   Replace create_login_page() with create_google_signin_page()

3. Add the JavaScript to your main app:
   In your main_app.py, add this to the layout:
   
   app.layout = html.Div([
       dcc.Location(id='url', refresh=False),
       dcc.Store(id='session-store', storage_type='session'),
       html.Div(get_google_signin_javascript(), 
                dangerouslySetInnerHTML={'__html': get_google_signin_javascript()}),
       html.Div(id='page-content')
   ])

4. Setup callbacks:
   Add setup_google_oauth_callbacks(app) after creating your app

5. Update your page router:
   if pathname == '/login' or not is_authenticated:
       return create_google_signin_page()

6. Test the implementation:
   - Run your app
   - Go to the login page
   - Check browser console (F12) for any errors
   - Try clicking the Google Sign-In button

DEBUGGING:
- Open browser dev tools (F12) and check console for messages
- Status messages will appear on the login page
- USC employees (@usc.edu.tt) are auto-approved
- Other users need admin approval
"""

print(IMPLEMENTATION_INSTRUCTIONS)
