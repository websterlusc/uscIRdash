# google_oauth_diagnostic.py
# Run this script to diagnose your Google OAuth setup

import sys


def check_google_dependencies():
    """Check if Google OAuth dependencies are installed"""
    print("=" * 60)
    print("GOOGLE OAUTH DIAGNOSTIC")
    print("=" * 60)

    try:
        from google.auth.transport import requests
        print("✅ google.auth.transport.requests - OK")
    except ImportError as e:
        print(f"❌ google.auth.transport.requests - MISSING: {e}")
        return False

    try:
        from google.oauth2 import id_token
        print("✅ google.oauth2.id_token - OK")
    except ImportError as e:
        print(f"❌ google.oauth2.id_token - MISSING: {e}")
        return False

    print("✅ All Google OAuth dependencies are installed")
    return True


def test_google_client_id():
    """Test if the Google Client ID is valid format"""
    client_id = "890006312213-jb98t4ftcjgbvalgrrbo46sl9u77e524.apps.googleusercontent.com"

    print("\n" + "-" * 40)
    print("GOOGLE CLIENT ID CHECK")
    print("-" * 40)
    print(f"Client ID: {client_id}")

    if client_id.endswith('.apps.googleusercontent.com'):
        print("✅ Client ID format looks correct")
    else:
        print("❌ Client ID format looks incorrect")

    if len(client_id) > 50:
        print("✅ Client ID length looks reasonable")
    else:
        print("❌ Client ID seems too short")


def test_token_verification():
    """Test the token verification function"""
    print("\n" + "-" * 40)
    print("TOKEN VERIFICATION FUNCTION TEST")
    print("-" * 40)

    try:
        from google.auth.transport import requests
        from google.oauth2 import id_token

        # Test with a dummy token (will fail, but should not crash)
        try:
            client_id = "890006312213-jb98t4ftcjgbvalgrrbo46sl9u77e524.apps.googleusercontent.com"
            result = id_token.verify_oauth2_token("dummy_token", requests.Request(), client_id)
            print("❌ Unexpected: dummy token was accepted")
        except ValueError as e:
            print(f"✅ Token verification correctly rejected dummy token: {e}")
        except Exception as e:
            print(f"⚠️ Unexpected error (but function exists): {e}")

    except ImportError:
        print("❌ Cannot test - missing dependencies")


def provide_installation_instructions():
    """Provide installation instructions if dependencies are missing"""
    print("\n" + "-" * 40)
    print("INSTALLATION INSTRUCTIONS")
    print("-" * 40)
    print("If any dependencies are missing, run:")
    print("pip install google-auth google-auth-oauthlib google-auth-httplib2")
    print("\nOr if using conda:")
    print("conda install -c conda-forge google-auth google-auth-oauthlib google-auth-httplib2")


def check_common_issues():
    """Check for common configuration issues"""
    print("\n" + "-" * 40)
    print("COMMON ISSUES CHECKLIST")
    print("-" * 40)

    issues = [
        "1. Google Cloud Console Setup:",
        "   - Is OAuth 2.0 enabled for your project?",
        "   - Is the client ID correctly configured?",
        "   - Are authorized domains set (localhost, your domain)?",
        "",
        "2. Network Issues:",
        "   - Can you access https://accounts.google.com from your browser?",
        "   - Is there a firewall blocking Google APIs?",
        "",
        "3. Browser Issues:",
        "   - Are third-party cookies enabled?",
        "   - Is JavaScript enabled?",
        "   - Try opening browser dev tools (F12) and check console for errors",
        "",
        "4. Local Development:",
        "   - Are you running on localhost:8050?",
        "   - Is this domain authorized in Google Cloud Console?",
        "",
        "5. Debug Steps:",
        "   - Open browser console (F12) when loading login page",
        "   - Look for messages starting with '🔍 DEBUG:'",
        "   - Check if you see 'Google button rendered successfully!'",
    ]

    for issue in issues:
        print(issue)


def main():
    """Run all diagnostic checks"""
    deps_ok = check_google_dependencies()
    test_google_client_id()

    if deps_ok:
        test_token_verification()

    provide_installation_instructions()
    check_common_issues()

    print("\n" + "=" * 60)
    print("NEXT STEPS:")
    print("=" * 60)

    if deps_ok:
        print("✅ Dependencies look good!")
        print("1. Replace your create_login_page() function with the enhanced debug version")
        print("2. Open your app and check the debug information panel")
        print("3. Open browser console (F12) and look for detailed logs")
        print("4. Try the 'Manual Google Sign-In (Debug)' button if the main button doesn't work")
    else:
        print("❌ Install missing dependencies first, then re-run this diagnostic")


if __name__ == "__main__":
    main()