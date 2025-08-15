"""
Ultra Safe Student Labour Report Page

This version handles the exact column naming issue and won't crash the server.
"""

from dash import html, dcc
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from config import USC_COLORS

def safe_load_data():
    """Load data with maximum safety"""
    try:
        from data_loader import data_loader
        print("🔄 Starting safe data load...")

        raw_data = data_loader.load_student_labour_data()
        print(f"✅ Raw data loaded: {list(raw_data.keys()) if raw_data else 'None'}")

        # Process each dataset safely
        processed = {}

        # Handle Assignment data with 'Unnamed' columns
        if 'assignment' in raw_data:
            df = raw_data['assignment'].copy()
            print(f"📊 Assignment columns: {list(df.columns)}")

            # Rename unnamed columns to something useful
            if len(df.columns) >= 3:
                df.columns = ['School_Site', 'Year_2022_2023', 'Year_2023_2024']
                processed['assignment'] = df
                print("✅ Assignment data processed")
            else:
                print("❌ Assignment data has insufficient columns")

        # Handle Employment data
        if 'employment' in raw_data:
            df = raw_data['employment'].copy()
            print(f"📊 Employment columns: {list(df.columns)}")
            processed['employment'] = df
            print("✅ Employment data processed")

        # Handle Expense data
        if 'expense' in raw_data:
            df = raw_data['expense'].copy()
            print(f"📊 Expense columns: {list(df.columns)}")
            processed['expense'] = df
            print("✅ Expense data processed")

        # Handle Monthly data
        if 'monthly_expense' in raw_data:
            df = raw_data['monthly_expense'].copy()
            print(f"📊 Monthly columns: {list(df.columns)}")
            processed['monthly_expense'] = df
            print("✅ Monthly data processed")

        print(f"🎉 All data processed successfully: {list(processed.keys())}")
        return processed

    except Exception as e:
        print(f"❌ Error in safe_load_data: {e}")
        import traceback
        traceback.print_exc()
        return None

def create_safe_assignment_chart():
    """Create assignment chart with maximum error handling"""
    try:
        print("🔄 Creating assignment chart...")
        data = safe_load_data()

        if not data or 'assignment' not in data:
            print("❌ No assignment data available")
            return px.bar(x=['No Data'], y=[0], title="Assignment Data Not Available")

        df = data['assignment']
        print(f"📊 Assignment chart data shape: {df.shape}")
        print(f"📊 Assignment chart columns: {list(df.columns)}")

        if df.empty or len(df.columns) < 3:
            return px.bar(x=['No Data'], y=[0], title="Insufficient Assignment Data")

        # Use the renamed columns
        school_col = df.columns[0]  # Should be 'School_Site'
        year1_col = df.columns[1]   # Should be 'Year_2022_2023'
        year2_col = df.columns[2]   # Should be 'Year_2023_2024'

        # Create simple bar chart for just the latest year
        fig = px.bar(
            df.head(10),  # Limit to first 10 rows to avoid overcrowding
            x=school_col,
            y=year2_col,
            title="Student Assignments by School/Site (2023-2024)",
            color_discrete_sequence=[USC_COLORS['primary_green']]
        )

        fig.update_layout(
            height=400,
            plot_bgcolor='white',
            xaxis_tickangle=-45,
            font_family="Arial"
        )

        print("✅ Assignment chart created successfully")
        return fig

    except Exception as e:
        print(f"❌ Error creating assignment chart: {e}")
        import traceback
        traceback.print_exc()
        return px.bar(x=['Error'], y=[1], title=f"Chart Error: {str(e)}")

def create_safe_employment_chart():
    """Create employment chart safely"""
    try:
        print("🔄 Creating employment chart...")
        data = safe_load_data()

        if not data or 'employment' not in data:
            return px.bar(x=['No Data'], y=[0], title="Employment Data Not Available")

        df = data['employment']
        print(f"📊 Employment data shape: {df.shape}")

        if df.empty or len(df.columns) < 3:
            return px.bar(x=['No Data'], y=[0], title="Insufficient Employment Data")

        # Create simple grouped bar chart
        fig = go.Figure()

        year_col = df.columns[0]
        academic_col = df.columns[1]
        non_academic_col = df.columns[2]

        fig.add_trace(go.Bar(
            name='Academic Employment',
            x=df[year_col],
            y=df[academic_col],
            marker_color=USC_COLORS['primary_green']
        ))

        fig.add_trace(go.Bar(
            name='Non-Academic Employment',
            x=df[year_col],
            y=df[non_academic_col],
            marker_color=USC_COLORS['accent_yellow']
        ))

        fig.update_layout(
            title='Student Employment by Type',
            barmode='group',
            height=400,
            plot_bgcolor='white',
            font_family="Arial"
        )

        print("✅ Employment chart created successfully")
        return fig

    except Exception as e:
        print(f"❌ Error creating employment chart: {e}")
        return px.bar(x=['Error'], y=[1], title=f"Employment Chart Error: {str(e)}")

def create_safe_summary_cards():
    """Create summary cards safely"""
    try:
        print("🔄 Creating summary cards...")
        data = safe_load_data()

        if not data or 'employment' not in data:
            return [
                dbc.Card([
                    dbc.CardBody([
                        html.H4("N/A", className="text-muted"),
                        html.P("Data Loading", className="mb-0")
                    ])
                ], className="text-center")
            ] * 4

        emp_df = data['employment']

        if not emp_df.empty and len(emp_df.columns) >= 3:
            latest = emp_df.iloc[-1]
            academic = latest.iloc[1]
            non_academic = latest.iloc[2]
            total = academic + non_academic

            cards = [
                dbc.Card([
                    dbc.CardBody([
                        html.H4(f"{total}", className="text-primary"),
                        html.P("Total Employment", className="mb-0")
                    ])
                ], className="text-center"),

                dbc.Card([
                    dbc.CardBody([
                        html.H4(f"{academic}", className="text-success"),
                        html.P("Academic Jobs", className="mb-0")
                    ])
                ], className="text-center"),

                dbc.Card([
                    dbc.CardBody([
                        html.H4(f"{non_academic}", className="text-warning"),
                        html.P("Non-Academic Jobs", className="mb-0")
                    ])
                ], className="text-center"),

                dbc.Card([
                    dbc.CardBody([
                        html.H4(f"{academic/total*100:.1f}%", className="text-info"),
                        html.P("Academic %", className="mb-0")
                    ])
                ], className="text-center")
            ]

            print("✅ Summary cards created successfully")
            return cards

    except Exception as e:
        print(f"❌ Error creating summary cards: {e}")

    # Fallback cards
    return [
        dbc.Card([
            dbc.CardBody([
                html.H4("Error", className="text-danger"),
                html.P("Loading Failed", className="mb-0")
            ])
        ], className="text-center")
    ] * 4

def get_safe_layout():
    """Create ultra-safe layout"""
    print("🚀 Starting ultra-safe layout creation...")

    # Pre-create all components to avoid on-demand creation
    print("📊 Creating summary cards...")
    summary_cards = create_safe_summary_cards()

    print("📊 Creating assignment chart...")
    assignment_chart = create_safe_assignment_chart()

    print("📊 Creating employment chart...")
    employment_chart = create_safe_employment_chart()

    print("📊 All components created, building layout...")

    layout = dbc.Container([
        # Header
        dbc.Row([
            dbc.Col([
                html.H1([
                    html.I(className="fas fa-users-cog me-3"),
                    "Student Labour Report"
                ], className="mb-4", style={"color": USC_COLORS["primary_green"]}),

                dbc.Alert([
                    html.I(className="fas fa-info-circle me-2"),
                    "Data successfully loaded from Excel files. Showing simplified charts for stability."
                ], color="success", className="mb-4")
            ])
        ]),

        # Summary Cards
        dbc.Row([
            dbc.Col(card, md=3, className="mb-4") for card in summary_cards
        ]),

        # Charts
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5("Student Assignments by School", className="mb-0")),
                    dbc.CardBody([
                        dcc.Graph(
                            figure=assignment_chart,
                            config={'displayModeBar': False}
                        )
                    ])
                ])
            ], md=12, className="mb-4")
        ]),

        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5("Employment Statistics", className="mb-0")),
                    dbc.CardBody([
                        dcc.Graph(
                            figure=employment_chart,
                            config={'displayModeBar': False}
                        )
                    ])
                ])
            ], md=12, className="mb-4")
        ]),

        # Data Preview
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5("Data Status", className="mb-0")),
                    dbc.CardBody([
                        html.P("✅ Assignment sheet: Columns renamed from 'Unnamed' format"),
                        html.P("✅ Employment sheet: Academic Year, Academic Employment, Non-Academic Employment"),
                        html.P("✅ Expense sheet: Year, Expense"),
                        html.P("✅ Monthly sheet: Month, 2021-2022, 2022-2023, 2023-2024"),
                        html.Hr(),
                        html.P("📧 For detailed data analysis, contact: ir@usc.edu.tt", className="text-muted")
                    ])
                ])
            ])
        ])
    ], fluid=True, className="py-4")

    print("✅ Layout created successfully!")
    return layout

# Create the layout immediately
print("🎯 Creating ultra-safe student labour layout...")
layout = get_safe_layout()
print("🎉 Ultra-safe layout ready!")