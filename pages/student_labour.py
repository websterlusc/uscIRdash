"""
Student Labour Report Page for USC Factbook - Simple & Clean Version
"""

from dash import html, dcc, callback, Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from config import USC_COLORS


def load_student_labour_data():
    """Load student labour data from Excel file"""
    try:
        from data_loader import data_loader
        print("🔄 Loading student labour data...")

        raw_data = data_loader.load_student_labour_data()
        print(f"📊 Raw data keys: {list(raw_data.keys()) if raw_data else 'None'}")

        if not raw_data:
            print("❌ No raw data returned")
            return None, None

        # Employment data
        employment_df = None
        if 'employment' in raw_data:
            employment_df = raw_data['employment'].copy()
            print(f"📊 Employment data shape: {employment_df.shape}")
            print(f"📊 Employment columns: {list(employment_df.columns)}")
            print(
                f"📊 Employment years: {employment_df['Academic Year'].unique() if 'Academic Year' in employment_df.columns else 'No Academic Year column'}")
            employment_df['Academic Year'] = employment_df['Academic Year'].astype(str)
        else:
            print("❌ No employment data found")

        # Expense data
        expense_df = None
        if 'expense' in raw_data:
            expense_df = raw_data['expense'].copy()
            print(f"📊 Expense data shape: {expense_df.shape}")
            print(f"📊 Expense columns: {list(expense_df.columns)}")
            print(
                f"📊 Expense years: {expense_df['Year'].unique() if 'Year' in expense_df.columns else 'No Year column'}")
            expense_df['Year'] = expense_df['Year'].astype(str).str.strip()
            # Clean expense data
            expense_df['Expense'] = expense_df['Expense'].astype(str).str.replace(',', '').str.replace(' ', '')
            expense_df['Expense'] = pd.to_numeric(expense_df['Expense'], errors='coerce')
        else:
            print("❌ No expense data found")

        print("✅ Student labour data loaded successfully")
        return employment_df, expense_df

    except Exception as e:
        print(f"❌ Error loading student labour data: {e}")
        import traceback
        traceback.print_exc()
        return None, None


def create_employment_chart(employment_df, view_mode="Values", selected_years=None):
    """Create employment chart"""
    print(f"🎨 Creating employment chart: df={employment_df is not None}, view={view_mode}, years={selected_years}")

    if employment_df is None or employment_df.empty:
        print("❌ No employment data for chart")
        fig = go.Figure()
        fig.add_annotation(
            text="No employment data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16)
        )
        fig.update_layout(height=400, title="Employment Chart")
        return fig

    # Prepare data
    df = employment_df.copy()
    print(f"📊 Original data shape: {df.shape}")

    if selected_years:
        df = df[df['Academic Year'].isin(selected_years)]
        print(f"📊 Filtered data shape: {df.shape}")

    if df.empty:
        print("❌ No data after filtering")
        fig = go.Figure()
        fig.add_annotation(
            text="No data for selected years",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        )
        fig.update_layout(height=400, title="Employment Chart")
        return fig

    # Create chart based on view mode
    if view_mode == "Percentage":
        # Calculate percentages
        df['Total'] = df['Academic Employment'] + df['Non-Academic Employment']
        df['Academic %'] = (df['Academic Employment'] / df['Total'] * 100).round(1)
        df['Non-Academic %'] = (df['Non-Academic Employment'] / df['Total'] * 100).round(1)

        fig = go.Figure()
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
        fig.update_layout(
            title="Student Employment Distribution (%)",
            yaxis_title="Percentage (%)",
            barmode='group'
        )
    else:
        # Numbers view
        fig = go.Figure()
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
        fig.update_layout(
            title="Student Employment Numbers",
            yaxis_title="Number of Students",
            barmode='group'
        )

    fig.update_layout(
        xaxis_title="Academic Year",
        plot_bgcolor='white',
        height=400
    )

    print("✅ Employment chart created successfully")
    return fig


def create_expense_chart(expense_df, chart_type="Bar", view_mode="Values", selected_years=None):
    """Create expense chart"""
    print(f"🎨 Creating expense chart: df={expense_df is not None}, type={chart_type}, years={selected_years}")

    if expense_df is None or expense_df.empty:
        print("❌ No expense data for chart")
        fig = go.Figure()
        fig.add_annotation(
            text="No expense data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16)
        )
        fig.update_layout(height=400, title="Expense Chart")
        return fig

    # Prepare data
    df = expense_df.copy()
    print(f"📊 Original expense data shape: {df.shape}")

    if selected_years:
        df = df[df['Year'].isin(selected_years)]
        print(f"📊 Filtered expense data shape: {df.shape}")

    if df.empty:
        print("❌ No expense data after filtering")
        fig = go.Figure()
        fig.add_annotation(
            text="No data for selected years",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        )
        fig.update_layout(height=400, title="Expense Chart")
        return fig

    # Create chart based on type and view mode
    if chart_type == "Pie":
        fig = px.pie(
            df,
            values='Expense',
            names='Year',
            title='Expense Distribution',
            color_discrete_sequence=[USC_COLORS["primary_green"], USC_COLORS["accent_yellow"],
                                     USC_COLORS["secondary_green"]]
        )
    elif chart_type == "Line":
        fig = px.line(
            df,
            x='Year',
            y='Expense',
            title='Expense Trend',
            markers=True
        )
        fig.update_traces(line=dict(color=USC_COLORS["primary_green"], width=3), marker=dict(size=8))
    else:  # Bar chart
        fig = px.bar(
            df,
            x='Year',
            y='Expense',
            title='Annual Expenses',
            color='Year',
            color_discrete_sequence=[USC_COLORS["primary_green"], USC_COLORS["accent_yellow"],
                                     USC_COLORS["secondary_green"]]
        )

    if chart_type != "Pie":
        fig.update_layout(
            xaxis_title="Year",
            yaxis_title="Expense ($)",
            plot_bgcolor='white',
            height=400,
            showlegend=False
        )
    else:
        fig.update_layout(height=400)

    print("✅ Expense chart created successfully")
    return fig


# Load data once
employment_df, expense_df = load_student_labour_data()

# Create layout
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

    # Employment Section
    html.H3("👥 Employment Analysis", className="mb-3", style={"color": USC_COLORS["primary_green"]}),

    # Employment Filters
    dbc.Accordion([
        dbc.AccordionItem([
            dbc.Row([
                dbc.Col([
                    html.Label("View Mode:", className="fw-bold mb-2"),
                    dcc.RadioItems(
                        id='employment-view-radio',
                        options=[
                            {'label': ' Values', 'value': 'Values'},
                            {'label': ' Percentage', 'value': 'Percentage'}
                        ],
                        value='Values',
                        inline=True,
                        className="mb-3"
                    )
                ], md=6),
                dbc.Col([
                    html.Label("Academic Years:", className="fw-bold mb-2"),
                    dcc.Dropdown(
                        id='employment-years-dropdown',
                        options=[],
                        value=[],
                        multi=True,
                        className="mb-3"
                    )
                ], md=6)
            ])
        ], title="📊 Employment Filters")
    ], className="mb-3", start_collapsed=True),

    # Employment Chart
    dbc.Card([
        dbc.CardBody([
            dcc.Graph(id='employment-chart')
        ])
    ], className="mb-4"),

    html.Hr(),

    # Expense Section
    html.H3("💰 Expense Analysis", className="mb-3", style={"color": USC_COLORS["primary_green"]}),

    # Expense Filters
    dbc.Accordion([
        dbc.AccordionItem([
            dbc.Row([
                dbc.Col([
                    html.Label("Chart Type:", className="fw-bold mb-2"),
                    dcc.RadioItems(
                        id='expense-chart-radio',
                        options=[
                            {'label': ' Bar', 'value': 'Bar'},
                            {'label': ' Line', 'value': 'Line'},
                            {'label': ' Pie', 'value': 'Pie'}
                        ],
                        value='Bar',
                        inline=True,
                        className="mb-3"
                    )
                ], md=6),
                dbc.Col([
                    html.Label("Years:", className="fw-bold mb-2"),
                    dcc.Dropdown(
                        id='expense-years-dropdown',
                        options=[],
                        value=[],
                        multi=True,
                        className="mb-3"
                    )
                ], md=6)
            ])
        ], title="💰 Expense Filters")
    ], className="mb-3", start_collapsed=True),

    # Expense Chart
    dbc.Card([
        dbc.CardBody([
            dcc.Graph(id='expense-chart')
        ])
    ], className="mb-4")

], fluid=True, className="py-4")


# Callbacks
@callback(
    [Output('employment-years-dropdown', 'options'),
     Output('employment-years-dropdown', 'value')],
    Input('employment-chart', 'id')
)
def populate_employment_years(_):
    """Populate employment years dropdown"""
    print("🔄 Populating employment years dropdown...")
    if employment_df is not None and not employment_df.empty:
        years = sorted(employment_df['Academic Year'].unique(), reverse=True)
        print(f"📅 Found employment years: {years}")
        options = [{'label': year, 'value': year} for year in years]
        default_years = years[:3] if len(years) >= 3 else years
        print(f"📅 Default employment years: {default_years}")
        return options, default_years
    else:
        print("❌ No employment data for years dropdown")
        return [], []


@callback(
    [Output('expense-years-dropdown', 'options'),
     Output('expense-years-dropdown', 'value')],
    Input('expense-chart', 'id')
)
def populate_expense_years(_):
    """Populate expense years dropdown"""
    print("🔄 Populating expense years dropdown...")
    if expense_df is not None and not expense_df.empty:
        years = sorted(expense_df['Year'].unique(), reverse=True)
        print(f"📅 Found expense years: {years}")
        options = [{'label': year, 'value': year} for year in years]
        default_years = years[:3] if len(years) >= 3 else years
        print(f"📅 Default expense years: {default_years}")
        return options, default_years
    else:
        print("❌ No expense data for years dropdown")
        return [], []


@callback(
    Output('employment-chart', 'figure'),
    [Input('employment-view-radio', 'value'),
     Input('employment-years-dropdown', 'value')]
)
def update_employment_chart(view_mode, selected_years):
    """Update employment chart"""
    print(f"🔄 Updating employment chart: view={view_mode}, years={selected_years}")
    return create_employment_chart(employment_df, view_mode, selected_years)


@callback(
    Output('expense-chart', 'figure'),
    [Input('expense-chart-radio', 'value'),
     Input('expense-years-dropdown', 'value')]
)
def update_expense_chart(chart_type, selected_years):
    """Update expense chart"""
    print(f"🔄 Updating expense chart: type={chart_type}, years={selected_years}")
    return create_expense_chart(expense_df, chart_type, "Values", selected_years)


print("🎯 Student Labour Report initialized successfully!")