"""
Student Labour Report - Working Version
"""

from dash import html, dcc, callback, Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from config import USC_COLORS

def load_data():
    """Load data using the working data_loader"""
    try:
        from data_loader import data_loader
        print("🔄 Loading student labour data...")

        raw_data = data_loader.load_student_labour_data()
        print(f"✅ Raw data loaded: {list(raw_data.keys()) if raw_data else 'None'}")

        if not raw_data:
            return None, None

        # Get employment data
        employment_df = raw_data.get('employment')
        expense_df = raw_data.get('expense')

        if employment_df is not None:
            print(f"📊 Employment shape: {employment_df.shape}")
            print(f"📊 Employment data:\n{employment_df}")

        if expense_df is not None:
            print(f"📊 Expense shape: {expense_df.shape}")
            print(f"📊 Expense data:\n{expense_df}")

        return employment_df, expense_df

    except Exception as e:
        print(f"❌ Error loading data: {e}")
        import traceback
        traceback.print_exc()
        return None, None

# Load data immediately
employment_df, expense_df = load_data()

def create_employment_chart(view_mode='numbers', employment_type='both', selected_years=None):
    """Create employment chart with filters"""
    if employment_df is None:
        fig = go.Figure()
        fig.add_annotation(text="No employment data", xref="paper", yref="paper", x=0.5, y=0.5)
        return fig

    # Filter by selected years
    df = employment_df.copy()
    if selected_years:
        df = df[df['Academic Year'].isin(selected_years)]

    if df.empty:
        fig = go.Figure()
        fig.add_annotation(text="No data for selected years", xref="paper", yref="paper", x=0.5, y=0.5)
        return fig

    # Create chart based on employment type and view mode
    fig = go.Figure()

    if employment_type == 'both':
        if view_mode == 'percentage':
            # Calculate percentages
            df['Total'] = df['Academic Employment'] + df['Non-Academic Employment']
            df['Academic %'] = (df['Academic Employment'] / df['Total'] * 100).round(1)
            df['Non-Academic %'] = (df['Non-Academic Employment'] / df['Total'] * 100).round(1)

            fig.add_trace(go.Bar(
                name='Academic',
                x=df['Academic Year'],
                y=df['Academic %'],
                marker_color=USC_COLORS["primary_green"]
            ))
            fig.add_trace(go.Bar(
                name='Non-Academic',
                x=df['Academic Year'],
                y=df['Non-Academic %'],
                marker_color=USC_COLORS["accent_yellow"]
            ))
            title = "Student Employment Distribution (%)"
            y_title = "Percentage (%)"
        else:
            fig.add_trace(go.Bar(
                name='Academic',
                x=df['Academic Year'],
                y=df['Academic Employment'],
                marker_color=USC_COLORS["primary_green"]
            ))
            fig.add_trace(go.Bar(
                name='Non-Academic',
                x=df['Academic Year'],
                y=df['Non-Academic Employment'],
                marker_color=USC_COLORS["accent_yellow"]
            ))
            title = "Student Employment Numbers"
            y_title = "Number of Students"

    elif employment_type == 'academic':
        y_data = df['Academic Employment']
        if view_mode == 'percentage':
            total = df['Academic Employment'].sum()
            y_data = (df['Academic Employment'] / total * 100).round(1)
            title = "Academic Employment Distribution (%)"
            y_title = "Percentage of Total (%)"
        else:
            title = "Academic Employment Numbers"
            y_title = "Number of Students"

        fig.add_trace(go.Bar(
            name='Academic',
            x=df['Academic Year'],
            y=y_data,
            marker_color=USC_COLORS["primary_green"]
        ))

    else:  # non-academic
        y_data = df['Non-Academic Employment']
        if view_mode == 'percentage':
            total = df['Non-Academic Employment'].sum()
            y_data = (df['Non-Academic Employment'] / total * 100).round(1)
            title = "Non-Academic Employment Distribution (%)"
            y_title = "Percentage of Total (%)"
        else:
            title = "Non-Academic Employment Numbers"
            y_title = "Number of Students"

        fig.add_trace(go.Bar(
            name='Non-Academic',
            x=df['Academic Year'],
            y=y_data,
            marker_color=USC_COLORS["accent_yellow"]
        ))

    fig.update_layout(
        title=title,
        xaxis_title="Academic Year",
        yaxis_title=y_title,
        barmode='group',
        height=400,
        showlegend=employment_type == 'both'
    )
    return fig

def create_expense_chart(chart_type='bar', view_mode='numbers', selected_years=None):
    """Create expense chart with filters"""
    if expense_df is None:
        fig = go.Figure()
        fig.add_annotation(text="No expense data", xref="paper", yref="paper", x=0.5, y=0.5)
        return fig

    # Clean and filter data
    df = expense_df.copy()
    df['Year'] = df['Year'].astype(str).str.strip()
    df['Expense'] = pd.to_numeric(df['Expense'].astype(str).str.replace(',', '').str.replace(' ', ''), errors='coerce')

    if selected_years:
        df = df[df['Year'].isin(selected_years)]

    if df.empty:
        fig = go.Figure()
        fig.add_annotation(text="No data for selected years", xref="paper", yref="paper", x=0.5, y=0.5)
        return fig

    # Handle percentage view
    if view_mode == 'percentage':
        total = df['Expense'].sum()
        df['Percentage'] = (df['Expense'] / total * 100).round(1)
        y_column = 'Percentage'
        y_title = "Percentage of Total (%)"
    else:
        y_column = 'Expense'
        y_title = "Expense ($)"

    # Create chart based on type
    if chart_type == 'pie':
        fig = px.pie(
            df,
            values=y_column,
            names='Year',
            title=f'Expense Distribution ({view_mode.title()})',
            color_discrete_sequence=[USC_COLORS["primary_green"], USC_COLORS["accent_yellow"], USC_COLORS["secondary_green"]]
        )
    elif chart_type == 'line':
        fig = px.line(
            df,
            x='Year',
            y=y_column,
            title=f'Expense Trend ({view_mode.title()})',
            markers=True
        )
        fig.update_traces(line=dict(color=USC_COLORS["primary_green"], width=3), marker=dict(size=8))
    else:  # bar
        fig = px.bar(
            df,
            x='Year',
            y=y_column,
            title=f'Annual Expenses ({view_mode.title()})',
            color_discrete_sequence=[USC_COLORS["primary_green"]]
        )

    if chart_type != 'pie':
        fig.update_layout(
            xaxis_title="Year",
            yaxis_title=y_title,
            height=400
        )
    else:
        fig.update_layout(height=400)

    return fig

# Callbacks
@callback(
    Output('employment-chart', 'figure'),
    [Input('employment-view-radio', 'value'),
     Input('employment-type-dropdown', 'value'),
     Input('employment-years-dropdown', 'value')],
    prevent_initial_call=False
)
def update_employment_chart(view_mode, employment_type, selected_years):
    """Update employment chart based on filters"""
    print(f"🔄 Employment callback triggered: view={view_mode}, type={employment_type}, years={selected_years}")

    # Handle None values with proper defaults
    if view_mode is None:
        view_mode = 'numbers'
    if employment_type is None:
        employment_type = 'both'
    if selected_years is None or len(selected_years) == 0:
        selected_years = ['2021-2022', '2022-2023', '2023-2024'] if employment_df is not None else []

    print(f"🔄 Creating employment chart with: view={view_mode}, type={employment_type}, years={selected_years}")

    try:
        result = create_employment_chart(view_mode, employment_type, selected_years)
        print("✅ Employment chart updated successfully")
        return result
    except Exception as e:
        print(f"❌ Error updating employment chart: {e}")
        import traceback
        traceback.print_exc()
        # Return a basic working chart as fallback
        return create_employment_chart('numbers', 'both', ['2021-2022', '2022-2023', '2023-2024'])

@callback(
    Output('expense-chart', 'figure'),
    [Input('expense-chart-radio', 'value'),
     Input('expense-view-radio', 'value'),
     Input('expense-years-dropdown', 'value')],
    prevent_initial_call=False
)
def update_expense_chart(chart_type, view_mode, selected_years):
    """Update expense chart based on filters"""
    print(f"🔄 Expense callback triggered: type={chart_type}, view={view_mode}, years={selected_years}")

    # Handle None values with proper defaults
    if chart_type is None:
        chart_type = 'bar'
    if view_mode is None:
        view_mode = 'numbers'
    if selected_years is None or len(selected_years) == 0:
        selected_years = ['2021-2022', '2022-2023', '2023-2024'] if expense_df is not None else []

    print(f"🔄 Creating expense chart with: type={chart_type}, view={view_mode}, years={selected_years}")

    try:
        result = create_expense_chart(chart_type, view_mode, selected_years)
        print("✅ Expense chart updated successfully")
        return result
    except Exception as e:
        print(f"❌ Error updating expense chart: {e}")
        import traceback
        traceback.print_exc()
        # Return a basic working chart as fallback
        return create_expense_chart('bar', 'numbers', ['2021-2022', '2022-2023', '2023-2024'])

# Create layout with left sidebar filters
layout = dbc.Container([
    # Header
    dbc.Row([
        dbc.Col([
            html.H1([
                html.I(className="fas fa-users-cog me-3"),
                "Student Labour Report"
            ], className="mb-4", style={"color": USC_COLORS["primary_green"]}),
        ])
    ]),

    # Main content with sidebar
    dbc.Row([
        # Left Sidebar - Filters
        dbc.Col([
            dbc.Card([
                dbc.CardHeader([
                    html.H5([
                        html.I(className="fas fa-filter me-2"),
                        "Filters & Controls"
                    ], className="mb-0", style={'color': 'white'})
                ], style={'backgroundColor': USC_COLORS["primary_green"]}),
                dbc.CardBody([
                    # Employment Filters
                    html.H6("👥 Employment Analysis", className="mb-3", style={'color': USC_COLORS["primary_green"]}),

                    html.Label("View Mode:", className="fw-bold mb-2"),
                    dcc.RadioItems(
                        id='employment-view-radio',
                        options=[
                            {'label': ' Numbers', 'value': 'numbers'},
                            {'label': ' Percentage', 'value': 'percentage'}
                        ],
                        value='numbers',
                        className="mb-3"
                    ),

                    html.Label("Employment Type:", className="fw-bold mb-2"),
                    dcc.Dropdown(
                        id='employment-type-dropdown',
                        options=[
                            {'label': 'Both Academic & Non-Academic', 'value': 'both'},
                            {'label': 'Academic Only', 'value': 'academic'},
                            {'label': 'Non-Academic Only', 'value': 'non-academic'}
                        ],
                        value='both',
                        className="mb-3"
                    ),

                    html.Label("Academic Years:", className="fw-bold mb-2"),
                    dcc.Dropdown(
                        id='employment-years-dropdown',
                        options=[
                            {'label': '2021-2022', 'value': '2021-2022'},
                            {'label': '2022-2023', 'value': '2022-2023'},
                            {'label': '2023-2024', 'value': '2023-2024'}
                        ] if employment_df is not None else [],
                        value=['2021-2022', '2022-2023', '2023-2024'] if employment_df is not None else [],
                        multi=True,
                        className="mb-4"
                    ),

                    html.Hr(),

                    # Expense Filters
                    html.H6("💰 Expense Analysis", className="mb-3", style={'color': USC_COLORS["primary_green"]}),

                    html.Label("Chart Type:", className="fw-bold mb-2"),
                    dcc.RadioItems(
                        id='expense-chart-radio',
                        options=[
                            {'label': ' Bar Chart', 'value': 'bar'},
                            {'label': ' Line Chart', 'value': 'line'},
                            {'label': ' Pie Chart', 'value': 'pie'}
                        ],
                        value='bar',
                        className="mb-3"
                    ),

                    html.Label("View Mode:", className="fw-bold mb-2"),
                    dcc.RadioItems(
                        id='expense-view-radio',
                        options=[
                            {'label': ' Numbers', 'value': 'numbers'},
                            {'label': ' Percentage', 'value': 'percentage'}
                        ],
                        value='numbers',
                        className="mb-3"
                    ),

                    html.Label("Years:", className="fw-bold mb-2"),
                    dcc.Dropdown(
                        id='expense-years-dropdown',
                        options=[
                            {'label': '2021-2022', 'value': '2021-2022'},
                            {'label': '2022-2023', 'value': '2022-2023'},
                            {'label': '2023-2024', 'value': '2023-2024'}
                        ] if expense_df is not None else [],
                        value=['2021-2022', '2022-2023', '2023-2024'] if expense_df is not None else [],
                        multi=True,
                        className="mb-4"
                    ),

                    html.Hr(),

                    # Data Status
                    dbc.Alert([
                        html.Small([
                            html.Strong("Data Status:"), html.Br(),
                            f"Employment: {'✅' if employment_df is not None else '❌'} ({len(employment_df) if employment_df is not None else 0} records)", html.Br(),
                            f"Expense: {'✅' if expense_df is not None else '❌'} ({len(expense_df) if expense_df is not None else 0} records)"
                        ])
                    ], color="light", className="mb-0")
                ])
            ])
        ], width=3),

        # Right Side - Charts
        dbc.Col([
            # Employment Chart
            dbc.Card([
                dbc.CardHeader([
                    html.H5("👥 Employment Analysis", className="mb-0", style={'color': 'white'})
                ], style={'backgroundColor': USC_COLORS["primary_green"]}),
                dbc.CardBody([
                    dcc.Graph(
                        figure=create_employment_chart('numbers', 'both', ['2021-2022', '2022-2023', '2023-2024'] if employment_df is not None else []),
                        id='employment-chart'
                    )
                ])
            ], className="mb-4"),

            # Expense Chart
            dbc.Card([
                dbc.CardHeader([
                    html.H5("💰 Expense Analysis", className="mb-0", style={'color': 'white'})
                ], style={'backgroundColor': USC_COLORS["primary_green"]}),
                dbc.CardBody([
                    dcc.Graph(
                        figure=create_expense_chart('bar', 'numbers', ['2021-2022', '2022-2023', '2023-2024'] if expense_df is not None else []),
                        id='expense-chart'
                    )
                ])
            ])
        ], width=9)
    ])

], fluid=True, className="py-4")

print("🎯 Student Labour Report layout created!")