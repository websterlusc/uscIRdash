#!/usr/bin/env python3
"""
USC IR Portal - Database Management Tool
Use this script to manage users, reset passwords, and view logs
"""

import sqlite3
import hashlib
import secrets
from datetime import datetime
import sys
import getpass

DATABASE = 'usc_ir_new.db'


def hash_password(password):
    """Hash password with salt"""
    salt = secrets.token_hex(16)
    password_hash = hashlib.pbkdf2_hmac('sha256',
                                        password.encode('utf-8'),
                                        salt.encode('utf-8'),
                                        100000)
    return f"{salt}:{password_hash.hex()}"


def create_admin(email, username, password, full_name):
    """Create a new admin user"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # Check if user already exists
    cursor.execute('SELECT id FROM users WHERE email = ? OR username = ?', (email, username))
    if cursor.fetchone():
        print(f"❌ User with email {email} or username {username} already exists!")
        conn.close()
        return

    password_hash = hash_password(password)

    cursor.execute('''
        INSERT INTO users (email, username, password_hash, full_name, 
                          department, position, role, is_active)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (email, username, password_hash, full_name,
          'Institutional Research', 'Administrator', 'admin', 1))

    conn.commit()
    conn.close()
    print(f"✅ Admin user '{username}' created successfully!")


def create_user(email, username, password, full_name, department, position):
    """Create a regular user"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # Check if user already exists
    cursor.execute('SELECT id FROM users WHERE email = ? OR username = ?', (email, username))
    if cursor.fetchone():
        print(f"❌ User with email {email} or username {username} already exists!")
        conn.close()
        return

    password_hash = hash_password(password)

    cursor.execute('''
        INSERT INTO users (email, username, password_hash, full_name, 
                          department, position, role, is_active)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (email, username, password_hash, full_name,
          department, position, 'user', 1))

    conn.commit()
    conn.close()
    print(f"✅ User '{username}' created successfully!")


def list_users():
    """List all users"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute('''
        SELECT id, email, username, full_name, department, position, role, is_active, last_login
        FROM users
        ORDER BY role DESC, username
    ''')

    users = cursor.fetchall()
    conn.close()

    print("\n" + "=" * 130)
    print("USER LIST - USC IR PORTAL")
    print("=" * 130)
    print(
        f"{'ID':<5} {'Email':<30} {'Username':<15} {'Name':<25} {'Dept':<20} {'Role':<10} {'Active':<8} {'Last Login':<20}")
    print("-" * 130)

    for user in users:
        active = "✅ Yes" if user[7] else "❌ No"
        last_login = user[8] if user[8] else "Never"
        role_display = f"🛡️ {user[6]}" if user[6] == 'admin' else user[6]

        print(f"{user[0]:<5} {user[1]:<30} {user[2]:<15} {user[3]:<25} "
              f"{(user[4] or 'N/A'):<20} {role_display:<10} {active:<8} {last_login:<20}")

    print("=" * 130)
    print(f"Total users: {len(users)}")


def deactivate_user(username):
    """Deactivate a user account"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute('UPDATE users SET is_active = 0 WHERE username = ?', (username,))

    if cursor.rowcount > 0:
        conn.commit()
        print(f"✅ User '{username}' deactivated successfully!")
    else:
        print(f"❌ User '{username}' not found!")

    conn.close()


def activate_user(username):
    """Activate a user account"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute('UPDATE users SET is_active = 1 WHERE username = ?', (username,))

    if cursor.rowcount > 0:
        conn.commit()
        print(f"✅ User '{username}' activated successfully!")
    else:
        print(f"❌ User '{username}' not found!")

    conn.close()


def reset_password(username, new_password):
    """Reset user password"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    password_hash = hash_password(new_password)
    cursor.execute('UPDATE users SET password_hash = ? WHERE username = ?',
                   (password_hash, username))

    if cursor.rowcount > 0:
        conn.commit()
        print(f"✅ Password for '{username}' reset successfully!")
    else:
        print(f"❌ User '{username}' not found!")

    conn.close()


def promote_to_admin(username):
    """Promote user to admin"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute('UPDATE users SET role = ? WHERE username = ?', ('admin', username))

    if cursor.rowcount > 0:
        conn.commit()
        print(f"✅ User '{username}' promoted to admin!")
    else:
        print(f"❌ User '{username}' not found!")

    conn.close()


def clear_expired_sessions():
    """Clear all expired sessions"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute('DELETE FROM sessions WHERE expires_at < ?', (datetime.now(),))
    deleted = cursor.rowcount

    conn.commit()
    conn.close()
    print(f"✅ Cleared {deleted} expired sessions")


def view_access_logs(limit=50):
    """View recent access logs"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute('''
        SELECT a.timestamp, u.username, a.action, a.details
        FROM access_logs a
        LEFT JOIN users u ON a.user_id = u.id
        ORDER BY a.timestamp DESC
        LIMIT ?
    ''', (limit,))

    logs = cursor.fetchall()
    conn.close()

    print(f"\n{'=' * 100}")
    print(f"RECENT ACCESS LOGS (Last {limit})")
    print(f"{'=' * 100}")
    print(f"{'Timestamp':<20} {'User':<15} {'Action':<15} {'Details':<50}")
    print(f"{'-' * 100}")

    for log in logs:
        timestamp = log[0] if log[0] else "Unknown"
        user = log[1] if log[1] else "System"
        action = log[2] if log[2] else "Unknown"
        details = (log[3][:47] + "...") if log[3] and len(log[3]) > 50 else (log[3] or "")

        print(f"{timestamp:<20} {user:<15} {action:<15} {details:<50}")

    print(f"{'=' * 100}")


def interactive_mode():
    """Interactive command-line interface"""
    print("\n" + "=" * 60)
    print("USC IR DATABASE MANAGEMENT - INTERACTIVE MODE")
    print("=" * 60)

    while True:
        print("\n📋 MENU:")
        print("1. List all users")
        print("2. Create admin user")
        print("3. Create regular user")
        print("4. Reset password")
        print("5. Deactivate user")
        print("6. Activate user")
        print("7. Promote to admin")
        print("8. View access logs")
        print("9. Clear expired sessions")
        print("0. Exit")

        choice = input("\nEnter choice (0-9): ")

        if choice == "0":
            print("Goodbye! 👋")
            break
        elif choice == "1":
            list_users()
        elif choice == "2":
            email = input("Email: ")
            username = input("Username: ")
            password = getpass.getpass("Password: ")
            full_name = input("Full Name: ")
            create_admin(email, username, password, full_name)
        elif choice == "3":
            email = input("Email: ")
            username = input("Username: ")
            password = getpass.getpass("Password: ")
            full_name = input("Full Name: ")
            department = input("Department: ")
            position = input("Position: ")
            create_user(email, username, password, full_name, department, position)
        elif choice == "4":
            username = input("Username to reset: ")
            new_password = getpass.getpass("New password: ")
            reset_password(username, new_password)
        elif choice == "5":
            username = input("Username to deactivate: ")
            deactivate_user(username)
        elif choice == "6":
            username = input("Username to activate: ")
            activate_user(username)
        elif choice == "7":
            username = input("Username to promote: ")
            promote_to_admin(username)
        elif choice == "8":
            limit = input("Number of logs to view (default 50): ")
            limit = int(limit) if limit else 50
            view_access_logs(limit)
        elif choice == "9":
            clear_expired_sessions()
        else:
            print("❌ Invalid choice!")


# Command-line interface
if __name__ == "__main__":
    if len(sys.argv) < 2:
        # No arguments - run interactive mode
        interactive_mode()
    else:
        command = sys.argv[1]

        if command == "list":
            list_users()
        elif command == "create-admin" and len(sys.argv) == 6:
            create_admin(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
        elif command == "create-user" and len(sys.argv) == 8:
            create_user(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6], sys.argv[7])
        elif command == "deactivate" and len(sys.argv) == 3:
            deactivate_user(sys.argv[2])
        elif command == "activate" and len(sys.argv) == 3:
            activate_user(sys.argv[2])
        elif command == "reset-password" and len(sys.argv) == 4:
            reset_password(sys.argv[2], sys.argv[3])
        elif command == "promote" and len(sys.argv) == 3:
            promote_to_admin(sys.argv[2])
        elif command == "clear-sessions":
            clear_expired_sessions()
        elif command == "logs":
            limit = int(sys.argv[2]) if len(sys.argv) > 2 else 50
            view_access_logs(limit)
        elif command == "help":
            print("""
USC IR Database Management Tool

USAGE:
    python manage_db.py                                    # Interactive mode
    python manage_db.py [command] [args]                  # Command mode

COMMANDS:
    list                                                   # List all users
    create-admin <email> <username> <password> <name>     # Create admin user
    create-user <email> <username> <password> <name> <dept> <position>  # Create regular user
    deactivate <username>                                 # Deactivate user
    activate <username>                                   # Activate user
    reset-password <username> <new_password>              # Reset password
    promote <username>                                    # Promote user to admin
    clear-sessions                                        # Clear expired sessions
    logs [limit]                                          # View access logs
    help                                                  # Show this help

EXAMPLES:
    python manage_db.py create-admin nswaby@usc.edu.tt nswaby pass123 "Nordian Swaby"
    python manage_db.py create-user john@usc.edu.tt john pass123 "John Doe" "Finance" "Analyst"
    python manage_db.py reset-password admin newpass123
    python manage_db.py list
    python manage_db.py logs 20
            """)
        else:
            print("❌ Invalid command! Use 'python manage_db.py help' for usage.")