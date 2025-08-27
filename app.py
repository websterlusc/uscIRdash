#!/usr/bin/env python3
"""
USC Institutional Research Portal - Authentication Server
Standalone Flask server for handling authentication
"""

import os
from datetime import timedelta
from dotenv import load_dotenv
from flask import Flask

# Load environment variables from .env file
load_dotenv()

# Import authentication routes
from auth_routes import setup_auth_routes, create_user_session, DATABASE

# Create standalone Flask app for authentication
app = Flask(__name__)

# Configure Flask app settings
app.secret_key = os.getenv('SECRET_KEY', 'usc-ir-secret-key-2025-change-in-production')
app.permanent_session_lifetime = timedelta(days=30)

# Setup authentication routes
setup_auth_routes(app)


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


def init_database():
    """Initialize the database with required tables"""
    import sqlite3

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT,
            full_name TEXT,
            role TEXT DEFAULT 'user',
            is_active INTEGER DEFAULT 1,
            is_approved INTEGER DEFAULT 0,
            google_auth INTEGER DEFAULT 0,
            google_id TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP
        )
    ''')

    # User sessions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_token TEXT UNIQUE NOT NULL,
            user_id INTEGER NOT NULL,
            user_email TEXT NOT NULL,
            expires_at TIMESTAMP NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    conn.commit()
    conn.close()
    print("✅ Database initialized")


def main():
    """Main application entry point"""
    print("🔐 Starting USC IR Authentication Server...")

    # Initialize database
    init_database()

    # Check environment
    if not check_environment():
        print("❌ Environment check failed. Please fix configuration before running.")
        return

    print(f"🌐 Google Client ID: {os.getenv('GOOGLE_CLIENT_ID', 'NOT_SET')[:20]}...")
    print("🔧 Authentication routes configured")
    print("🏃 Starting auth server on http://localhost:5000")
    print("🔗 Login page: http://localhost:5000/login")
    print("🔧 Debug page: http://localhost:5000/debug/auth")
    print("-" * 50)

    # Run the Flask app
    app.run(
        debug=True,
        host='0.0.0.0',
        port=5000,
        threaded=True
    )


if __name__ == '__main__':
    main()