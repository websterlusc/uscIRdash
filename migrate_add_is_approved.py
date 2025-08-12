import sqlite3

DATABASE = 'path_to_your_db_file.db'  # change this to your actual DB path

def migrate():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    try:
        cursor.execute("ALTER TABLE users ADD COLUMN is_approved INTEGER DEFAULT 0;")
        print("Column 'is_approved' added successfully.")
    except sqlite3.OperationalError as e:
        print(f"Migration error: {e}")
    finally:
        conn.commit()
        conn.close()

if __name__ == '__main__':
    migrate()

