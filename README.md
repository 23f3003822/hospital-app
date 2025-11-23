# 🏥 Hospital Management System 🏨

This project is a **web-based hospital management application** designed to streamline and simplify interactions between **patients, doctors, and administrators**. It handles doctor management, appointment booking, treatment updates, and patient history — all in one unified platform.

---

## 🔧 Technologies Used

- **Python** (Flask Framework)
- **HTML5, CSS3, Bootstrap 5** for responsive UI
- **SQLite** for lightweight database management
- **SQLAlchemy ORM** for database models
- **Jinja2** templating engine for dynamic rendering
- **Session Management** for role-based login (Admin / Doctor / Patient)

---

## 🎯 Project Objective

> The main goal is to develop an **efficient and user-friendly hospital management system** that:
> - Reduces manual workload for hospital staff
> - Simplifies appointment scheduling for patients
> - Helps doctors manage visits and update treatment details
> - Maintains complete medical history for every patient
> - Ensures smooth and secure role-based access

---

## 🧑‍💻 Features

### 🧍 Patient Side
- Patient Registration & Login
- View available doctors and specializations
- Check doctor availability
- Book, reschedule, or cancel appointments
- View appointment history
- Access diagnosis, prescriptions, and treatment notes
- Edit personal profile

### 👨‍⚕️ Doctor Side
- Doctor Login
- View daily & weekly appointments
- Mark appointments as Completed or Cancelled
- Add diagnosis, prescriptions, and treatment notes
- View complete patient history for better consultation

### 👨‍💼 Admin Side
- Pre-created Admin login
- Add, edit, or delete doctor profiles
- View all appointments (upcoming & past)
- Search doctors or patients by name/specialization
- Manage doctor availability

---

## 🚀 How to Run Locally

1. **Clone the repository**  
   ```bash
   git clone https://github.com/23f3003822/hospital-app.git
   cd hospital-app

2. **Install required dependencies**
   ```bash
   pip install -r requirements.txt

3. **Run the application**
   ```bash
   python app.py

4. **Open the app in your browser**
   ```
   http://127.0.0.1:5000
