#!/usr/bin/env python3
"""
USC Institutional Research Portal
Main Application Runner with Fixed Authentication
"""

import os
import sys
from datetime import timedelta

# Add the current directory to Python path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import Dash app and Flask server
from main_app import app, server

# Import authentication routes
from auth_routes import setup_auth_routes

# Configure Flask app settings
server.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-here-change-this-in-production')
server.permanent_session_lifetime = timedelta(days=30)

# Setup authentication routes
setup_auth_routes(server)


# Environment check
def check_environment():
    """Check if required environment variables are set"""
    required_vars = ['GOOGLE_CLIENT_ID']
    missing_vars = []

    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)

    if missing_vars:
        print(f"⚠️  Missing environment variables: {', '.join(missing_vars)}")
        print("Please create a .env file with the following variables:")
        for var in missing_vars:
            print(f"   {var}=your_value_here")
        print("\nFor Google OAuth, get your client ID from: https://console.cloud.google.com/")
        return False

    print("✅ Environment variables configured")
    return True


def main():
    """Main application entry point"""
    print("🚀 Starting USC Institutional Research Portal...")

    # Check environment
    if not check_environment():
        print("❌ Environment check failed. Please fix configuration before running.")
        return

    print(f"🌐 Google Client ID: {os.getenv('GOOGLE_CLIENT_ID', 'NOT_SET')[:20]}...")
    print("🔧 Authentication routes configured")
    print("📊 Dash application ready")
    print("🏃 Starting server on http://localhost:8050")

    # Run the app
    app.run_server(
        debug=True,
        host='0.0.0.0',
        port=8050,
        dev_tools_hot_reload=True,
        dev_tools_ui=True
    )


if __name__ == '__main__':
    main()