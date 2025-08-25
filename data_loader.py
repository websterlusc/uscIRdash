"""
Data Loading Utilities for USC Institutional Research Web App

This module provides utilities to load and process data from Excel files
for the factbook integration.
"""

import pandas as pd
import numpy as np
import os
from pathlib import Path
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataLoader:
    """Class to handle loading and processing of institutional research data"""

    def __init__(self, data_directory="data"):
        """Initialize data loader with data directory path"""
        self.data_directory = Path(data_directory)
        self.data_cache = {}

    def load_excel_file(self, filename, sheet_name=None):
        """
        Load Excel file with error handling

        Args:
            filename (str): Name of the Excel file
            sheet_name (str, optional): Specific sheet name to load

        Returns:
            dict or pd.DataFrame: Data from Excel file
        """
        try:
            file_path = self.data_directory / filename

            if not file_path.exists():
                logger.error(f"File not found: {file_path}")
                return None

            if sheet_name:
                return pd.read_excel(file_path, sheet_name=sheet_name)
            else:
                # Load all sheets
                return pd.read_excel(file_path, sheet_name=None)

        except Exception as e:
            logger.error(f"Error loading {filename}: {str(e)}")
            return None

    def load_student_labour_data(self):
        """Load student labour report data from Excel file"""
        try:
            # Load all sheets from the student labour report
            data = self.load_excel_file("student_labour_report.xlsx")

            if data is None:
                logger.info("Excel file not found, using sample data")
                return self._get_sample_student_labour_data()

            processed_data = {}

            # Process Assignment sheet
            if 'Assignment' in data:
                assignment_df = data['Assignment']
                # Clean up the data - remove any empty rows
                assignment_df = assignment_df.dropna(how='all')
                # Debug: print column names
                logger.info(f"Assignment sheet columns: {list(assignment_df.columns)}")
                processed_data['assignment'] = assignment_df

            # Process Employment sheet
            if 'Employment' in data:
                employment_df = data['Employment']
                employment_df = employment_df.dropna(how='all')
                logger.info(f"Employment sheet columns: {list(employment_df.columns)}")
                processed_data['employment'] = employment_df

            # Process Expense sheet
            if 'Expense' in data:
                expense_df = data['Expense']
                expense_df = expense_df.dropna(how='all')
                # Clean expense values - remove any formatting issues
                if len(expense_df.columns) >= 2:  # Make sure we have at least 2 columns
                    expense_col = expense_df.columns[1]  # Second column should be expense
                    expense_df[expense_col] = pd.to_numeric(
                        expense_df[expense_col].astype(str).str.replace(',', '').str.replace(' ', ''),
                        errors='coerce'
                    )
                logger.info(f"Expense sheet columns: {list(expense_df.columns)}")
                processed_data['expense'] = expense_df

            # Process Monthly Expense sheet
            if 'Monthly Expense' in data:
                monthly_df = data['Monthly Expense']
                monthly_df = monthly_df.dropna(how='all')
                # Clean numeric columns (all except first column which should be Month)
                for col in monthly_df.columns[1:]:
                    if col in monthly_df.columns:
                        monthly_df[col] = pd.to_numeric(
                            monthly_df[col].astype(str).str.replace(',', '').str.replace(' ', ''),
                            errors='coerce'
                        )
                logger.info(f"Monthly Expense sheet columns: {list(monthly_df.columns)}")
                processed_data['monthly_expense'] = monthly_df

            logger.info("Successfully processed student labour data")
            return processed_data

        except Exception as e:
            logger.error(f"Error processing student labour data: {str(e)}")
            return self._get_sample_student_labour_data()

    def _get_sample_student_labour_data(self):
        """Return sample student labour data when actual file is not available"""
        logger.info("Using sample student labour data")

        # Assignment data by schools/sites
        assignment_data = {
            'Academic Schools/Sites': [
                'Antigua Satellite Site', 'Barbados Satellite Site', 'ESL',
                'School of Business & Entrepreneurship', 'School of Education & Humanities',
                'School of Humanities', 'School of Sciences & Technology',
                'School of Social Sciences', 'School of Theology & Religion',
                'School of Graduate Studies & Research', 'Student Life',
                'Library', 'Financial Affairs', 'Campus Safety'
            ],
            '2022-2023': [1, 1, 1, 5, 7, 0, 6, 2, 1, 1, 3, 2, 1, 2],
            '2023-2024': [2, 0, 0, 7, 3, 8, 9, 3, 2, 0, 4, 3, 2, 3]
        }

        # Employment data
        employment_data = {
            'Academic Year': ['2021-2022', '2022-2023', '2023-2024'],
            'Academic Employment': [28, 36, 39],
            'Non-Academic Employment': [22, 108, 116]
        }

        # Expense data
        expense_data = {
            'Year': ['2021-2022', '2022-2023', '2023-2024'],
            'Expense': [721414.71, 1373333.33, 1134534.23]
        }

        # Monthly expense data
        monthly_expense_data = {
            'Month': ['July', 'August', 'September', 'October', 'November', 'December',
                     'January', 'February', 'March', 'April', 'May', 'June'],
            '2021-2022': [50949.25, 47256.86, 58476.7, 51800.36, 36738.53, 58476.7,
                         68476.7, 45256.86, 78476.7, 61800.36, 46738.53, 48476.7],
            '2022-2023': [67771.58, 75542.58, 120395.32, 96120.96, 83904.02, 120395.32,
                         140395.32, 85542.58, 130395.32, 106120.96, 93904.02, 110395.32],
            '2023-2024': [112032.16, 101974.89, 133529.52, 144041.99, 172862.06, 133529.52,
                         153529.52, 121974.89, 143529.52, 154041.99, 182862.06, 143529.52]
        }

        return {
            'assignment': pd.DataFrame(assignment_data),
            'employment': pd.DataFrame(employment_data),
            'expense': pd.DataFrame(expense_data),
            'monthly_expense': pd.DataFrame(monthly_expense_data)
        }

    def load_enrollment_data(self):
        """Load enrollment data from Excel files"""
        try:
            # Try to load the most recent enrollment data
            files_to_try = [

                "enrolment_data.xlsx"
            ]

            for filename in files_to_try:
                data = self.load_excel_file(filename)
                if data is not None:
                    logger.info(f"Loaded enrollment data from {filename}")
                    return data

            logger.warning("No enrollment data files found, using sample data")
            return self._get_sample_enrollment_data()

        except Exception as e:
            logger.error(f"Error loading enrollment data: {str(e)}")
            return self._get_sample_enrollment_data()

    def _get_sample_enrollment_data(self):
        """Return sample enrollment data"""
        return {
            'total_enrollment': pd.DataFrame({
                'Academic Year': ['2021-2022', '2022-2023', '2023-2024', '2024-2025'],
                'Total Students': [3410, 3130, 2778, 3110]
            })
        }

    def load_graduation_data(self):
        """Load graduation data from Excel files"""
        try:
            data = self.load_excel_file("GraduationData.xlsx")
            if data is not None:
                return data
            else:
                return self._get_sample_graduation_data()

        except Exception as e:
            logger.error(f"Error loading graduation data: {str(e)}")
            return self._get_sample_graduation_data()

    def _get_sample_graduation_data(self):
        """Return sample graduation data"""
        return {
            'graduates': pd.DataFrame({
                'Program': ['Business', 'Education', 'Sciences', 'Theology', 'Social Sciences'],
                'Graduates': [45, 32, 28, 15, 23]
            })
        }

    def load_financial_data(self):
        """Load financial data from Excel files"""
        try:
            data = self.load_excel_file("financial_data.xlsx")
            if data is not None:
                return data
            else:
                return self._get_sample_financial_data()

        except Exception as e:
            logger.error(f"Error loading financial data: {str(e)}")
            return self._get_sample_financial_data()

    def _get_sample_financial_data(self):
        """Return sample financial data"""
        return {
            'revenue': pd.DataFrame({
                'Year': ['2021-2022', '2022-2023', '2023-2024'],
                'Tuition Revenue': [15000000, 16200000, 17100000],
                'Other Revenue': [3500000, 3800000, 4200000]
            })
        }

    def get_all_available_datasets(self):
        """Get list of all available datasets"""
        datasets = []

        # Check which Excel files exist in the data directory
        if self.data_directory.exists():
            for file_path in self.data_directory.glob("*.xlsx"):
                datasets.append({
                    'filename': file_path.name,
                    'size': file_path.stat().st_size,
                    'modified': file_path.stat().st_mtime
                })

        return datasets

    def validate_data_integrity(self, data_dict):
        """Validate data integrity and return validation report"""
        report = {'valid': True, 'issues': []}

        for key, df in data_dict.items():
            if df is None or df.empty:
                report['valid'] = False
                report['issues'].append(f"Dataset '{key}' is empty or None")
                continue

            # Check for missing values
            missing_count = df.isnull().sum().sum()
            if missing_count > 0:
                report['issues'].append(f"Dataset '{key}' has {missing_count} missing values")

            # Check for duplicate rows
            if df.duplicated().any():
                duplicate_count = df.duplicated().sum()
                report['issues'].append(f"Dataset '{key}' has {duplicate_count} duplicate rows")

        return report

# Global instance for easy import
data_loader = DataLoader()