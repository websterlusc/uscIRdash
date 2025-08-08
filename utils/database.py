import sqlite3
from datetime import datetime
import hashlib
import secrets


def init_database(db_path: str = "usc_ir.db"):
    """Initialize the database with all required tables"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            full_name TEXT NOT NULL,
            department TEXT,
            is_admin BOOLEAN DEFAULT 0,
            is_active BOOLEAN DEFAULT 1,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            last_login DATETIME
        )
    ''')

    # User sessions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT UNIQUE NOT NULL,
            user_id INTEGER NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            expires_at DATETIME NOT NULL,
            last_used DATETIME,
            ip_address TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    # Access requests table (for non-users requesting access)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS access_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            department TEXT NOT NULL,
            position TEXT NOT NULL,
            is_usc_employee BOOLEAN NOT NULL,
            access_type TEXT NOT NULL,
            justification TEXT,
            requested_duration INTEGER DEFAULT 30,
            status TEXT DEFAULT 'pending',
            approved_by INTEGER,
            approved_date DATETIME,
            approved_duration INTEGER,
            notes TEXT,
            FOREIGN KEY (approved_by) REFERENCES users (id)
        )
    ''')

    # Audit log table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS audit_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            user_id INTEGER,
            action TEXT NOT NULL,
            resource TEXT,
            details TEXT,
            ip_address TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    # System settings table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS system_settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            setting_key TEXT UNIQUE NOT NULL,
            setting_value TEXT,
            description TEXT,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_by INTEGER,
            FOREIGN KEY (updated_by) REFERENCES users (id)
        )
    ''')

    conn.commit()

    # Create default admin user if none exists
    create_default_admin(cursor)

    conn.commit()
    conn.close()


def create_default_admin(cursor):
    """Create default admin user if no admin exists"""
    # Check if any admin users exist
    cursor.execute('SELECT COUNT(*) FROM users WHERE is_admin = 1')
    admin_count = cursor.fetchone()[0]

    if admin_count == 0:
        # Create default admin
        admin_password = "admin123"  # Change this in production!
        password_hash = hash_password(admin_password)

        cursor.execute('''
            INSERT INTO users (username, password_hash, email, full_name, 
                             department, is_admin, created_at)
            VALUES (?, ?, ?, ?, ?, 1, ?)
        ''', ("admin", password_hash, "ir@usc.edu.tt", "IR Administrator",
              "Institutional Research", datetime.now()))

        print("Default admin user created:")
        print("Username: admin")
        print("Password: admin123")
        print("*** CHANGE THIS PASSWORD IMMEDIATELY! ***")


def hash_password(password: str) -> str:
    """Hash password with salt"""
    salt = secrets.token_hex(16)
    password_hash = hashlib.pbkdf2_hmac('sha256',
                                        password.encode('utf-8'),
                                        salt.encode('utf-8'),
                                        100000)
    return f"{salt}:{password_hash.hex()}"


def create_sample_users(db_path: str = "usc_ir.db"):
    """Create sample users for testing"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    sample_users = [
        {
            "username": "nswaby",
            "password": "director123",
            "email": "ir@usc.edu.tt",
            "full_name": "Nordian C. Swaby Robinson",
            "department": "Institutional Research",
            "is_admin": True
        },
        {
            "username": "lwebster",
            "password": "dev123",
            "email": "websterl@usc.edu.tt",
            "full_name": "Liam Webster",
            "department": "Institutional Research",
            "is_admin": True
        },
        {
            "username": "faculty1",
            "password": "faculty123",
            "email": "faculty@usc.edu.tt",
            "full_name": "Faculty Member",
            "department": "Academic Affairs",
            "is_admin": False
        }
    ]

    for user in sample_users:
        try:
            password_hash = hash_password(user["password"])
            cursor.execute('''
                INSERT OR IGNORE INTO users 
                (username, password_hash, email, full_name, department, is_admin, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (user["username"], password_hash, user["email"], user["full_name"],
                  user["department"], user["is_admin"], datetime.now()))
        except Exception as e:
            print(f"Error creating user {user['username']}: {e}")

    conn.commit()
    conn.close()


def setup_system_settings(db_path: str = "usc_ir.db"):
    """Setup default system settings"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    default_settings = [
        {
            "key": "site_name",
            "value": "USC Institutional Research",
            "description": "Main site name"
        },
        {
            "key": "session_timeout_hours",
            "value": "8",
            "description": "Session timeout in hours"
        },
        {
            "key": "max_login_attempts",
            "value": "5",
            "description": "Maximum login attempts before lockout"
        },
        {
            "key": "factbook_enabled",
            "value": "true",
            "description": "Enable factbook access"
        },
        {
            "key": "alumni_portal_enabled",
            "value": "true",
            "description": "Enable alumni portal access"
        }
    ]

    for setting in default_settings:
        cursor.execute('''
            INSERT OR IGNORE INTO system_settings (setting_key, setting_value, description)
            VALUES (?, ?, ?)
        ''', (setting["key"], setting["value"], setting["description"]))

    conn.commit()
    conn.close()


def log_user_action(user_id: int, action: str, resource: str = None,
                    details: str = None, ip_address: str = None,
                    db_path: str = "usc_ir.db"):
    """Log user actions for audit trail"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO audit_log (user_id, action, resource, details, ip_address)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, action, resource, details, ip_address))

        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error logging action: {e}")


def cleanup_expired_sessions(db_path: str = "usc_ir.db"):
    """Clean up expired sessions"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute('''
            DELETE FROM user_sessions 
            WHERE expires_at < datetime('now')
        ''')

        deleted_count = cursor.rowcount
        conn.commit()
        conn.close()

        if deleted_count > 0:
            print(f"Cleaned up {deleted_count} expired sessions")

    except Exception as e:
        print(f"Error cleaning up sessions: {e}")


def get_user_stats(db_path: str = "usc_ir.db") -> dict:
    """Get user statistics for admin dashboard"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Total users
        cursor.execute('SELECT COUNT(*) FROM users WHERE is_active = 1')
        total_users = cursor.fetchone()[0]

        # Admin users
        cursor.execute('SELECT COUNT(*) FROM users WHERE is_admin = 1 AND is_active = 1')
        admin_users = cursor.fetchone()[0]

        # Active sessions
        cursor.execute('''
            SELECT COUNT(*) FROM user_sessions 
            WHERE expires_at > datetime('now')
        ''')
        active_sessions = cursor.fetchone()[0]

        # Pending access requests
        cursor.execute('''
            SELECT COUNT(*) FROM access_requests 
            WHERE status = 'pending'
        ''')
        pending_requests = cursor.fetchone()[0]

        # Recent logins (last 24 hours)
        cursor.execute('''
            SELECT COUNT(*) FROM users 
            WHERE last_login > datetime('now', '-1 day')
        ''')
        recent_logins = cursor.fetchone()[0]

        conn.close()

        return {
            "total_users": total_users,
            "admin_users": admin_users,
            "active_sessions": active_sessions,
            "pending_requests": pending_requests,
            "recent_logins": recent_logins
        }

    except Exception as e:
        print(f"Error getting user stats: {e}")
        return {
            "total_users": 0,
            "admin_users": 0,
            "active_sessions": 0,
            "pending_requests": 0,
            "recent_logins": 0
        }