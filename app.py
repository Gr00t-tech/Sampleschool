from flask import Flask, request, redirect, render_template, url_for, session, flash

from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = "supersecretkey"  # Needed for session handling

# -------------------------------
# Database Configuration
# -------------------------------
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///school.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# -------------------------------
# Models
# -------------------------------
class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    grade = db.Column(db.String(50), nullable=False)

class Teacher(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    teacher = db.Column(db.String(100), nullable=False)
    subject = db.Column(db.String(100), nullable=False)

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course = db.Column(db.String(100), nullable=False)
    teacher = db.Column(db.String(100), nullable=False)
    time = db.Column(db.String(50), nullable=False)

class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(50), nullable=False)

# -------------------------------
# Login Page
# -------------------------------
@app.route("/", methods=["GET"])
def login_page():
    return render_template("login.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        if username.lower() == "karisa" and password == "1234":
            session["logged_in"] = True
            session["username"] = username
            flash("Login successful!", "success")
            return redirect(url_for("new_page"))
        else:
            flash("Invalid username or password", "danger")
            return render_template("login.html")

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("login_page"))
# -------------------------------
# Reset Password Page
# -------------------------------
@app.route("/resetpwd", methods=["GET", "POST"])
def resetpwd():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        if not email:
            flash("Email is required!", "warning")
        else:
            # Later you can integrate Flask-Mail or token-based reset here
            flash(f"Password reset instructions sent to {email}", "info")
            return redirect(url_for("login_page"))
    return render_template("resetpwd.html")

# -------------------------------
# New Navigation Hub Page
# -------------------------------
@app.route("/new")
def new_page():
    if not session.get("logged_in"):
        return redirect(url_for("login_page"))
    return render_template("new.html", username=session.get("username"))

# -------------------------------
# Students Page
# -------------------------------
@app.route("/home", methods=["GET", "POST"])
def home():
    if not session.get("logged_in"):
        return redirect(url_for("login_page"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        age = request.form.get("age", "").strip()
        grade = request.form.get("grade", "").strip()

        if not name or not age or not grade:
            flash("All fields are required!", "warning")
        else:
            student = Student(name=name, age=int(age), grade=grade)
            db.session.add(student)
            db.session.commit()
            flash("Student added successfully!", "success")
        return redirect(url_for("home"))

    students = Student.query.all()
    return render_template("home.html", students=students, username=session.get("username"))

@app.route("/students/edit/<int:id>", methods=["GET", "POST"])
def edit_student(id):
    student = Student.query.get_or_404(id)
    if request.method == "POST":
        student.name = request.form.get("name", "").strip()
        student.age = int(request.form.get("age", "").strip())
        student.grade = request.form.get("grade", "").strip()
        db.session.commit()
        flash("Student updated successfully!", "success")
        return redirect(url_for("home"))
    return render_template("edit_student.html", student=student)

@app.route("/students/delete/<int:id>", methods=["POST"])
def delete_student(id):
    student = Student.query.get_or_404(id)
    db.session.delete(student)
    db.session.commit()
    flash("Student deleted successfully!", "info")
    return redirect(url_for("home"))

# -------------------------------
# Courses Page
# -------------------------------
@app.route("/courses", methods=["GET", "POST"])
def courses_page():
    if not session.get("logged_in"):
        return redirect(url_for("login_page"))

    if request.method == "POST":
        course_name = request.form.get("course", "").strip()
        teacher = request.form.get("teacher", "").strip()
        time = request.form.get("time", "").strip()

        if not course_name or not teacher or not time:
            flash("All fields are required!", "warning")
        else:
            course = Course(course=course_name, teacher=teacher, time=time)
            db.session.add(course)
            db.session.commit()
            flash("Course added successfully!", "success")
        return redirect(url_for("courses_page"))

    courses = Course.query.all()
    return render_template("courses.html", courses=courses, username=session.get("username"))

@app.route("/courses/edit/<int:id>", methods=["GET", "POST"])
def edit_course(id):
    course = Course.query.get_or_404(id)
    if request.method == "POST":
        course.course = request.form.get("course", "").strip()
        course.teacher = request.form.get("teacher", "").strip()
        course.time = request.form.get("time", "").strip()
        db.session.commit()
        flash("Course updated successfully!", "success")
        return redirect(url_for("courses_page"))
    return render_template("edit_course.html", course=course)

@app.route("/courses/delete/<int:id>", methods=["POST"])
def delete_course(id):
    course = Course.query.get_or_404(id)
    db.session.delete(course)
    db.session.commit()
    flash("Course deleted successfully!", "info")
    return redirect(url_for("courses_page"))

# -------------------------------
# Teachers Page
# -------------------------------
@app.route("/teachers", methods=["GET", "POST"])
def teachers_page():
    if not session.get("logged_in"):
        return redirect(url_for("login_page"))

    if request.method == "POST":
        teacher_name = request.form.get("teacher", "").strip()

        if not teacher_name:
            flash("Teacher is required!", "warning")
        else:
            # Look up subject for this teacher
            teacher_obj = Teacher.query.filter_by(teacher=teacher_name).first()
            if teacher_obj:
                subject = teacher_obj.subject
                new_teacher = Teacher(teacher=teacher_name, subject=subject)
                db.session.add(new_teacher)
                db.session.commit()
                flash("Teacher added successfully!", "success")
            else:
                flash("Teacher not found in database!", "danger")

        return redirect(url_for("teachers_page"))

    teachers = Teacher.query.all()
    return render_template("teachers.html", teachers=teachers, username=session.get("username"))


@app.route("/teachers/edit/<int:id>", methods=["GET", "POST"])
def edit_teacher(id):
    teacher = Teacher.query.get_or_404(id)
    if request.method == "POST":
        teacher.teacher = request.form.get("teacher", "").strip()
        teacher.subject = request.form.get("subject", "").strip()
        db.session.commit()
        flash("Teacher updated successfully!", "success")
        return redirect(url_for("teachers_page"))
    return render_template("edit_teacher.html", teacher=teacher)

@app.route("/teachers/delete/<int:id>", methods=["POST"])
def delete_teacher(id):
    teacher = Teacher.query.get_or_404(id)
    db.session.delete(teacher)
    db.session.commit()
    flash("Teacher deleted successfully!", "info")
    return redirect(url_for("teachers_page"))

# -------------------------------
# Attendance Page
# -------------------------------
@app.route("/attendance", methods=["GET", "POST"])
def attendance():
    if not session.get("logged_in"):
        return redirect(url_for("login_page"))

    if request.method == "POST":
        student = request.form.get("student", "").strip()
        status = request.form.get("status", "").strip()

        if not student or not status:
            flash("All fields are required!", "warning")
        else:
            record = Attendance(student=student, status=status)
            db.session.add(record)
            db.session.commit()
            flash("Attendance recorded successfully!", "success")
        return redirect(url_for("attendance"))

    attendance_records = Attendance.query.all()
    return render_template("attendance.html", students=Student.query.all(), attendance=attendance_records, username=session.get("username"))

@app.route("/attendance/edit/<int:id>", methods=["GET", "POST"])
def edit_attendance(id):
    record = Attendance.query.get_or_404(id)
    if request.method == "POST":
        record.student = request.form.get("student", "").strip()
        record.status = request.form.get("status", "").strip()
        db.session.commit()
        flash("Attendance updated successfully!", "success")
        return redirect(url_for("attendance"))
    return render_template("edit_attendance.html", record=record)

@app.route("/attendance/delete/<int:id>", methods=["POST"])
def delete_attendance(id):
    record = Attendance.query.get_or_404(id)
    db.session.delete(record)
    db.session.commit()
    flash("Attendance record deleted successfully!", "info")
    return redirect(url_for("attendance"))

# ✅ Entry point
if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Ensure tables are created
    app.run(debug=True, port=5005)
