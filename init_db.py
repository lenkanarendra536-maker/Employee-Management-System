import sqlite3

def init_db():
    conn = sqlite3.connect("company.db")
    cursor = conn.cursor()

    # Enable foreign key support
    cursor.execute("PRAGMA foreign_keys = ON")

    # ---------------- ADMIN TABLE ----------------
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS admin (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        emailid TEXT,
        username TEXT,
        password TEXT,
        role TEXT
    )
    """)

    # ---------------- EMPLOYEE TABLE ----------------
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS employee (
        eid INTEGER PRIMARY KEY AUTOINCREMENT,
        ename TEXT,
        edept TEXT,
        esalary INTEGER,
        ephone TEXT,
        id INTEGER,
        FOREIGN KEY (id) REFERENCES admin(id) ON DELETE CASCADE
    )
    """)

    conn.commit()
    conn.close()

    print("Database initialized successfully!")

if __name__ == "__main__":
    init_db()