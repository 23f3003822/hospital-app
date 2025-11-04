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
