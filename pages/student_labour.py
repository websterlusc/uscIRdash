"""
Student Labour Report - Enhanced Version with Inline Filters and Monthly Expenses
"""

from dash import html, dcc
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from config import USC_COLORS

def load_data_dynamically():
    """Load data dynamically from Excel file each time - no caching"""
    try:
        print("🔄 Loading fresh data from Excel file...")
        # Import and use data loader fresh each time
        from importlib import reload
        import data_loader
        reload(data_loader)  # Force reload of data_loader module

        raw_data = data_loader.data_loader.load_student_labour_data()

        if raw_data and 'employment' in raw_data and 'expense' in raw_data:
            print("✅ Fresh data loaded successfully")
            employment_df = raw_data['employment'].copy()
            expense_df = raw_data['expense'].copy()
            monthly_expense_df = raw_data.get('monthly_expense', None)

            # Clean employment data
            employment_df['Academic Year'] = employment_df['Academic Year'].astype(str).str.strip()

            # Clean expense data
            expense_df['Year'] = expense_df['Year'].astype(str).str.strip()
            if 'Expense' in expense_df.columns:
                expense_df['Expense'] = expense_df['Expense'].astype(str).str.replace(',', '').str.replace(' ', '')
                expense_df['Expense'] = pd.to_numeric(expense_df['Expense'], errors='coerce')

            # Clean monthly expense data if available
            if monthly_expense_df is not None:
                monthly_expense_df = monthly_expense_df.copy()
                # Clean numeric columns (all except first column which should be Month)
                for col in monthly_expense_df.columns[1:]:
                    if col in monthly_expense_df.columns:
                        monthly_expense_df[col] = pd.to_numeric(
                            monthly_expense_df[col].astype(str).str.replace(',', '').str.replace(' ', ''),
                            errors='coerce'
                        )

            print(f"📊 Loaded employment years: {employment_df['Academic Year'].unique().tolist()}")
            print(f"📊 Loaded expense years: {expense_df['Year'].unique().tolist()}")
            if monthly_expense_df is not None:
                monthly_years = [col for col in monthly_expense_df.columns if col != 'Month']
                print(f"📊 Loaded monthly years: {monthly_years}")

            return employment_df, expense_df, monthly_expense_df
        else:
            print("⚠️ Data loader returned empty, using sample data")
            return get_sample_data()

    except Exception as e:
        print(f"❌ Error loading fresh data: {e}")
        print("⚠️ Falling back to sample data")
        return get_sample_data()

def get_fresh_filter_options():
    """Get fresh filter options from current data"""
    employment_df, expense_df, monthly_expense_df = load_data_dynamically()

    available_employment_years = []
    available_expense_years = []
    available_monthly_years = []

    if employment_df is not None and not employment_df.empty:
        available_employment_years = employment_df['Academic Year'].unique().tolist()

    if expense_df is not None and not expense_df.empty:
        available_expense_years = expense_df['Year'].unique().tolist()

    if monthly_expense_df is not None and not monthly_expense_df.empty:
        available_monthly_years = [col for col in monthly_expense_df.columns if col != 'Month']

    return available_employment_years, available_expense_years, available_monthly_years

def get_sample_data():
    """Provide sample data based on the Excel file structure we examined"""
    print("📊 Creating sample data based on Excel structure...")

    # Employment data based on what we saw in the Excel file
    employment_data = {
        'Academic Year': ['2021-2022', '2022-2023', '2023-2024'],
        'Academic Employment': [28, 36, 39],
        'Non-Academic Employment': [22, 108, 116]
    }
    employment_df = pd.DataFrame(employment_data)

    # Expense data based on what we saw in the Excel file
    expense_data = {
        'Year': ['2021-2022', '2022-2023', '2023-2024'],
        'Expense': [721414.71, 1373333.33, 134534.23]
    }
    expense_df = pd.DataFrame(expense_data)

    # Monthly expense sample data
    monthly_expense_data = {
        'Month': ['July', 'August', 'September', 'October', 'November', 'December',
                 'January', 'February', 'March', 'April', 'May', 'June'],
        '2021-2022': [50949.25, 47256.86, 58476.70, 62380.45, 55342.12, 48976.33,
                     52109.87, 59123.44, 61234.56, 48567.89, 45123.67, 53890.12],
        '2022-2023': [67771.58, 75542.58, 120395.32, 118234.67, 95432.11, 87654.32,
                     102345.67, 113456.78, 125678.90, 95432.11, 78901.23, 89012.34],
        '2023-2024': [112032.16, 101974.89, 133529.52, 145678.90, 123456.78, 109876.54,
                     134567.89, 156789.01, 167890.12, 134567.89, 123456.78, 145678.90]
    }
    monthly_expense_df = pd.DataFrame(monthly_expense_data)

    print("✅ Sample data created successfully")
    return employment_df, expense_df, monthly_expense_df

# DON'T load data immediately - load fresh each time functions are called
print("📊 Student Labour Report module initialized - data will be loaded dynamically")

def create_employment_chart(view_mode='numbers', employment_type='both', selected_years=None):
    """Create employment chart with proper filters and styling - LOADS FRESH DATA"""
    print(f"🎨 Creating employment chart: view={view_mode}, type={employment_type}, years={selected_years}")

    # Load fresh data every time
    employment_df, _, _ = load_data_dynamically()

    if employment_df is None or employment_df.empty:
        print("❌ No employment data for chart")
        fig = go.Figure()
        fig.add_annotation(
            text="No employment data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16, color="gray")
        )
        fig.update_layout(height=500, title="Employment Chart")
        return fig

    # Filter data by selected years
    df = employment_df.copy()
    if selected_years and len(selected_years) > 0:
        print(f"📊 Filtering by years: {selected_years}")
        df = df[df['Academic Year'].isin(selected_years)]
        print(f"📊 Filtered data shape: {df.shape}")

    if df.empty:
        print("❌ No data after filtering")
        fig = go.Figure()
        fig.add_annotation(
            text="No data for selected years",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16, color="gray")
        )
        fig.update_layout(height=500, title="Employment Chart")
        return fig

    # Create chart based on filters - GROUPED BY EMPLOYMENT TYPE
    fig = go.Figure()

    # Define consistent colors matching other charts
    colors = [USC_COLORS["primary_green"], USC_COLORS["accent_yellow"], USC_COLORS["secondary_green"]]

    if employment_type == 'both':
        if view_mode == 'percentage':
            print("📊 Creating percentage view for both types - grouped by employment type")
            # Calculate percentages
            df['Total'] = df['Academic Employment'] + df['Non-Academic Employment']
            df['Academic %'] = (df['Academic Employment'] / df['Total'] * 100).round(1)
            df['Non-Academic %'] = (df['Non-Academic Employment'] / df['Total'] * 100).round(1)

            # Add traces for each year within each employment type
            for i, year in enumerate(df['Academic Year']):
                fig.add_trace(go.Bar(
                    name=year,
                    x=['Academic', 'Non-Academic'],
                    y=[df.iloc[i]['Academic %'], df.iloc[i]['Non-Academic %']],
                    text=[f"{df.iloc[i]['Academic %']}%", f"{df.iloc[i]['Non-Academic %']}%"],
                    textposition='outside',
                    textfont=dict(color='black', size=12),
                    marker_color=colors[i % len(colors)],  # Use consistent colors
                    showlegend=True
                ))

            title = "Student Employment Distribution (%) - Grouped by Employment Type"
            yaxis_title = "Percentage (%)"
        else:
            print("📊 Creating numbers view for both types - grouped by employment type")
            # Create grouped data for numbers
            for i, year in enumerate(df['Academic Year']):
                fig.add_trace(go.Bar(
                    name=year,
                    x=['Academic', 'Non-Academic'],
                    y=[df.iloc[i]['Academic Employment'], df.iloc[i]['Non-Academic Employment']],
                    text=[str(df.iloc[i]['Academic Employment']), str(df.iloc[i]['Non-Academic Employment'])],
                    textposition='outside',
                    textfont=dict(color='black', size=12),
                    marker_color=colors[i % len(colors)],  # Use consistent colors
                    showlegend=True
                ))

            title = "Student Employment Numbers - Grouped by Employment Type"
            yaxis_title = "Number of Students"

    elif employment_type == 'academic':
        print("📊 Creating academic only view")
        if view_mode == 'percentage':
            for i, year in enumerate(df['Academic Year']):
                fig.add_trace(go.Bar(
                    name=year,
                    x=['Academic'],
                    y=[100],
                    text=['100%'],
                    textposition='outside',
                    textfont=dict(color='black', size=12),
                    marker_color=colors[i % len(colors)],  # Use consistent colors
                    showlegend=True
                ))
            title = "Academic Employment (100%)"
            yaxis_title = "Percentage (%)"
        else:
            for i, year in enumerate(df['Academic Year']):
                fig.add_trace(go.Bar(
                    name=year,
                    x=['Academic'],
                    y=[df.iloc[i]['Academic Employment']],
                    text=[str(df.iloc[i]['Academic Employment'])],
                    textposition='outside',
                    textfont=dict(color='black', size=12),
                    marker_color=colors[i % len(colors)],  # Use consistent colors
                    showlegend=True
                ))
            title = "Academic Employment Numbers"
            yaxis_title = "Number of Students"

    else:  # non-academic
        print("📊 Creating non-academic only view")
        if view_mode == 'percentage':
            for i, year in enumerate(df['Academic Year']):
                fig.add_trace(go.Bar(
                    name=year,
                    x=['Non-Academic'],
                    y=[100],
                    text=['100%'],
                    textposition='outside',
                    textfont=dict(color='black', size=12),
                    marker_color=colors[i % len(colors)],  # Use consistent colors
                    showlegend=True
                ))
            title = "Non-Academic Employment (100%)"
            yaxis_title = "Percentage (%)"
        else:
            for i, year in enumerate(df['Academic Year']):
                fig.add_trace(go.Bar(
                    name=year,
                    x=['Non-Academic'],
                    y=[df.iloc[i]['Non-Academic Employment']],
                    text=[str(df.iloc[i]['Non-Academic Employment'])],
                    textposition='outside',
                    textfont=dict(color='black', size=12),
                    marker_color=colors[i % len(colors)],  # Use consistent colors
                    showlegend=True
                ))
            title = "Non-Academic Employment Numbers"
            yaxis_title = "Number of Students"

    fig.update_layout(
        title=dict(
            text=title,
            font=dict(size=16, color='black')
        ),
        xaxis_title="Employment Type",
        yaxis_title=yaxis_title,
        plot_bgcolor='white',
        paper_bgcolor='white',
        height=500,  # Increased height
        barmode='group',
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(color='black')
        )
    )

    fig.update_xaxes(title_font=dict(color='black'), tickfont=dict(color='black'))
    fig.update_yaxes(title_font=dict(color='black'), tickfont=dict(color='black'))

    print("✅ Employment chart created successfully")
    return fig

def create_expense_chart(chart_type='bar', view_mode='numbers', selected_years=None):
    """Create expense chart with proper filters and styling - LOADS FRESH DATA"""
    print(f"🎨 Creating expense chart: type={chart_type}, view={view_mode}, years={selected_years}")

    # Load fresh data every time
    _, expense_df, _ = load_data_dynamically()

    if expense_df is None or expense_df.empty:
        print("❌ No expense data for chart")
        fig = go.Figure()
        fig.add_annotation(
            text="No expense data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16, color="gray")
        )
        fig.update_layout(height=500, title="Expense Chart")
        return fig

    # Filter data by selected years
    df = expense_df.copy()
    if selected_years and len(selected_years) > 0:
        print(f"📊 Filtering expense data by years: {selected_years}")
        df = df[df['Year'].isin(selected_years)]
        print(f"📊 Filtered expense data shape: {df.shape}")

    if df.empty:
        print("❌ No expense data after filtering")
        fig = go.Figure()
        fig.add_annotation(
            text="No data for selected years",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16, color="gray")
        )
        fig.update_layout(height=500, title="Expense Chart")
        return fig

    # Handle view mode
    if view_mode == 'percentage':
        print("📊 Creating percentage view for expenses")
        total_expense = df['Expense'].sum()
        df['Percentage'] = (df['Expense'] / total_expense * 100).round(1)
        y_values = df['Percentage']
        y_title = "Percentage (%)"
        text_values = [f"{val}%" for val in df['Percentage']]
    else:
        print("📊 Creating numbers view for expenses")
        y_values = df['Expense']
        y_title = "Expense ($)"
        text_values = [f"${val:,.0f}" for val in df['Expense']]

    # Create chart based on type
    if chart_type == 'pie':
        print("📊 Creating pie chart")
        fig = px.pie(
            df,
            values=y_values,
            names='Year',
            title='Expense Distribution',
            color_discrete_sequence=[USC_COLORS["primary_green"], USC_COLORS["accent_yellow"], USC_COLORS["secondary_green"]]
        )
        fig.update_traces(
            textinfo='label+percent+value',
            textfont=dict(color='black', size=12)
        )
    elif chart_type == 'line':
        print("📊 Creating line chart")
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df['Year'],
            y=y_values,
            mode='lines+markers',
            name='Expenses',
            line=dict(color=USC_COLORS["primary_green"], width=3),
            marker=dict(size=8, color=USC_COLORS["primary_green"]),
            text=text_values,
            textposition='top center',
            textfont=dict(color='black', size=12)
        ))
        fig.update_layout(
            title='Expense Trend Over Years',
            xaxis_title='Year',
            yaxis_title=y_title
        )
    else:  # bar chart
        print("📊 Creating bar chart")
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=df['Year'],
            y=y_values,
            name='Expenses',
            marker_color=USC_COLORS["primary_green"],
            text=text_values,
            textposition='outside',
            textfont=dict(color='black', size=12)
        ))
        fig.update_layout(
            title='Annual Expenses',
            xaxis_title='Year',
            yaxis_title=y_title
        )

    # Apply consistent styling
    fig.update_layout(
        plot_bgcolor='white',
        paper_bgcolor='white',
        height=500,  # Increased height
        title_font=dict(size=16, color='black'),
        showlegend=False if chart_type != 'pie' else True
    )

    if chart_type != 'pie':
        fig.update_xaxes(title_font=dict(color='black'), tickfont=dict(color='black'))
        fig.update_yaxes(title_font=dict(color='black'), tickfont=dict(color='black'))

    print("✅ Expense chart created successfully")
    return fig

def create_monthly_expense_chart(chart_type='bar', selected_years=None):
    """Create monthly expense chart - LOADS FRESH DATA"""
    print(f"🎨 Creating monthly expense chart: type={chart_type}, years={selected_years}")

    # Load fresh data every time
    _, _, monthly_expense_df = load_data_dynamically()

    if monthly_expense_df is None or monthly_expense_df.empty:
        print("❌ No monthly expense data for chart")
        fig = go.Figure()
        fig.add_annotation(
            text="No monthly expense data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16, color="gray")
        )
        fig.update_layout(height=500, title="Monthly Expense Chart")
        return fig

    df = monthly_expense_df.copy()

    # Get available year columns
    year_columns = [col for col in df.columns if col != 'Month']

    # Filter by selected years if provided
    if selected_years and len(selected_years) > 0:
        year_columns = [col for col in year_columns if col in selected_years]

    if not year_columns:
        fig = go.Figure()
        fig.add_annotation(
            text="No data for selected years",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16, color="gray")
        )
        fig.update_layout(height=500, title="Monthly Expense Chart")
        return fig

    fig = go.Figure()

    if chart_type == 'line':
        print("📊 Creating monthly line chart")
        colors = [USC_COLORS["primary_green"], USC_COLORS["accent_yellow"], USC_COLORS["secondary_green"]]
        for i, year in enumerate(year_columns):
            fig.add_trace(go.Scatter(
                x=df['Month'],
                y=df[year],
                mode='lines+markers',
                name=year,
                line=dict(color=colors[i % len(colors)], width=3),
                marker=dict(size=6)
            ))
        title = 'Monthly Expense Trends'
    else:  # bar chart
        print("📊 Creating monthly bar chart")
        colors = [USC_COLORS["primary_green"], USC_COLORS["accent_yellow"], USC_COLORS["secondary_green"]]
        for i, year in enumerate(year_columns):
            fig.add_trace(go.Bar(
                x=df['Month'],
                y=df[year],
                name=year,
                marker_color=colors[i % len(colors)],
                text=[f"${val:,.0f}" for val in df[year]],
                textposition='outside',
                textfont=dict(color='black', size=10)
            ))
        title = 'Monthly Expenses by Year'

    fig.update_layout(
        title=dict(text=title, font=dict(size=16, color='black')),
        xaxis_title='Month',
        yaxis_title='Expense ($)',
        plot_bgcolor='white',
        paper_bgcolor='white',
        height=500,  # Increased height
        barmode='group' if chart_type == 'bar' else None,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(color='black')
        )
    )

    fig.update_xaxes(title_font=dict(color='black'), tickfont=dict(color='black'))
    fig.update_yaxes(title_font=dict(color='black'), tickfont=dict(color='black'))

    print("✅ Monthly expense chart created successfully")
    return fig

# Get fresh filter options each time
available_employment_years, available_expense_years, available_monthly_years = get_fresh_filter_options()

print(f"📊 Available employment years: {available_employment_years}")
print(f"📊 Available expense years: {available_expense_years}")
print(f"📊 Available monthly years: {available_monthly_years}")

# Create layout with inline filters
def create_layout():
    """Create and return the layout for the student labour report"""
    try:
        return dbc.Container([
            # Header
            dbc.Row([
                dbc.Col([
                    html.H1([
                        html.I(className="fas fa-users-cog me-3"),
                        "Student Labour Report"
                    ], className="mb-4", style={"color": USC_COLORS["primary_green"]}),
                ])
            ]),

            # Employment Chart Section with Sidebar
            dbc.Row([
                # Left Sidebar - Employment Filters
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            html.H6([
                                html.I(className="fas fa-filter me-2"),
                                "Employment Filters"
                            ], className="mb-0", style={'color': USC_COLORS["accent_yellow"]})
                        ], style={'backgroundColor': USC_COLORS["primary_green"]}),
                        dbc.CardBody([
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
                                options=[{'label': year, 'value': year} for year in available_employment_years],
                                value=available_employment_years,
                                multi=True,
                                className="mb-3"
                            ),
                        ])
                    ])
                ], width=3),

                # Right Content - Employment Chart
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            html.H5([
                                html.I(className="fas fa-chart-bar me-2"),
                                "Employment Analysis"
                            ], className="mb-0", style={'color': USC_COLORS["accent_yellow"]})
                        ], style={'backgroundColor': USC_COLORS["primary_green"]}),
                        dbc.CardBody([
                            dcc.Graph(
                                id='employment-chart',
                                figure=create_employment_chart()
                            )
                        ])
                    ])
                ], width=9)
            ], className="mb-4"),

            # Annual Expense Chart Section with Sidebar
            dbc.Row([
                # Left Sidebar - Expense Filters
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            html.H6([
                                html.I(className="fas fa-filter me-2"),
                                "Expense Filters"
                            ], className="mb-0", style={'color': USC_COLORS["accent_yellow"]})
                        ], style={'backgroundColor': USC_COLORS["primary_green"]}),
                        dbc.CardBody([
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
                                options=[{'label': year, 'value': year} for year in available_expense_years],
                                value=available_expense_years,
                                multi=True,
                                className="mb-3"
                            ),
                        ])
                    ])
                ], width=3),

                # Right Content - Expense Chart
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            html.H5([
                                html.I(className="fas fa-chart-line me-2"),
                                "Annual Expense Analysis"
                            ], className="mb-0", style={'color': USC_COLORS["accent_yellow"]})
                        ], style={'backgroundColor': USC_COLORS["primary_green"]}),
                        dbc.CardBody([
                            dcc.Graph(
                                id='expense-chart',
                                figure=create_expense_chart()
                            )
                        ])
                    ])
                ], width=9)
            ], className="mb-4"),

            # Monthly Expense Chart Section with Sidebar
            dbc.Row([
                # Left Sidebar - Monthly Expense Filters
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            html.H6([
                                html.I(className="fas fa-filter me-2"),
                                "Monthly Filters"
                            ], className="mb-0", style={'color': USC_COLORS["accent_yellow"]})
                        ], style={'backgroundColor': USC_COLORS["primary_green"]}),
                        dbc.CardBody([
                            html.Label("Chart Type:", className="fw-bold mb-2"),
                            dcc.RadioItems(
                                id='monthly-chart-radio',
                                options=[
                                    {'label': ' Bar Chart', 'value': 'bar'},
                                    {'label': ' Line Chart', 'value': 'line'}
                                ],
                                value='line',
                                className="mb-3"
                            ),

                            html.Label("Academic Years:", className="fw-bold mb-2"),
                            dcc.Dropdown(
                                id='monthly-years-dropdown',
                                options=[{'label': year, 'value': year} for year in available_monthly_years],
                                value=available_monthly_years,
                                multi=True,
                                className="mb-3"
                            ),
                        ])
                    ])
                ], width=3),

                # Right Content - Monthly Expense Chart
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            html.H5([
                                html.I(className="fas fa-calendar-alt me-2"),
                                "Monthly Expense Analysis"
                            ], className="mb-0", style={'color': USC_COLORS["accent_yellow"]})
                        ], style={'backgroundColor': USC_COLORS["primary_green"]}),
                        dbc.CardBody([
                            dcc.Graph(
                                id='monthly-expense-chart',
                                figure=create_monthly_expense_chart()
                            )
                        ])
                    ])
                ], width=9)
            ])
        ], fluid=True)
    except Exception as e:
        print(f"❌ Error creating layout: {e}")
        import traceback
        traceback.print_exc()
        # Return a simple error layout
        return dbc.Container([
            dbc.Alert([
                html.H4("Layout Error", className="alert-heading"),
                html.P(f"Error creating student labour report layout: {str(e)}"),
                html.P("Check the console for detailed error information.")
            ], color="danger")
        ])

# Create the layout
layout = create_layout()

print("✅ Student Labour Report layout created successfully")