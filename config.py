import os
from datetime import timedelta

# USC Brand Colors
USC_COLORS = {
    'primary_green': '#1B5E20',
    'secondary_green': '#4CAF50',
    'accent_yellow': '#FDD835',
    'white': '#FFFFFF',
    'light_gray': '#F5F5F5',
    'dark_gray': '#424242',
    'text_gray': '#666666'
}

# Base URL Configuration
def get_base_url():
    """Get the base URL for links (local vs deployed)"""
    if os.environ.get('RENDER'):
        return "https://uscir.onrender.com"
    else:
        return "http://127.0.0.1"

BASE_URL = get_base_url()

# Database Configuration
DATABASE_CONFIG = {
    'path': 'usc_ir.db',
    'backup_interval_hours': 24,
    'cleanup_expired_sessions_hours': 1
}

# Authentication Configuration
AUTH_CONFIG = {
    'session_duration_hours': 8,
    'max_login_attempts': 5,
    'lockout_duration_minutes': 30,
    'password_min_length': 8,
    'require_strong_passwords': True
}

# Email Configuration
EMAIL_CONFIG = {
    'smtp_server': 'smtp.gmail.com',
    'smtp_port': 587,
    'sender_email': 'ir@usc.edu.tt',
    'sender_name': 'USC Institutional Research',
    'use_tls': True
}

# Application Configuration
APP_CONFIG = {
    'debug': not os.environ.get('RENDER'),
    'port': int(os.environ.get('PORT', 8050)),
    'host': '0.0.0.0',
    'title': 'USC Institutional Research',
    'description': 'University of the Southern Caribbean Institutional Research Portal',
    'version': '2.0.0'
}

# Feature Flags
FEATURES = {
    'factbook_enabled': True,
    'alumni_portal_enabled': True,
    'user_registration': False,  # Disable public registration
    'password_reset': True,
    'audit_logging': True,
    'session_monitoring': True
}

# File Upload Configuration
UPLOAD_CONFIG = {
    'max_file_size_mb': 50,
    'allowed_extensions': ['.xlsx', '.xls', '.csv', '.pdf', '.png', '.jpg'],
    'upload_folder': 'uploads',
    'temp_folder': 'temp'
}

# Analytics Configuration
ANALYTICS_CONFIG = {
    'google_analytics_id': None,  # Add if needed
    'track_page_views': True,
    'track_user_actions': True,
    'retention_days': 365
}

# Security Configuration
SECURITY_CONFIG = {
    'enable_csrf_protection': True,
    'secure_cookies': os.environ.get('RENDER') is not None,
    'content_security_policy': True,
    'rate_limiting': True,
    'max_requests_per_minute': 60
}

# System Maintenance
MAINTENANCE_CONFIG = {
    'maintenance_mode': False,
    'maintenance_message': 'System under maintenance. Please try again later.',
    'allowed_ips_during_maintenance': ['127.0.0.1']
}

# Default User Roles and Permissions
USER_ROLES = {
    'admin': {
        'name': 'Administrator',
        'permissions': [
            'user_management',
            'system_settings',
            'data_management',
            'audit_logs',
            'backup_restore',
            'factbook_access',
            'alumni_portal_access'
        ]
    },
    'ir_staff': {
        'name': 'IR Staff',
        'permissions': [
            'data_management',
            'factbook_access',
            'alumni_portal_access',
            'generate_reports'
        ]
    },
    'faculty': {
        'name': 'Faculty',
        'permissions': [
            'factbook_access',
            'basic_reports'
        ]
    },
    'staff': {
        'name': 'Staff',
        'permissions': [
            'factbook_access'
        ]
    },
    'external': {
        'name': 'External User',
        'permissions': [
            'limited_factbook_access'
        ]
    }
}

# Data Export Settings
EXPORT_CONFIG = {
    'formats': ['xlsx', 'csv', 'pdf'],
    'max_export_rows': 10000,
    'include_metadata': True,
    'watermark_exports': True
}

# Notification Settings
NOTIFICATION_CONFIG = {
    'email_notifications': True,
    'admin_notifications': [
        'new_access_requests',
        'system_errors',
        'security_alerts',
        'backup_status'
    ],
    'user_notifications': [
        'access_granted',
        'access_expired',
        'password_changed'
    ]
}

# API Configuration (for future integration)
API_CONFIG = {
    'enable_api': False,
    'api_version': 'v1',
    'rate_limit_per_hour': 1000,
    'require_api_key': True
}

# Logging Configuration
LOGGING_CONFIG = {
    'level': 'INFO',
    'file_path': 'logs/usc_ir.log',
    'max_file_size_mb': 10,
    'backup_count': 5,
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
}