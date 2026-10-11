import sqlite3

DB_PATH = "nagrikseva.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS complaints (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            citizen_name TEXT,
            description TEXT,
            detected_language TEXT,
            category TEXT,
            urgency TEXT,
            lat TEXT,
            lng TEXT,
            status TEXT DEFAULT 'Submitted'
        )
    ''')
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()