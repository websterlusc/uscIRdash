#!/usr/bin/env python3
"""
Test script to verify both servers are working
"""

import urllib.request
import urllib.error
import time
import sys

def test_server(url, name):
    """Test if a server is responding"""
    try:
        print(f"🔍 Testing {name}: {url}")
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=5) as response:
            status = response.status
            if status == 200:
                print(f"✅ {name} is working (Status: {status})")
                return True
            else:
                print(f"⚠️ {name} responded with status: {status}")
                return False
    except urllib.error.URLError as e:
        print(f"❌ {name} is not reachable: {e}")
        return False
    except Exception as e:
        print(f"❌ Error testing {name}: {e}")
        return False

def main():
    """Test both servers"""
    print("🧪 USC IR Server Test")
    print("=" * 40)
    
    # Test auth server
    auth_working = test_server("http://localhost:5000/debug/auth", "Auth Server")
    
    # Test login page specifically
    login_working = test_server("http://localhost:5000/login", "Login Page")
    
    # Test main app
    main_working = test_server("http://localhost:8050/", "Main App")
    
    print("\n" + "=" * 40)
    print("📊 Test Results:")
    print(f"   Auth Server: {'✅ Working' if auth_working else '❌ Not Working'}")
    print(f"   Login Page:  {'✅ Working' if login_working else '❌ Not Working'}")
    print(f"   Main App:    {'✅ Working' if main_working else '❌ Not Working'}")
    
    if all([auth_working, login_working, main_working]):
        print("\n🎉 All servers are working!")
        print("🔗 Try these URLs:")
        print("   Main App: http://localhost:8050/")
        print("   Login: http://localhost:5000/login")
        print("   Debug: http://localhost:5000/debug/auth")
    else:
        print("\n❌ Some servers are not working")
        print("💡 Make sure to start:")
        print("   1. Auth server: python app.py")
        print("   2. Main app: python main_app.py")

if __name__ == "__main__":
    main()
