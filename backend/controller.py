<<<<<<< HEAD
from flask import render_template, redirect, url_for, request, session
from .models import db, Admin, Department, Doctor, Patient, DoctorAvailability, Appointment, Treatment, ADMIN_EMAIL, ADMIN_PASSWORD
import os
from datetime import datetime, timedelta
from sqlalchemy.exc import IntegrityError

MORNING_SLOT = "10:00-14:00"
EVENING_SLOT = "16:00-20:00"

def get_next_n_dates(n):
    today = datetime.now().date()
    return [(today + timedelta(days=i)).isoformat() for i in range(n)]

def find_doctor_by_identifier(identifier):
    doctor = None
    try:
        doc_id = int(identifier)
        doctor = Doctor.query.get(doc_id)
    except Exception:
        doctor = Doctor.query.filter_by(email=identifier).first()
    return doctor


def register_routes(app):

    @app.route('/')
    def route_show_homepage():
        return redirect(url_for('route_show_signin'))

    @app.route('/signin', methods=['GET', 'POST'])
    def route_show_signin():
        if request.method == 'POST':
            email_input = request.form.get('email_or_username')
            password_input = request.form.get('password_value')
            selected_role = request.form.get('role')
            if selected_role == 'admin':
                if email_input == ADMIN_EMAIL and password_input == ADMIN_PASSWORD:
                    session.clear()
                    session['role'] = 'admin'
                    session['email'] = email_input
                    session['name'] = 'Admin'
                    return redirect(url_for('route_show_admin_dashboard'))
                return render_template('auth/signin.html', error_message='Invalid admin credentials')
            if selected_role == 'doctor':
                doctor_record = Doctor.query.filter_by(email=email_input, password=password_input).first()
                if doctor_record:
                    session.clear()
                    session['role'] = 'doctor'
                    session['doctor_id'] = doctor_record.id
                    session['email'] = doctor_record.email
                    session['name'] = doctor_record.name
                    return redirect(url_for('route_show_doctor_dashboard'))
                return render_template('auth/signin.html', error_message='Invalid doctor credentials')
            if selected_role == 'patient':
                patient_record = Patient.query.filter_by(email=email_input, password=password_input).first()
                if patient_record:
                    session.clear()
                    session['role'] = 'patient'
                    session['patient_id'] = patient_record.id
                    session['email'] = patient_record.email
                    session['name'] = patient_record.name
                    return redirect(url_for('route_show_patient_dashboard'))
                return render_template('auth/signin.html', error_message='Invalid patient credentials')
        return render_template('auth/signin.html')

    @app.route('/signup', methods=['GET', 'POST'])
    def route_show_signup():
        all_departments = Department.query.with_entities(Department.id, Department.name).all()
        if request.method == 'POST':
            name_input = request.form.get('full_name')
            email_input = request.form.get('email_address')
            password_input = request.form.get('create_password')
            role_input = request.form.get('role')
            specialization_input = request.form.get('specialization') or None
            if role_input == 'doctor':
                existing = Doctor.query.filter_by(email=email_input).first()
                if existing:
                    return render_template('auth/signup.html', error_message='Doctor email already exists', departments=all_departments)
                doctor = Doctor(name=name_input, email=email_input, password=password_input, specialization_id=specialization_input)
                try:
                    db.session.add(doctor)
                    db.session.commit()
                except IntegrityError:
                    db.session.rollback()
                return redirect(url_for('route_show_signin'))
            if role_input == 'patient':
                existing = Patient.query.filter_by(email=email_input).first()
                if existing:
                    return render_template('auth/signup.html', error_message='Patient email already exists', departments=all_departments)
                patient = Patient(name=name_input, email=email_input, password=password_input)
                try:
                    db.session.add(patient)
                    db.session.commit()
                except IntegrityError:
                    db.session.rollback()
                return redirect(url_for('route_show_signin'))
        return render_template('auth/signup.html', departments=all_departments)

    @app.route('/signout')
    def route_show_signout():
        session.clear()
        return redirect(url_for('route_show_signin'))

    @app.route('/admin/dashboard')
    def route_show_admin_dashboard():
        total_doctors = Doctor.query.count()
        total_patients = Patient.query.count()
        total_appointments = Appointment.query.count()
        return render_template('admin/dashboard.html', total_doctors=total_doctors, total_patients=total_patients, total_appointments=total_appointments)

    @app.route('/admin/doctors', methods=['GET', 'POST'])
    def route_show_admin_doctors_list():
        search_query = (request.args.get('q') or '').strip()
        if search_query:
            doctors = db.session.query(Doctor.id, Doctor.name, Doctor.email, Department.name.label('specialization'))
            doctors = doctors.outerjoin(Department, Doctor.specialization_id == Department.id).filter(Doctor.name.ilike(f"%{search_query}%"))
            doctors = doctors.all()
        else:
            doctors = db.session.query(Doctor.id, Doctor.name, Doctor.email, Department.name.label('specialization')).outerjoin(Department, Doctor.specialization_id == Department.id).all()
        departments = Department.query.with_entities(Department.id, Department.name).all()
        return render_template('admin/doctors_list.html', doctors=doctors, departments=departments, search_query=search_query)

    @app.route('/admin/doctors/add', methods=['POST'])
    def route_admin_add_doctor():
        name = request.form.get('add_name')
        email = request.form.get('add_email')
        password = request.form.get('add_password')
        specialization = request.form.get('add_specialization') or None
        doctor = Doctor(name=name, email=email, password=password, specialization_id=specialization)
        try:
            db.session.add(doctor)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
        return redirect(url_for('route_show_admin_doctors_list'))

    @app.route('/admin/doctor/<int:doctor_id>', methods=['GET', 'POST'])
    def route_show_admin_doctor_detail(doctor_id):
        doctor = Doctor.query.get(doctor_id)
        if request.method == 'POST':
            new_name = request.form.get('name')
            new_email = request.form.get('email')
            new_spec = request.form.get('specialization')
            if request.form.get('remove') == '1':
                if doctor:
                    db.session.delete(doctor)
                    db.session.commit()
                return redirect(url_for('route_show_admin_doctors_list'))
            if doctor:
                doctor.name = new_name
                doctor.email = new_email
                doctor.specialization_id = new_spec
                db.session.commit()
        departments = Department.query.with_entities(Department.id, Department.name).all()
        return render_template('admin/doctor_detail.html', doctor=doctor, departments=departments)

    @app.route('/admin/patients', methods=['GET', 'POST'])
    def route_show_admin_patients_list():
        search_query = (request.args.get('q') or '').strip()
        if search_query:
            patients = Patient.query.filter(Patient.name.ilike(f"%{search_query}%")).with_entities(Patient.id, Patient.name, Patient.email).all()
        else:
            patients = Patient.query.with_entities(Patient.id, Patient.name, Patient.email).all()
        return render_template('admin/patients_list.html', patients=patients, search_query=search_query)

    @app.route('/admin/patients/add', methods=['POST'])
    def route_admin_add_patient():
        name = request.form.get('add_name')
        email = request.form.get('add_email')
        password = request.form.get('add_password')
        patient = Patient(name=name, email=email, password=password)
        try:
            db.session.add(patient)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
        return redirect(url_for('route_show_admin_patients_list'))

    @app.route('/admin/patient/<int:patient_id>', methods=['GET', 'POST'])
    def route_show_admin_patient_detail(patient_id):
        patient = Patient.query.get(patient_id)
        if request.method == 'POST':
            new_name = request.form.get('name')
            new_email = request.form.get('email')
            if request.form.get('remove') == '1':
                if patient:
                    db.session.delete(patient)
                    db.session.commit()
                return redirect(url_for('route_show_admin_patients_list'))
            if patient:
                patient.name = new_name
                patient.email = new_email
                db.session.commit()
        treatments = db.session.query(Treatment, Appointment.appointment_date, Appointment.appointment_time, Doctor.name.label('doctor_name')).join(Appointment, Treatment.appointment_id == Appointment.id).outerjoin(Doctor, Appointment.doctor_id == Doctor.id).filter(Appointment.patient_id == patient_id).order_by(Treatment.created_at.desc()).all()
        return render_template('admin/patient_detail.html', patient=patient, treatments=treatments)

    @app.route('/admin/appointments')
    def route_show_admin_appointments_list():
        appointments = db.session.query(Appointment.id, Patient.id.label('patient_id'), Patient.name.label('patient_name'), Doctor.id.label('doctor_id'), Doctor.name.label('doctor_name'), Appointment.appointment_date, Appointment.appointment_time, Appointment.status).outerjoin(Patient, Appointment.patient_id == Patient.id).outerjoin(Doctor, Appointment.doctor_id == Doctor.id).order_by(Appointment.appointment_date, Appointment.appointment_time).all()
        return render_template('admin/appointments_list.html', appointments=appointments)

    @app.route('/admin/appointment/cancel/<int:appointment_id>', methods=['POST'])
    def route_admin_cancel_appointment(appointment_id):
        appt = Appointment.query.get(appointment_id)
        if appt and appt.status == 'Booked':
            appt.status = 'Cancelled'
            db.session.commit()
        return redirect(url_for('route_show_admin_appointments_list'))

    @app.route('/admin/departments', methods=['GET', 'POST'])
    def route_show_admin_departments():
        if request.method == 'POST':
            dept_name = request.form.get('department_name')
            dept_desc = request.form.get('department_description')
            if dept_name:
                dept = Department(name=dept_name, description=dept_desc)
                try:
                    db.session.add(dept)
                    db.session.commit()
                except IntegrityError:
                    db.session.rollback()
        departments = Department.query.with_entities(Department.id, Department.name, Department.description).all()
        return render_template('admin/departments_list.html', departments=departments)

    @app.route('/doctor/dashboard')
    def route_show_doctor_dashboard():
        doctor_id = session.get('doctor_id')
        upcoming = []
        if doctor_id:
            upcoming = db.session.query(Appointment.id, Patient.id.label('patient_id'), Patient.name.label('patient_name'), Appointment.appointment_date, Appointment.appointment_time, Appointment.status).outerjoin(Patient, Appointment.patient_id == Patient.id).filter(Appointment.doctor_id == doctor_id, Appointment.status == 'Booked').order_by(Appointment.appointment_date, Appointment.appointment_time).all()
        return render_template('doctor/dashboard.html', upcoming=upcoming)

    @app.route('/doctor/availability', methods=['GET', 'POST'])
    def route_show_doctor_availability():
        doctor_id = session.get('doctor_id')
        if not doctor_id:
            return redirect(url_for('route_show_signin'))
        if request.method == 'POST':
            date_input = request.form.get('availability_date')
            if date_input:
                try:
                    da1 = DoctorAvailability(doctor_id=doctor_id, available_date=date_input, available_time=MORNING_SLOT)
                    da2 = DoctorAvailability(doctor_id=doctor_id, available_date=date_input, available_time=EVENING_SLOT)
                    db.session.add_all([da1, da2])
                    db.session.commit()
                except IntegrityError:
                    db.session.rollback()
        avail = DoctorAvailability.query.filter_by(doctor_id=doctor_id).order_by(DoctorAvailability.available_date).with_entities(DoctorAvailability.available_date, DoctorAvailability.available_time).all()
        return render_template('doctor/availability.html', avail=avail)

    @app.route('/doctor/appointments')
    def route_show_doctor_appointments_list():
        doctor_id = session.get('doctor_id')
        appointments = []
        if doctor_id:
            appointments = db.session.query(Appointment.id, Patient.id.label('patient_id'), Patient.name.label('patient_name'), Appointment.appointment_date, Appointment.appointment_time, Appointment.status).outerjoin(Patient, Appointment.patient_id == Patient.id).filter(Appointment.doctor_id == doctor_id).order_by(Appointment.appointment_date, Appointment.appointment_time).all()
        return render_template('doctor/appointments_list.html', appointments=appointments)

    @app.route('/doctor/appointment/<int:appointment_id>', methods=['GET', 'POST'])
    def route_show_doctor_appointment_detail(appointment_id):
        doctor_id = session.get('doctor_id')
        appointment = db.session.query(Appointment, Patient.id.label('patient_id'), Patient.name.label('patient_name')).outerjoin(Patient, Appointment.patient_id == Patient.id).filter(Appointment.id == appointment_id).first()
        if request.method == 'POST':
            statusrow = Appointment.query.get(appointment_id)
            if statusrow and statusrow.status == 'Booked':
                action = request.form.get('action')
                if action in ('Completed', 'Cancelled'):
                    statusrow.status = action
                    db.session.commit()
            diagnosis = request.form.get('diagnosis')
            prescription = request.form.get('prescription')
            notes = request.form.get('doctor_notes')
            if diagnosis or prescription or notes:
                tr = Treatment(appointment_id=appointment_id, diagnosis=diagnosis, prescription=prescription, doctor_notes=notes)
                db.session.add(tr)
                db.session.commit()
            appointment = db.session.query(Appointment, Patient.id.label('patient_id'), Patient.name.label('patient_name')).outerjoin(Patient, Appointment.patient_id == Patient.id).filter(Appointment.id == appointment_id).first()
        treatments = Treatment.query.filter_by(appointment_id=appointment_id).order_by(Treatment.created_at.desc()).all()
        return render_template('doctor/appointment_detail.html', appointment=appointment, treatments=treatments)

    @app.route('/patient/dashboard')
    def route_show_patient_dashboard():
        patient_id = session.get('patient_id')
        departments = Department.query.with_entities(Department.id, Department.name).all()
        upcoming = []
        completed = []
        if patient_id:
            upcoming = Appointment.query.filter_by(patient_id=patient_id, status='Booked').order_by(Appointment.appointment_date, Appointment.appointment_time).all()
            completed = db.session.query(Appointment, Treatment.diagnosis, Treatment.prescription).outerjoin(Treatment, Appointment.id == Treatment.appointment_id).filter(Appointment.patient_id == patient_id, Appointment.status == 'Completed').order_by(Appointment.appointment_date.desc()).all()
        return render_template('patient/dashboard.html', departments=departments, upcoming=upcoming, completed=completed)

    @app.route('/patient/doctors')
    def route_show_patient_doctors_list():
        specialization_filter = request.args.get('specialization')
        departments = Department.query.with_entities(Department.id, Department.name).all()
        if specialization_filter:
            doctors = db.session.query(Doctor.id, Doctor.name, Doctor.email, Department.name.label('specialization')).outerjoin(Department, Doctor.specialization_id == Department.id).filter(Department.id == specialization_filter).all()
        else:
            doctors = db.session.query(Doctor.id, Doctor.name, Doctor.email, Department.name.label('specialization')).outerjoin(Department, Doctor.specialization_id == Department.id).all()
        return render_template('patient/doctors_list.html', doctors=doctors, departments=departments)

    @app.route('/patient/book/<int:doctor_id>', methods=['GET', 'POST'])
    def route_show_patient_book_appointment(doctor_id):
        doctor = find_doctor_by_identifier(doctor_id)
        if not doctor:
            return redirect(url_for('route_show_patient_doctors_list'))
        next7 = get_next_n_dates(7)
        availability_map = {}
        for d in next7:
            slots = [r.available_time for r in DoctorAvailability.query.filter_by(doctor_id=doctor.id, available_date=d).all()]
            slot_status = {}
            for slot in [MORNING_SLOT, EVENING_SLOT]:
                if slot in slots:
                    cnt = Appointment.query.filter_by(doctor_id=doctor.id, appointment_date=d, appointment_time=slot).count()
                    slot_status[slot] = (cnt == 0)
                else:
                    slot_status[slot] = False
            availability_map[d] = slot_status
        booked = None
        if request.method == 'POST':
            slot_choice = request.form.get('slot_choice')
            date_choice = request.form.get('date_choice')
            patient_id = session.get('patient_id')
            if not patient_id:
                return redirect(url_for('route_show_signin'))
            appt = Appointment(patient_id=patient_id, doctor_id=doctor.id, appointment_date=date_choice, appointment_time=slot_choice)
            try:
                db.session.add(appt)
                db.session.commit()
                booked = appt.id
            except IntegrityError:
                db.session.rollback()
                booked = False
        return render_template('patient/book_appointment.html', doctor=doctor, next7=next7, availability_map=availability_map, booked=booked)

    @app.route('/patient/appointments')
    def route_show_patient_appointments_list():
        patient_id = session.get('patient_id')
        appointments = []
        if patient_id:
            appointments = db.session.query(Appointment.id, Doctor.id.label('doctor_id'), Doctor.name.label('doctor_name'), Appointment.appointment_date, Appointment.appointment_time, Appointment.status).outerjoin(Doctor, Appointment.doctor_id == Doctor.id).filter(Appointment.patient_id == patient_id).order_by(Appointment.appointment_date, Appointment.appointment_time).all()
        return render_template('patient/appointments_list.html', appointments=appointments)

    @app.route('/patient/appointment/<int:appointment_id>', methods=['GET', 'POST'])
    def route_show_patient_appointment_detail(appointment_id):
        patient_id = session.get('patient_id')
        appointment = db.session.query(Appointment, Doctor.name.label('doctor_name'), Patient.name.label('patient_name')).outerjoin(Doctor, Appointment.doctor_id == Doctor.id).outerjoin(Patient, Appointment.patient_id == Patient.id).filter(Appointment.id == appointment_id).first()
        if request.method == 'POST':
            appt = Appointment.query.get(appointment_id)
            if appt and appt.status == 'Booked':
                action = request.form.get('action')
                if action == 'Cancel':
                    appt.status = 'Cancelled'
                    db.session.commit()
            appointment = db.session.query(Appointment, Doctor.name.label('doctor_name'), Patient.name.label('patient_name')).outerjoin(Doctor, Appointment.doctor_id == Doctor.id).outerjoin(Patient, Appointment.patient_id == Patient.id).filter(Appointment.id == appointment_id).first()
        treatments = Treatment.query.filter_by(appointment_id=appointment_id).order_by(Treatment.created_at.desc()).all()
        return render_template('patient/appointment_detail.html', appointment=appointment, treatments=treatments)

    @app.route('/patient/profile', methods=['GET', 'POST'])
    def route_show_patient_profile():
        patient_id = session.get('patient_id')
        if not patient_id:
            return redirect(url_for('route_show_signin'))
        patient = Patient.query.get(patient_id)
        if request.method == 'POST' and patient:
            new_name = request.form.get('name')
            new_email = request.form.get('email')
            new_password = request.form.get('password')
            patient.name = new_name
            patient.email = new_email
            patient.password = new_password
            db.session.commit()
            session['name'] = new_name
            session['email'] = new_email
        return render_template('patient/profile.html', patient=patient)
=======
from flask import Blueprint, render_template, redirect, url_for, request, session

main_blueprint = Blueprint('main_blueprint', __name__)

HARD_CODED_ADMIN_EMAIL = "admin@example.com"
HARD_CODED_ADMIN_PASSWORD = "admin123"

in_memory_patient_accounts = {}
in_memory_doctor_accounts = {}
in_memory_departments = [
    {"id": "dept1", "name": "Cardiology"},
    {"id": "dept2", "name": "Dermatology"},
    {"id": "dept3", "name": "Pediatrics"}
]

def generate_new_department_id():
    base = "dept"
    index = 1
    existing_ids = {d["id"] for d in in_memory_departments}
    while f"{base}{index}" in existing_ids:
        index += 1
    return f"{base}{index}"

@main_blueprint.route('/')
def route_show_homepage():
    return redirect(url_for('main_blueprint.route_handle_signin'))

@main_blueprint.route('/signin', methods=['GET', 'POST'])
def route_handle_signin():
    if request.method == 'POST':
        email_input = request.form.get('email_or_username')
        password_input = request.form.get('password_value')
        selected_role = request.form.get('role')
        if selected_role == 'admin':
            if email_input == HARD_CODED_ADMIN_EMAIL and password_input == HARD_CODED_ADMIN_PASSWORD:
                session.clear()
                session['role'] = 'admin'
                session['user_email'] = email_input
                return redirect(url_for('main_blueprint.route_show_admin_dashboard'))
            return render_template('auth/signin.html', error_message='Invalid admin credentials')
        if selected_role == 'doctor':
            account = in_memory_doctor_accounts.get(email_input)
            if account and account.get('password') == password_input:
                session.clear()
                session['role'] = 'doctor'
                session['user_email'] = email_input
                session['user_name'] = account.get('name')
                return redirect(url_for('main_blueprint.route_show_doctor_dashboard'))
            return render_template('auth/signin.html', error_message='Invalid doctor credentials')
        account = in_memory_patient_accounts.get(email_input)
        if account and account.get('password') == password_input:
            session.clear()
            session['role'] = 'patient'
            session['user_email'] = email_input
            session['user_name'] = account.get('name')
            return redirect(url_for('main_blueprint.route_show_patient_dashboard'))
        return render_template('auth/signin.html', error_message='Invalid patient credentials')
    return render_template('auth/signin.html')

@main_blueprint.route('/signup', methods=['GET', 'POST'])
def route_handle_signup():
    if request.method == 'POST':
        full_name = request.form.get('full_name')
        email_address = request.form.get('email_address')
        create_password = request.form.get('create_password')
        desired_role = request.form.get('role')
        selected_specialization = request.form.get('specialization')
        if desired_role == 'doctor':
            if email_address in in_memory_doctor_accounts:
                return render_template('auth/signup.html', error_message='Doctor email already exists', departments=in_memory_departments)
            in_memory_doctor_accounts[email_address] = {
                'name': full_name,
                'email': email_address,
                'password': create_password,
                'specialization_id': selected_specialization
            }
            return redirect(url_for('main_blueprint.route_handle_signin'))
        if email_address in in_memory_patient_accounts:
            return render_template('auth/signup.html', error_message='Patient email already exists', departments=in_memory_departments)
        in_memory_patient_accounts[email_address] = {
            'name': full_name,
            'email': email_address,
            'password': create_password
        }
        return redirect(url_for('main_blueprint.route_handle_signin'))
    return render_template('auth/signup.html', departments=in_memory_departments)

@main_blueprint.route('/signout')
def route_handle_signout():
    session.clear()
    return redirect(url_for('main_blueprint.route_handle_signin'))

@main_blueprint.route('/admin/dashboard')
def route_show_admin_dashboard():
    return render_template('admin/dashboard.html')

@main_blueprint.route('/admin/departments', methods=['GET', 'POST'])
def route_show_admin_departments():
    if request.method == 'POST':
        department_name = request.form.get('department_name')
        if department_name:
            new_id = generate_new_department_id()
            in_memory_departments.append({"id": new_id, "name": department_name})
    return render_template('admin/departments_list.html', departments=in_memory_departments)

@main_blueprint.route('/admin/doctors')
def route_show_admin_doctors_list():
    doctors = []
    for d in in_memory_doctor_accounts.values():
        spec_name = next((dept["name"] for dept in in_memory_departments if dept["id"] == d.get("specialization_id")), "Not set")
        doctors.append({"name": d.get("name"), "email": d.get("email"), "specialization": spec_name})
    return render_template('admin/doctors_list.html', doctors=doctors)

@main_blueprint.route('/admin/patients')
def route_show_admin_patients_list():
    patients = list(in_memory_patient_accounts.values())
    return render_template('admin/patients_list.html', patients=patients)

@main_blueprint.route('/admin/appointments')
def route_show_admin_appointments_list():
    return render_template('admin/appointments_list.html')

@main_blueprint.route('/doctor/dashboard')
def route_show_doctor_dashboard():
    return render_template('doctor/dashboard.html')

@main_blueprint.route('/doctor/availability')
def route_show_doctor_availability():
    return render_template('doctor/availability.html')

@main_blueprint.route('/doctor/appointments')
def route_show_doctor_appointments_list():
    return render_template('doctor/appointments_list.html')

@main_blueprint.route('/doctor/appointment/<appointment_id>')
def route_show_doctor_appointment_detail(appointment_id):
    return render_template('doctor/appointment_detail.html')

@main_blueprint.route('/patient/dashboard')
def route_show_patient_dashboard():
    return render_template('patient/dashboard.html')

@main_blueprint.route('/patient/doctors')
def route_show_patient_doctors_list():
    specialization_filter = request.args.get('specialization')
    doctors = []
    for d in in_memory_doctor_accounts.values():
        spec = next((dept for dept in in_memory_departments if dept["id"] == d.get("specialization_id")), None)
        spec_name = spec["name"] if spec else "Not set"
        doctors.append({"email": d.get("email"), "name": d.get("name"), "specialization_id": d.get("specialization_id"), "specialization_name": spec_name})
    if specialization_filter:
        doctors = [doc for doc in doctors if doc.get("specialization_id") == specialization_filter]
    return render_template('patient/doctors_list.html', doctors=doctors, departments=in_memory_departments)

@main_blueprint.route('/patient/book/<doctor_id>')
def route_show_patient_book_appointment(doctor_id):
    doctor = in_memory_doctor_accounts.get(doctor_id)
    return render_template('patient/book_appointment.html', doctor=doctor)

@main_blueprint.route('/patient/appointments')
def route_show_patient_appointments_list():
    return render_template('patient/appointments_list.html')

@main_blueprint.route('/patient/appointment/<appointment_id>')
def route_show_patient_appointment_detail(appointment_id):
    return render_template('patient/appointment_detail.html')
>>>>>>> 5e96f4170d4dd4c8dd2b47ffc11a27c45b5d9cbf
