import os
import sqlite3

DATABASE_PATH = os.path.join('instance', 'hospital.db')
ADMIN_EMAIL = "admin@example.com"
ADMIN_PASSWORD = "admin123"
ADMIN_FULL_NAME = "System Administrator"

def get_sqlite_connection(database_path=DATABASE_PATH):
    os.makedirs(os.path.dirname(database_path), exist_ok=True)
    connection = sqlite3.connect(database_path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON;")
    return connection

def create_tables_if_not_exists(database_path=DATABASE_PATH):
    conn = get_sqlite_connection(database_path)
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS admins (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      email TEXT UNIQUE NOT NULL,
      password TEXT NOT NULL,
      full_name TEXT
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS departments (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      name TEXT UNIQUE NOT NULL,
      description TEXT
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS doctors (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      name TEXT NOT NULL,
      email TEXT UNIQUE NOT NULL,
      password TEXT NOT NULL,
      specialization_id INTEGER,
      bio TEXT,
      blacklisted INTEGER DEFAULT 0,
      FOREIGN KEY (specialization_id) REFERENCES departments(id) ON DELETE SET NULL
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS patients (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      name TEXT NOT NULL,
      email TEXT UNIQUE NOT NULL,
      password TEXT NOT NULL,
      phone TEXT,
      age INTEGER,
      address TEXT,
      blacklisted INTEGER DEFAULT 0
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS doctor_availability (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      doctor_id INTEGER NOT NULL,
      available_date TEXT NOT NULL,
      available_time TEXT NOT NULL,
      note TEXT,
      FOREIGN KEY (doctor_id) REFERENCES doctors(id) ON DELETE CASCADE,
      UNIQUE (doctor_id, available_date, available_time)
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS appointments (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      patient_id INTEGER NOT NULL,
      doctor_id INTEGER NOT NULL,
      appointment_date TEXT NOT NULL,
      appointment_time TEXT NOT NULL,
      status TEXT NOT NULL DEFAULT 'Booked',
      notes TEXT,
      created_at TEXT DEFAULT (datetime('now')),
      FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE,
      FOREIGN KEY (doctor_id) REFERENCES doctors(id) ON DELETE CASCADE,
      UNIQUE (doctor_id, appointment_date, appointment_time)
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS treatments (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      appointment_id INTEGER NOT NULL,
      diagnosis TEXT,
      prescription TEXT,
      doctor_notes TEXT,
      created_at TEXT DEFAULT (datetime('now')),
      FOREIGN KEY (appointment_id) REFERENCES appointments(id) ON DELETE CASCADE
    );
    """)

    conn.commit()
    conn.close()

def create_admin_if_not_exists(database_path=DATABASE_PATH):
    conn = get_sqlite_connection(database_path)
    cur = conn.cursor()
    cur.execute("SELECT id FROM admins WHERE email = ?", (ADMIN_EMAIL,))
    row = cur.fetchone()
    if row is None:
        cur.execute("INSERT INTO admins (email, password, full_name) VALUES (?, ?, ?)",
                    (ADMIN_EMAIL, ADMIN_PASSWORD, ADMIN_FULL_NAME))
        conn.commit()
        result = "admin_created"
    else:
        result = "admin_exists"
    conn.close()
    return result

def initialize_database_sqlite(database_path=DATABASE_PATH):
    create_tables_if_not_exists(database_path)
    admin_status = create_admin_if_not_exists(database_path)
    return {"database_path": database_path, "admin_status": admin_status}

if __name__ == "__main__":
    result = initialize_database_sqlite()
    print("Database initialization result:", result)
