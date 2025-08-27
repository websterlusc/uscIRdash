#!/usr/bin/env python3
"""
USC Institutional Research - Server Startup Script
This script helps start both the auth server and main app properly
"""

import subprocess
import sys
import time
import os
import signal
from threading import Thread


def start_auth_server():
    """Start the authentication server"""
    print("🔐 Starting Authentication Server...")
    try:
        # Start auth server
        auth_process = subprocess.Popen([
            sys.executable, 'app.py'
        ], cwd='.', stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

        # Monitor output
        for line in iter(auth_process.stdout.readline, ''):
            if line.strip():
                print(f"[AUTH] {line.strip()}")

        return auth_process
    except Exception as e:
        print(f"❌ Failed to start auth server: {e}")
        return None


def start_main_app():
    """Start the main Dash application"""
    print("📊 Starting Main Application...")
    try:
        # Wait a moment for auth server to start
        time.sleep(3)

        # Start main app
        main_process = subprocess.Popen([
            sys.executable, 'main_app.py'
        ], cwd='.', stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

        # Monitor output
        for line in iter(main_process.stdout.readline, ''):
            if line.strip():
                print(f"[MAIN] {line.strip()}")

        return main_process
    except Exception as e:
        print(f"❌ Failed to start main app: {e}")
        return None


def check_prerequisites():
    """Check if all required files exist"""
    required_files = [
        'main_app.py',
        'app.py',
        'auth_routes.py',
        'login.html',
        '.env'
    ]

    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)

    if missing_files:
        print("❌ Missing required files:")
        for file in missing_files:
            print(f"   - {file}")
        return False

    print("✅ All required files found")
    return True


def main():
    """Main startup function"""
    print("🚀 USC IR Portal Startup")
    print("=" * 50)

    # Check prerequisites
    if not check_prerequisites():
        print("\n❌ Please ensure all required files are present")
        return

    print("\n📋 Starting Services...")
    print("   Auth Server: http://localhost:5000")
    print("   Main App: http://localhost:8050")
    print("   Login: http://localhost:5000/login")
    print()

    # Start both servers
    try:
        # Start auth server in background
        auth_thread = Thread(target=start_auth_server, daemon=True)
        auth_thread.start()

        # Start main app (this will block)
        start_main_app()

    except KeyboardInterrupt:
        print("\n🛑 Shutting down servers...")
        print("✅ Servers stopped")


if __name__ == "__main__":
    main()