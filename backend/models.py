import os
<<<<<<< HEAD
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
=======
import sqlite3
>>>>>>> 5e96f4170d4dd4c8dd2b47ffc11a27c45b5d9cbf

DATABASE_PATH = os.path.join('instance', 'hospital.db')
ADMIN_EMAIL = "admin@example.com"
ADMIN_PASSWORD = "admin123"
ADMIN_FULL_NAME = "System Administrator"

<<<<<<< HEAD
db = SQLAlchemy()

class Admin(db.Model):
  __tablename__ = 'admins'
  id = db.Column(db.Integer, primary_key=True)
  email = db.Column(db.String, unique=True, nullable=False)
  password = db.Column(db.String, nullable=False)
  full_name = db.Column(db.String)


class Department(db.Model):
  __tablename__ = 'departments'
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String, unique=True, nullable=False)
  description = db.Column(db.String)
  doctors = db.relationship('Doctor', backref='specialization_obj', lazy='dynamic', passive_deletes=True)


class Doctor(db.Model):
  __tablename__ = 'doctors'
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String, nullable=False)
  email = db.Column(db.String, unique=True, nullable=False)
  password = db.Column(db.String, nullable=False)
  specialization_id = db.Column(db.Integer, db.ForeignKey('departments.id', ondelete='SET NULL'))
  bio = db.Column(db.Text)
  blacklisted = db.Column(db.Integer, default=0)
  appointments = db.relationship('Appointment', backref='doctor_obj', lazy='dynamic', passive_deletes=True)
  availabilities = db.relationship('DoctorAvailability', backref='doctor_obj', cascade='all, delete-orphan', passive_deletes=True)


class Patient(db.Model):
  __tablename__ = 'patients'
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String, nullable=False)
  email = db.Column(db.String, unique=True, nullable=False)
  password = db.Column(db.String, nullable=False)
  phone = db.Column(db.String)
  age = db.Column(db.Integer)
  address = db.Column(db.String)
  blacklisted = db.Column(db.Integer, default=0)
  appointments = db.relationship('Appointment', backref='patient_obj', lazy='dynamic', passive_deletes=True)


class DoctorAvailability(db.Model):
  __tablename__ = 'doctor_availability'
  id = db.Column(db.Integer, primary_key=True)
  doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id', ondelete='CASCADE'), nullable=False)
  available_date = db.Column(db.String, nullable=False)
  available_time = db.Column(db.String, nullable=False)
  note = db.Column(db.Text)
  __table_args__ = (db.UniqueConstraint('doctor_id', 'available_date', 'available_time', name='uix_availability'),)


class Appointment(db.Model):
  __tablename__ = 'appointments'
  id = db.Column(db.Integer, primary_key=True)
  patient_id = db.Column(db.Integer, db.ForeignKey('patients.id', ondelete='CASCADE'), nullable=False)
  doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id', ondelete='CASCADE'), nullable=False)
  appointment_date = db.Column(db.String, nullable=False)
  appointment_time = db.Column(db.String, nullable=False)
  status = db.Column(db.String, nullable=False, default='Booked')
  notes = db.Column(db.Text)
  created_at = db.Column(db.DateTime, server_default=db.func.current_timestamp())
  __table_args__ = (db.UniqueConstraint('doctor_id', 'appointment_date', 'appointment_time', name='uix_appointment'),)
  treatments = db.relationship('Treatment', backref='appointment_obj', cascade='all, delete-orphan', passive_deletes=True)


class Treatment(db.Model):
  __tablename__ = 'treatments'
  id = db.Column(db.Integer, primary_key=True)
  appointment_id = db.Column(db.Integer, db.ForeignKey('appointments.id', ondelete='CASCADE'), nullable=False)
  diagnosis = db.Column(db.Text)
  prescription = db.Column(db.Text)
  doctor_notes = db.Column(db.Text)
  created_at = db.Column(db.DateTime, server_default=db.func.current_timestamp())


def _make_app_for_db(database_path):
  os.makedirs(os.path.dirname(database_path), exist_ok=True)
  app = Flask(__name__, instance_relative_config=True)
  app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.abspath(database_path)}"
  app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
  return app


def create_tables_if_not_exists(database_path=DATABASE_PATH):
  app = _make_app_for_db(database_path)
  db.init_app(app)
  with app.app_context():
    db.create_all()


def create_admin_if_not_exists(database_path=DATABASE_PATH):
  app = _make_app_for_db(database_path)
  db.init_app(app)
  with app.app_context():
    existing = Admin.query.filter_by(email=ADMIN_EMAIL).first()
    if existing is None:
      admin = Admin(email=ADMIN_EMAIL, password=ADMIN_PASSWORD, full_name=ADMIN_FULL_NAME)
      db.session.add(admin)
      db.session.commit()
      return "admin_created"
    else:
      return "admin_exists"


def initialize_database_sqlite(database_path=DATABASE_PATH):
  create_tables_if_not_exists(database_path)
  status = create_admin_if_not_exists(database_path)
  return {"database_path": database_path, "admin_status": status}


if __name__ == "__main__":
  print(initialize_database_sqlite())
=======
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
>>>>>>> 5e96f4170d4dd4c8dd2b47ffc11a27c45b5d9cbf
