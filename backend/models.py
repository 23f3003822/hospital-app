import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

DATABASE_PATH = os.path.join('instance', 'hospital.db')
ADMIN_EMAIL = "admin@example.com"
ADMIN_PASSWORD = "admin123"
ADMIN_FULL_NAME = "System Administrator"

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
