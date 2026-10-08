import sqlite3

def get_db_connection(db_name="habits.db"):
    """Establishes and returns a connection to the SQLite database."""
    conn = sqlite3.connect(db_name)
    # This setting helps retrieve database rows as dictionary-like objects
    conn.row_factory = sqlite3.Row
    return conn

def create_tables():
    """Creates the necessary database tables if they do not exist."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. Create the habits table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS habits (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        periodicity TEXT NOT NULL,
        created_at TEXT NOT NULL
    )
    """)
    
    # 2. Create the completions table to track check-offs
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS completions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        habit_id INTEGER NOT NULL,
        check_in_date TEXT NOT NULL,
        FOREIGN KEY (habit_id) REFERENCES habits (id) ON DELETE CASCADE
    )
    """)
    
    conn.commit()
    conn.close()
    print("Database tables created successfully!")

if __name__ == "__main__":
    create_tables()
