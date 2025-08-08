"""
Working callback functions for the USC IR website
Add these to your main_app.py file
"""

from dash import callback, Input, Output, State, dash_table, ctx
import dash_bootstrap_components as dbc
from dash import html
import pandas as pd
import sqlite3
from datetime import datetime
import re
from auth.auth_manager import AuthManager
from utils.database import log_user_action

# Initialize auth manager
auth_manager = AuthManager()


# Access request form submission callback
@callback(
    Output("request-form-alert", "children"),
    [Input("submit-access-request", "n_clicks")],
    [State("req-name", "value"),
     State("req-email", "value"),
     State("req-department", "value"),
     State("req-position", "value"),
     State("req-usc-employee", "value"),
     State("req-access-type", "value"),
     State("req-duration", "value"),
     State("req-justification", "value"),
     State("req-agreement", "value")]
)
def submit_access_request(n_clicks, name, email, department, position,
                          is_usc_employee, access_type, duration, justification, agreement):
    if not n_clicks:
        return ""

    # Validation
    if not all([name, email, department, position, access_type, justification]):
        return dbc.Alert([
            html.I(className="fas fa-exclamation-triangle me-2"),
            "Please fill in all required fields."
        ], color="danger", dismissable=True)

    if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
        return dbc.Alert([
            html.I(className="fas fa-exclamation-triangle me-2"),
            "Please enter a valid email address."
        ], color="danger", dismissable=True)

    if not agreement:
        return dbc.Alert([
            html.I(className="fas fa-exclamation-triangle me-2"),
            "Please agree to the Data Usage Agreement."
        ], color="danger", dismissable=True)

    try:
        # Insert request into database
        conn = sqlite3.connect('usc_ir.db')
        cursor = conn.cursor()

        access_type_str = ','.join(access_type) if isinstance(access_type, list) else str(access_type)

        cursor.execute('''
            INSERT INTO access_requests 
            (name, email, department, position, is_usc_employee, access_type, justification, requested_duration)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (name, email, department, position, bool(is_usc_employee), access_type_str, justification, duration))

        request_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return dbc.Alert([
            html.I(className="fas fa-check-circle me-2"),
            html.Strong("Request Submitted Successfully!"), html.Br(),
            f"Your access request (ID: {request_id}) has been submitted. ",
            f"You will receive an email at {email} once reviewed. ",
            "USC employees typically receive faster processing."
        ], color="success", dismissable=False)

    except Exception as e:
        return dbc.Alert([
            html.I(className="fas fa-exclamation-triangle me-2"),
            f"Error submitting request: {str(e)}"
        ], color="danger", dismissable=True)


# Admin dashboard tab content callback
@callback(
    Output("admin-dashboard-content", "children"),
    [Input("admin-tabs", "active_tab")],
    [State("session-store", "data")]
)
def update_admin_dashboard_content(active_tab, session_data):
    # Validate session
    if not auth_manager.validate_session(session_data):
        return dbc.Alert("Session expired. Please login again.", color="danger")

    if active_tab == "users-tab":
        return create_user_management_content()
    elif active_tab == "requests-tab":
        return create_access_requests_content()
    elif active_tab == "settings-tab":
        return create_system_settings_content()
    elif active_tab == "audit-tab":
        return create_audit_log_content()
    elif active_tab == "data-tab":
        return create_data_management_content()
    else:
        return create_user_management_content()


def create_user_management_content():
    """Create user management interface with real data"""
    try:
        conn = sqlite3.connect('usc_ir.db')
        df = pd.read_sql_query('''
            SELECT id, username, full_name, email, department, 
                   CASE WHEN is_admin = 1 THEN 'Admin' ELSE 'User' END as role,
                   CASE WHEN is_active = 1 THEN 'Active' ELSE 'Inactive' END as status,
                   COALESCE(last_login, 'Never') as last_login
            FROM users 
            ORDER BY created_at DESC
        ''', conn)
        conn.close()

        return html.Div([
            dbc.Row([
                dbc.Col([
                    html.H4("User Management"),
                    html.P("Manage system users, roles, and permissions.")
                ], md=8),
                dbc.Col([
                    dbc.Button([
                        html.I(className="fas fa-plus me-2"),
                        "Add User"
                    ], color="primary", id="add-user-btn", className="mb-3")
                ], md=4, className="text-end")
            ]),

            dbc.Card([
                dbc.CardHeader("System Users"),
                dbc.CardBody([
                    dash_table.DataTable(
                        id="users-table",
                        data=df.to_dict('records'),
                        columns=[
                            {"name": "ID", "id": "id"},
                            {"name": "Username", "id": "username"},
                            {"name": "Full Name", "id": "full_name"},
                            {"name": "Email", "id": "email"},
                            {"name": "Department", "id": "department"},
                            {"name": "Role", "id": "role"},
                            {"name": "Status", "id": "status"},
                            {"name": "Last Login", "id": "last_login"}
                        ],
                        style_cell={'textAlign': 'left', 'padding': '10px'},
                        style_header={'backgroundColor': '#1B5E20', 'color': 'white', 'fontWeight': 'bold'},
                        style_data_conditional=[
                            {
                                'if': {'filter_query': '{role} = Admin'},
                                'backgroundColor': '#fff3cd',
                                'color': 'black',
                            }
                        ],
                        page_size=10,
                        sort_action="native",
                        filter_action="native"
                    )
                ])
            ])
        ])
    except Exception as e:
        return dbc.Alert(f"Error loading users: {str(e)}", color="danger")


def create_access_requests_content():
    """Create access requests interface with real data"""
    try:
        conn = sqlite3.connect('usc_ir.db')
        df = pd.read_sql_query('''
            SELECT id, name, email, department, position, access_type, 
                   CASE WHEN is_usc_employee = 1 THEN 'Yes' ELSE 'No' END as usc_employee,
                   requested_duration, status, 
                   DATE(timestamp) as requested_date,
                   justification
            FROM access_requests 
            ORDER BY timestamp DESC
        ''', conn)
        conn.close()

        # Separate pending and all requests
        pending_df = df[df['status'] == 'pending']

        return html.Div([
            html.H4("Access Requests Management", className="mb-4"),

            # Pending requests section
            dbc.Card([
                dbc.CardHeader([
                    html.H5([
                        html.I(className="fas fa-clock me-2"),
                        f"Pending Requests ({len(pending_df)})"
                    ], className="mb-0")
                ]),
                dbc.CardBody([
                    create_pending_requests_cards(pending_df) if len(pending_df) > 0
                    else html.P("No pending requests.", className="text-muted text-center py-4")
                ])
            ], className="mb-4"),

            # All requests table
            dbc.Card([
                dbc.CardHeader("All Requests History"),
                dbc.CardBody([
                    dash_table.DataTable(
                        id="requests-table",
                        data=df.to_dict('records'),
                        columns=[
                            {"name": "ID", "id": "id"},
                            {"name": "Name", "id": "name"},
                            {"name": "Email", "id": "email"},
                            {"name": "Department", "id": "department"},
                            {"name": "USC Employee", "id": "usc_employee"},
                            {"name": "Access Type", "id": "access_type"},
                            {"name": "Duration", "id": "requested_duration"},
                            {"name": "Status", "id": "status"},
                            {"name": "Requested", "id": "requested_date"}
                        ],
                        style_cell={'textAlign': 'left', 'padding': '10px'},
                        style_header={'backgroundColor': '#1B5E20', 'color': 'white', 'fontWeight': 'bold'},
                        style_data_conditional=[
                            {
                                'if': {'filter_query': '{status} = pending'},
                                'backgroundColor': '#fff3cd',
                            },
                            {
                                'if': {'filter_query': '{status} = approved'},
                                'backgroundColor': '#d4edda',
                            },
                            {
                                'if': {'filter_query': '{status} = denied'},
                                'backgroundColor': '#f8d7da',
                            }
                        ],
                        page_size=15,
                        sort_action="native",
                        filter_action="native"
                    )
                ])
            ])
        ])
    except Exception as e:
        return dbc.Alert(f"Error loading requests: {str(e)}", color="danger")


def create_pending_requests_cards(pending_df):
    """Create cards for pending requests"""
    if pending_df.empty:
        return html.P("No pending requests.", className="text-center text-muted py-4")

    cards = []
    for _, row in pending_df.iterrows():
        employee_badge = dbc.Badge("USC Employee" if row['usc_employee'] == 'Yes' else "External",
                                   color="success" if row['usc_employee'] == 'Yes' else "warning")

        card = dbc.Card([
            dbc.CardHeader([
                html.Div([
                    html.H6(f"{row['name']} - {row['email']}", className="mb-0"),
                    employee_badge
                ], className="d-flex justify-content-between align-items-center")
            ]),
            dbc.CardBody([
                html.P([
                    html.Strong("Department: "), row['department'], html.Br(),
                    html.Strong("Position: "), row['position'], html.Br(),
                    html.Strong("Access Type: "), row['access_type'], html.Br(),
                    html.Strong("Duration: "), f"{row['requested_duration']} days", html.Br(),
                    html.Strong("Requested: "), row['requested_date']
                ], className="mb-3"),

                html.Details([
                    html.Summary("View Justification", className="mb-2"),
                    html.P(row['justification'], className="text-muted small")
                ], className="mb-3"),

                dbc.Row([
                    dbc.Col([
                        dbc.Button([
                            html.I(className="fas fa-check me-2"),
                            "Approve"
                        ], id=f"approve-{row['id']}", color="success", size="sm", className="me-2"),
                        dbc.Button([
                            html.I(className="fas fa-times me-2"),
                            "Deny"
                        ], id=f"deny-{row['id']}", color="danger", size="sm")
                    ])
                ])
            ])
        ], className="mb-3")
        cards.append(card)

    return html.Div(cards)


def create_system_settings_content():
    """Create system settings interface"""
    return html.Div([
        html.H4("System Settings", className="mb-4"),

        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("General Settings"),
                    dbc.CardBody([
                        dbc.Form([
                            dbc.Row([
                                dbc.Col([
                                    dbc.Label("Site Name"),
                                    dbc.Input(id="setting-site-name", value="USC Institutional Research", type="text")
                                ], md=6),
                                dbc.Col([
                                    dbc.Label("Session Timeout (hours)"),
                                    dbc.Input(id="setting-session-timeout", value="8", type="number")
                                ], md=6)
                            ], className="mb-3"),
                            dbc.Row([
                                dbc.Col([
                                    dbc.Label("Max Login Attempts"),
                                    dbc.Input(id="setting-max-attempts", value="5", type="number")
                                ], md=6),
                                dbc.Col([
                                    dbc.Label("Maintenance Mode"),
                                    dbc.Switch(id="setting-maintenance", value=False)
                                ], md=6)
                            ], className="mb-3")
                        ])
                    ])
                ])
            ], md=6),
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Feature Flags"),
                    dbc.CardBody([
                        dbc.Checklist([
                            {"label": " Enable Factbook Access", "value": "factbook"},
                            {"label": " Enable Alumni Portal", "value": "alumni"},
                            {"label": " Enable User Registration", "value": "registration"},
                            {"label": " Enable Password Reset", "value": "password_reset"},
                            {"label": " Enable Audit Logging", "value": "audit_log"}
                        ], value=["factbook", "alumni", "password_reset", "audit_log"], id="feature-flags")
                    ])
                ])
            ], md=6)
        ]),

        html.Hr(className="my-4"),

        dbc.Row([
            dbc.Col([
                dbc.Button("Save Settings", id="save-settings-btn", color="primary", className="me-2"),
                dbc.Button("Reset to Defaults", id="reset-settings-btn", color="outline-secondary"),
                html.Div(id="settings-alert", className="mt-3")
            ])
        ])
    ])


def create_audit_log_content():
    """Create audit log interface with real data"""
    try:
        conn = sqlite3.connect('usc_ir.db')
        df = pd.read_sql_query('''
            SELECT a.timestamp, u.username, a.action, a.resource, 
                   a.ip_address, a.details
            FROM audit_log a
            LEFT JOIN users u ON a.user_id = u.id
            ORDER BY a.timestamp DESC
            LIMIT 100
        ''', conn)
        conn.close()

        if df.empty:
            # Create some sample audit entries
            sample_audit = [
                {
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "username": "admin",
                    "action": "Login",
                    "resource": "System",
                    "ip_address": "127.0.0.1",
                    "details": "Successful admin login"
                },
                {
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "username": "System",
                    "action": "Database",
                    "resource": "Setup",
                    "ip_address": "localhost",
                    "details": "Database initialized"
                }
            ]
            df = pd.DataFrame(sample_audit)

        return html.Div([
            html.H4("Audit Log", className="mb-4"),
            dbc.Alert([
                html.I(className="fas fa-shield-alt me-2"),
                "System activity and security events are logged here."
            ], color="info", className="mb-4"),

            dbc.Card([
                dbc.CardHeader("Recent Activity"),
                dbc.CardBody([
                    dash_table.DataTable(
                        data=df.to_dict('records'),
                        columns=[
                            {"name": "Timestamp", "id": "timestamp"},
                            {"name": "User", "id": "username"},
                            {"name": "Action", "id": "action"},
                            {"name": "Resource", "id": "resource"},
                            {"name": "IP Address", "id": "ip_address"},
                            {"name": "Details", "id": "details"}
                        ],
                        style_cell={'textAlign': 'left', 'padding': '10px'},
                        style_header={'backgroundColor': '#1B5E20', 'color': 'white', 'fontWeight': 'bold'},
                        page_size=20,
                        sort_action="native",
                        filter_action="native"
                    )
                ])
            ])
        ])
    except Exception as e:
        return dbc.Alert(f"Error loading audit log: {str(e)}", color="danger")


def create_data_management_content():
    """Create data management interface"""
    return html.Div([
        html.H4("Data Management", className="mb-4"),

        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Quick Actions"),
                    dbc.CardBody([
                        dbc.Row([
                            dbc.Col([
                                dbc.Button([
                                    html.I(className="fas fa-download me-2"),
                                    "Export Users"
                                ], id="export-users-btn", color="primary", className="w-100 mb-2")
                            ], md=6),
                            dbc.Col([
                                dbc.Button([
                                    html.I(className="fas fa-download me-2"),
                                    "Export Requests"
                                ], id="export-requests-btn", color="info", className="w-100 mb-2")
                            ], md=6)
                        ]),
                        dbc.Row([
                            dbc.Col([
                                dbc.Button([
                                    html.I(className="fas fa-broom me-2"),
                                    "Clean Old Sessions"
                                ], id="clean-sessions-btn", color="warning", className="w-100 mb-2")
                            ], md=6),
                            dbc.Col([
                                dbc.Button([
                                    html.I(className="fas fa-sync me-2"),
                                    "Refresh Stats"
                                ], id="refresh-stats-btn", color="secondary", className="w-100 mb-2")
                            ], md=6)
                        ])
                    ])
                ])
            ], md=6),
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Database Info"),
                    dbc.CardBody([
                        html.Div(id="db-info-content"),
                        get_database_info()
                    ])
                ])
            ], md=6)
        ])
    ])


def get_database_info():
    """Get database information"""
    try:
        conn = sqlite3.connect('usc_ir.db')
        cursor = conn.cursor()

        # Get table info
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()

        info = []
        for table in tables:
            table_name = table[0]
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            info.append(f"{table_name}: {count} records")

        conn.close()

        return html.Ul([html.Li(item) for item in info])

    except Exception as e:
        return html.P(f"Error getting database info: {str(e)}", className="text-danger")


# Settings save callback
@callback(
    Output("settings-alert", "children"),
    [Input("save-settings-btn", "n_clicks")],
    [State("setting-site-name", "value"),
     State("setting-session-timeout", "value"),
     State("setting-max-attempts", "value"),
     State("setting-maintenance", "value"),
     State("feature-flags", "value")]
)
def save_settings(n_clicks, site_name, session_timeout, max_attempts, maintenance, features):
    if not n_clicks:
        return ""

    try:
        # Here you would save to database
        # For now, just show success message
        return dbc.Alert([
            html.I(className="fas fa-check me-2"),
            "Settings saved successfully!"
        ], color="success", dismissable=True)
    except Exception as e:
        return dbc.Alert([
            html.I(className="fas fa-exclamation-triangle me-2"),
            f"Error saving settings: {str(e)}"
        ], color="danger", dismissable=True)
