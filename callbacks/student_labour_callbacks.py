"""
Student Labour Report Callbacks
Separated callbacks file for cleaner code organization
"""

from dash import callback, Input, Output
import traceback
import plotly.graph_objects as go

def register_student_labour_callbacks():
    """Register all callbacks for the student labour report"""
    
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
        print(f"🔄 Employment callback triggered: view={view_mode}, type={employment_type}, years={selected_years}")
        
        try:
            # Import the chart creation function
            from pages.ultra_safe_student_labour import create_employment_chart
            
            result = create_employment_chart(view_mode, employment_type, selected_years)
            print("✅ Employment chart updated successfully")
            return result
            
        except Exception as e:
            print(f"❌ Error in employment callback: {e}")
            traceback.print_exc()
            
            # Return a basic error chart
            fig = go.Figure()
            fig.add_annotation(
                text=f"Error updating employment chart: {str(e)}",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=16, color="red")
            )
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
        print(f"🔄 Expense callback triggered: type={chart_type}, view={view_mode}, years={selected_years}")
        
        try:
            # Import the chart creation function
            from pages.ultra_safe_student_labour import create_expense_chart
            
            result = create_expense_chart(chart_type, view_mode, selected_years)
            print("✅ Expense chart updated successfully")
            return result
            
        except Exception as e:
            print(f"❌ Error in expense callback: {e}")
            traceback.print_exc()
            
            # Return a basic error chart
            fig = go.Figure()
            fig.add_annotation(
                text=f"Error updating expense chart: {str(e)}",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=16, color="red")
            )
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
        print(f"🔄 Monthly expense callback triggered: type={chart_type}, years={selected_years}")
        
        try:
            # Import the chart creation function
            from pages.ultra_safe_student_labour import create_monthly_expense_chart
            
            result = create_monthly_expense_chart(chart_type, selected_years)
            print("✅ Monthly expense chart updated successfully")
            return result
            
        except Exception as e:
            print(f"❌ Error in monthly expense callback: {e}")
            traceback.print_exc()
            
            # Return a basic error chart
            fig = go.Figure()
            fig.add_annotation(
                text=f"Error updating monthly expense chart: {str(e)}",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=16, color="red")
            )
            fig.update_layout(height=500, title="Monthly Expense Chart Error")
            return fig
    
    print("✅ Student labour callbacks registered successfully")

# You can also create individual callback functions if you prefer more modularity
def register_employment_callback():
    """Register only the employment chart callback"""
    @callback(
        Output('employment-chart', 'figure'),
        [
            Input('employment-view-radio', 'value'),
            Input('employment-type-dropdown', 'value'),
            Input('employment-years-dropdown', 'value')
        ]
    )
    def update_employment_chart(view_mode, employment_type, selected_years):
        try:
            from pages.ultra_safe_student_labour import create_employment_chart
            return create_employment_chart(view_mode, employment_type, selected_years)
        except Exception as e:
            print(f"❌ Employment callback error: {e}")
            fig = go.Figure()
            fig.add_annotation(text=f"Error: {str(e)}", xref="paper", yref="paper", x=0.5, y=0.5)
            return fig

def register_expense_callback():
    """Register only the expense chart callback"""
    @callback(
        Output('expense-chart', 'figure'),
        [
            Input('expense-chart-radio', 'value'),
            Input('expense-view-radio', 'value'),
            Input('expense-years-dropdown', 'value')
        ]
    )
    def update_expense_chart(chart_type, view_mode, selected_years):
        try:
            from pages.ultra_safe_student_labour import create_expense_chart
            return create_expense_chart(chart_type, view_mode, selected_years)
        except Exception as e:
            print(f"❌ Expense callback error: {e}")
            fig = go.Figure()
            fig.add_annotation(text=f"Error: {str(e)}", xref="paper", yref="paper", x=0.5, y=0.5)
            return fig

def register_monthly_expense_callback():
    """Register only the monthly expense chart callback"""
    @callback(
        Output('monthly-expense-chart', 'figure'),
        [
            Input('monthly-chart-radio', 'value'),
            Input('monthly-years-dropdown', 'value')
        ]
    )
    def update_monthly_expense_chart(chart_type, selected_years):
        try:
            from pages.ultra_safe_student_labour import create_monthly_expense_chart
            return create_monthly_expense_chart(chart_type, selected_years)
        except Exception as e:
            print(f"❌ Monthly expense callback error: {e}")
            fig = go.Figure()
            fig.add_annotation(text=f"Error: {str(e)}", xref="paper", yref="paper", x=0.5, y=0.5)
            return fig