import dash_bootstrap_components as dbc
from dash import html, dash_table
import pandas as pd
from utils.database import get_user_stats
from config import USC_COLORS


def create_admin_dashboard():
    """Create admin dashboard with management tools"""
    return dbc.Container([
        html.H1([
            html.I(className="fas fa-shield-alt me-3"),
            "Admin Dashboard"
        ], className="mb-4"),

        create_admin_stats_section(),
        create_admin_tabs(),

    ], className="py-4")


def create_admin_stats_section():
    """Create admin statistics overview"""
    try:
        stats = get_user_stats()
    except:
        stats = {
            "total_users": 0,
            "admin_users": 0,
            "active_sessions": 0,
            "pending_requests": 0,
            "recent_logins": 0
        }

    stat_cards = [
        {
            "title": "Total Users",
            "value": stats["total_users"],
            "icon": "fas fa-users",
            "color": "primary"
        },
        {
            "title": "Admin Users",
            "value": stats["admin_users"],
            "icon": "fas fa-user-shield",
            "color": "danger"
        },
        {
            "title": "Active Sessions",
            "value": stats["active_sessions"],
            "icon": "fas fa-clock",
            "color": "success"
        },
        {
            "title": "Pending Requests",
            "value": stats["pending_requests"],
            "icon": "fas fa-envelope",
            "color": "warning"
        },
        {
            "title": "Recent Logins",
            "value": stats["recent_logins"],
            "icon": "fas fa-sign-in-alt",
            "color": "info"
        }
    ]

    cards = []
    for stat in stat_cards:
        card = dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.Div([
                        html.I(className=f"{stat['icon']} fa-2x mb-2",
                               style={"color": USC_COLORS["primary_green"]}),
                        html.H3(str(stat["value"]), className="mb-1",
                                style={"color": USC_COLORS["primary_green"], "fontWeight": "700"}),
                        html.P(stat["title"], className="mb-0 text-muted")
                    ], className="text-center")
                ])
            ], className="h-100 shadow-sm")
        ], md=2, className="mb-3")
        cards.append(card)

    return html.Div([
        html.H3("System Overview", className="mb-4"),
        dbc.Row(cards)
    ], className="mb-5")


def create_admin_tabs():
    """Create admin dashboard tabs"""
    return dbc.Tabs([
        dbc.Tab(label="User Management", tab_id="users-tab"),
        dbc.Tab(label="Access Requests", tab_id="requests-tab"),
        dbc.Tab(label="System Settings", tab_id="settings-tab"),
        dbc.Tab(label="Audit Log", tab_id="audit-tab"),
        dbc.Tab(label="Data Management", tab_id="data-tab")
    ], id="admin-tabs", active_tab="users-tab", className="mb-4")


def create_user_management_tab():
    """User management interface"""
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

        # User table placeholder
        dbc.Card([
            dbc.CardHeader("Active Users"),
            dbc.CardBody([
                html.Div(id="users-table-container"),
                create_sample_users_table()
            ])
        ])
    ])


def create_sample_users_table():
    """Create a sample users table"""
    sample_data = [
        {
            "ID": 1,
            "Username": "admin",
            "Full Name": "System Administrator",
            "Email": "ir@usc.edu.tt",
            "Department": "Institutional Research",
            "Role": "Admin",
            "Status": "Active",
            "Last Login": "2025-01-08 10:30"
        },
        {
            "ID": 2,
            "Username": "nswaby",
            "Full Name": "Nordian C. Swaby Robinson",
            "Email": "ir@usc.edu.tt",
            "Department": "Institutional Research",
            "Role": "Admin",
            "Status": "Active",
            "Last Login": "2025-01-08 09:15"
        },
        {
            "ID": 3,
            "Username": "lwebster",
            "Full Name": "Liam Webster",
            "Email": "websterl@usc.edu.tt",
            "Department": "Institutional Research",
            "Role": "Admin",
            "Status": "Active",
            "Last Login": "2025-01-08 08:45"
        }
    ]

    return dash_table.DataTable(
        data=sample_data,
        columns=[
            {"name": "ID", "id": "ID"},
            {"name": "Username", "id": "Username"},
            {"name": "Full Name", "id": "Full Name"},
            {"name": "Email", "id": "Email"},
            {"name": "Department", "id": "Department"},
            {"name": "Role", "id": "Role"},
            {"name": "Status", "id": "Status"},
            {"name": "Last Login", "id": "Last Login"}
        ],
        style_cell={'textAlign': 'left', 'padding': '10px'},
        style_header={'backgroundColor': USC_COLORS['primary_green'], 'color': 'white', 'fontWeight': 'bold'},
        style_data_conditional=[
            {
                'if': {'filter_query': '{Role} = Admin'},
                'backgroundColor': '#fff3cd',
                'color': 'black',
            }
        ],
        page_size=10,
        sort_action="native",
        filter_action="native"
    )


def create_access_requests_tab():
    """Access requests management interface"""
    return html.Div([
        html.H4("Access Requests", className="mb-4"),
        dbc.Alert([
            html.I(className="fas fa-info-circle me-2"),
            "Review and manage access requests from external users and staff."
        ], color="info", className="mb-4"),

        dbc.Card([
            dbc.CardHeader("Pending Requests"),
            dbc.CardBody([
                html.Div(id="requests-table-container"),
                create_sample_requests_table()
            ])
        ])
    ])


def create_sample_requests_table():
    """Create sample access requests table"""
    sample_requests = [
        {
            "ID": 1,
            "Name": "John Smith",
            "Email": "john.smith@external.com",
            "Department": "Research Institute",
            "Position": "Research Analyst",
            "Access Type": "Factbook",
            "Requested": "2025-01-07",
            "Status": "Pending"
        },
        {
            "ID": 2,
            "Name": "Sarah Johnson",
            "Email": "s.johnson@usc.edu.tt",
            "Department": "Finance",
            "Position": "Financial Analyst",
            "Access Type": "Factbook, Alumni",
            "Requested": "2025-01-06",
            "Status": "Pending"
        }
    ]

    return dash_table.DataTable(
        data=sample_requests,
        columns=[
            {"name": "ID", "id": "ID"},
            {"name": "Name", "id": "Name"},
            {"name": "Email", "id": "Email"},
            {"name": "Department", "id": "Department"},
            {"name": "Position", "id": "Position"},
            {"name": "Access Type", "id": "Access Type"},
            {"name": "Requested", "id": "Requested"},
            {"name": "Status", "id": "Status"}
        ],
        style_cell={'textAlign': 'left', 'padding': '10px'},
        style_header={'backgroundColor': USC_COLORS['primary_green'], 'color': 'white', 'fontWeight': 'bold'},
        page_size=10,
        sort_action="native",
        filter_action="native"
    )


def create_system_settings_tab():
    """System settings interface"""
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
                                    dbc.Input(value="USC Institutional Research", type="text")
                                ], md=6),
                                dbc.Col([
                                    dbc.Label("Session Timeout (hours)"),
                                    dbc.Input(value="8", type="number")
                                ], md=6)
                            ], className="mb-3"),
                            dbc.Row([
                                dbc.Col([
                                    dbc.Label("Max Login Attempts"),
                                    dbc.Input(value="5", type="number")
                                ], md=6),
                                dbc.Col([
                                    dbc.Label("Maintenance Mode"),
                                    dbc.Switch(id="maintenance-switch", value=False)
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
                        dbc.Form([
                            dbc.Checklist([
                                {"label": "Enable Factbook Access", "value": "factbook"},
                                {"label": "Enable Alumni Portal", "value": "alumni"},
                                {"label": "Enable User Registration", "value": "registration"},
                                {"label": "Enable Password Reset", "value": "password_reset"},
                                {"label": "Enable Audit Logging", "value": "audit_log"}
                            ], value=["factbook", "alumni", "password_reset", "audit_log"], id="feature-flags")
                        ])
                    ])
                ])
            ], md=6)
        ]),

        html.Hr(className="my-4"),

        dbc.Row([
            dbc.Col([
                dbc.Button("Save Settings", color="primary", className="me-2"),
                dbc.Button("Reset to Defaults", color="outline-secondary")
            ])
        ])
    ])


def create_audit_log_tab():
    """Audit log interface"""
    return html.Div([
        html.H4("Audit Log", className="mb-4"),
        dbc.Alert([
            html.I(className="fas fa-shield-alt me-2"),
            "System activity and security events are logged here."
        ], color="info", className="mb-4"),

        dbc.Card([
            dbc.CardHeader("Recent Activity"),
            dbc.CardBody([
                create_sample_audit_table()
            ])
        ])
    ])


def create_sample_audit_table():
    """Create sample audit log table"""
    sample_audit = [
        {
            "Timestamp": "2025-01-08 10:30:15",
            "User": "admin",
            "Action": "Login",
            "Resource": "System",
            "IP Address": "192.168.1.100",
            "Details": "Successful login"
        },
        {
            "Timestamp": "2025-01-08 10:25:30",
            "User": "nswaby",
            "Action": "Data Export",
            "Resource": "Enrollment Data",
            "IP Address": "192.168.1.101",
            "Details": "Exported 2024 enrollment data"
        },
        {
            "Timestamp": "2025-01-08 10:20:45",
            "User": "lwebster",
            "Action": "User Created",
            "Resource": "User Management",
            "IP Address": "192.168.1.102",
            "Details": "Created user: faculty1"
        }
    ]

    return dash_table.DataTable(
        data=sample_audit,
        columns=[
            {"name": "Timestamp", "id": "Timestamp"},
            {"name": "User", "id": "User"},
            {"name": "Action", "id": "Action"},
            {"name": "Resource", "id": "Resource"},
            {"name": "IP Address", "id": "IP Address"},
            {"name": "Details", "id": "Details"}
        ],
        style_cell={'textAlign': 'left', 'padding': '10px'},
        style_header={'backgroundColor': USC_COLORS['primary_green'], 'color': 'white', 'fontWeight': 'bold'},
        page_size=15,
        sort_action="native",
        filter_action="native"
    )


def create_data_management_tab():
    """Data management interface"""
    return html.Div([
        html.H4("Data Management", className="mb-4"),

        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Data Upload"),
                    dbc.CardBody([
                        html.P("Upload new data files to update system information."),
                        dbc.Form([
                            dbc.Label("Select Data Type"),
                            dbc.Select([
                                {"label": "Enrollment Data", "value": "enrollment"},
                                {"label": "Financial Data", "value": "financial"},
                                {"label": "Graduation Data", "value": "graduation"},
                                {"label": "Faculty Data", "value": "faculty"}
                            ], value="enrollment"),
                            html.Br(),
                            dbc.Label("Upload File"),
                            dbc.Input(type="file", accept=".xlsx,.xls,.csv"),
                            html.Br(),
                            dbc.Button("Upload Data", color="primary")
                        ])
                    ])
                ])
            ], md=6),
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Data Export"),
                    dbc.CardBody([
                        html.P("Export system data for backup or analysis."),
                        dbc.Form([
                            dbc.Label("Select Export Type"),
                            dbc.Select([
                                {"label": "Complete Database", "value": "complete"},
                                {"label": "User Data Only", "value": "users"},
                                {"label": "Academic Data Only", "value": "academic"},
                                {"label": "Financial Data Only", "value": "financial"}
                            ], value="complete"),
                            html.Br(),
                            dbc.Label("Export Format"),
                            dbc.RadioItems([
                                {"label": "Excel (.xlsx)", "value": "xlsx"},
                                {"label": "CSV", "value": "csv"},
                                {"label": "JSON", "value": "json"}
                            ], value="xlsx"),
                            html.Br(),
                            dbc.Button("Export Data", color="success")
                        ])
                    ])
                ])
            ], md=6)
        ]),

        html.Hr(className="my-4"),

        dbc.Card([
            dbc.CardHeader("Database Maintenance"),
            dbc.CardBody([
                dbc.Row([
                    dbc.Col([
                        dbc.Button([
                            html.I(className="fas fa-database me-2"),
                            "Backup Database"
                        ], color="info", className="me-2 mb-2")
                    ], md=3),
                    dbc.Col([
                        dbc.Button([
                            html.I(className="fas fa-broom me-2"),
                            "Clean Old Sessions"
                        ], color="warning", className="me-2 mb-2")
                    ], md=3),
                    dbc.Col([
                        dbc.Button([
                            html.I(className="fas fa-sync me-2"),
                            "Refresh Statistics"
                        ], color="secondary", className="me-2 mb-2")
                    ], md=3),
                    dbc.Col([
                        dbc.Button([
                            html.I(className="fas fa-chart-bar me-2"),
                            "Generate Report"
                        ], color="primary", className="mb-2")
                    ], md=3)
                ])
            ])
        ])
    ])