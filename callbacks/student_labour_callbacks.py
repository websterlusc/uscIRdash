"""
Student Labour Report Callbacks - Simple Working Version
"""

from dash import callback, Input, Output
import traceback
import plotly.graph_objects as go

def register_student_labour_callbacks():
    """Register all callbacks for the student labour report"""
    print("🔧 Registering student labour callbacks...")

    @callback(
        Output('employment-chart', 'figure'),
        [
            Input('employment-view-radio', 'value'),
            Input('employment-type-dropdown', 'value'),
            Input('employment-years-dropdown', 'value')
        ]
    )
    def update_employment_chart(view_mode, employment_type, selected_years):
        """Update employment chart based on filters"""
        print(f"🔄 Employment callback: view={view_mode}, type={employment_type}, years={selected_years}")

        try:
            from pages.ultra_safe_student_labour import create_employment_chart
            result = create_employment_chart(view_mode, employment_type, selected_years)
            print("✅ Employment chart updated")
            return result
        except Exception as e:
            print(f"❌ Employment error: {e}")
            fig = go.Figure()
            fig.add_annotation(text=f"Error: {str(e)}", xref="paper", yref="paper", x=0.5, y=0.5)
            fig.update_layout(height=500, title="Employment Chart Error")
            return fig

    @callback(
        Output('expense-chart', 'figure'),
        [
            Input('expense-chart-radio', 'value'),
            Input('expense-view-radio', 'value'),
            Input('expense-years-dropdown', 'value')
        ]
    )
    def update_expense_chart(chart_type, view_mode, selected_years):
        """Update expense chart based on filters"""
        print(f"🔄 Expense callback: type={chart_type}, view={view_mode}, years={selected_years}")

        try:
            from pages.ultra_safe_student_labour import create_expense_chart
            result = create_expense_chart(chart_type, view_mode, selected_years)
            print("✅ Expense chart updated")
            return result
        except Exception as e:
            print(f"❌ Expense error: {e}")
            fig = go.Figure()
            fig.add_annotation(text=f"Error: {str(e)}", xref="paper", yref="paper", x=0.5, y=0.5)
            fig.update_layout(height=500, title="Expense Chart Error")
            return fig

    @callback(
        Output('monthly-expense-chart', 'figure'),
        [
            Input('monthly-chart-radio', 'value'),
            Input('monthly-years-dropdown', 'value')
        ]
    )
    def update_monthly_expense_chart(chart_type, selected_years):
        """Update monthly expense chart based on filters"""
        print(f"🔄 Monthly callback: type={chart_type}, years={selected_years}")

        try:
            from pages.ultra_safe_student_labour import create_monthly_expense_chart
            result = create_monthly_expense_chart(chart_type, selected_years)
            print("✅ Monthly chart updated")
            return result
        except Exception as e:
            print(f"❌ Monthly error: {e}")
            fig = go.Figure()
            fig.add_annotation(text=f"Error: {str(e)}", xref="paper", yref="paper", x=0.5, y=0.5)
            fig.update_layout(height=500, title="Monthly Chart Error")
            return fig

    print("✅ All student labour callbacks registered successfully")