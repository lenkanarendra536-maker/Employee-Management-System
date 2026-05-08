import sqlite3
from flask import Flask, request, render_template, redirect, session,flash
import random
import smtplib
from email.mime.text import MIMEText

app = Flask(__name__)
app.secret_key = 'hello123'

# ---------------- DATABASE (SQLite) ----------------
con = sqlite3.connect("company.db", check_same_thread=False)
con.row_factory = sqlite3.Row  # enables column-name access


otp_store = {}

# ---------------- SEND OTP ----------------
def send_otp(email, otp):
    sender_email = "narendralenka553@gmail.com"
    app_password = "jjveqxphbbzentof"

    msg = MIMEText(f"Your OTP is: {otp}")
    msg['Subject'] = "OTP Verification"
    msg['From'] = sender_email
    msg['To'] = email

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(sender_email, app_password)
    server.send_message(msg)
    server.quit()


# ---------------- HOME ----------------
@app.route('/')
def Home():
    return render_template("login.html")


# ---------------- REGISTER ----------------
@app.route('/register', methods=["GET", "POST"])
def Register():

    if request.method == "POST":

        name = request.form["name"]
        emailid = request.form["emailid"]
        username = request.form["username"]
        password = request.form["password"]
        role = request.form["role"]

        cursor = con.cursor()

        # CHECK EMAIL ALREADY EXISTS

        cursor.execute(
            "SELECT * FROM admin WHERE emailid=?",
            (emailid,)
        )

        existing_email = cursor.fetchone()

        if existing_email:

            flash(
                "Email already registered!",
                "danger"
            )

            cursor.close()

            return redirect('/register')

        # CHECK USERNAME ALREADY EXISTS

        cursor.execute(
            "SELECT * FROM admin WHERE username=?",
            (username,)
        )

        existing_username = cursor.fetchone()

        if existing_username:

            flash(
                "Username already exists!",
                "warning"
            )

            cursor.close()

            return redirect('/register')

        # INSERT USER

        cursor.execute(
            """
            INSERT INTO admin
            (name,emailid,username,password,role)

            VALUES (?,?,?,?,?)
            """,

            (name, emailid, username, password, role)
        )

        con.commit()

        cursor.close()

        flash(
            "Registration successful! Please login.",
            "success"
        )

        return redirect('/login')

    return render_template("register.html")


# ---------------- LOGIN ----------------
@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        email = request.form.get('emailid')
        password = request.form.get('password')

        cursor = con.cursor()

        cursor.execute(
            "SELECT * FROM admin WHERE emailid = ? AND password = ?",
            (email, password)
        )

        user = cursor.fetchone()

        cursor.close()

        if user:
            session['admin'] = email
            flash("Login successful!", "success")
            return redirect('/dashboard')

        else:
            flash("Invalid Email or Password", "danger")
            return redirect('/login')

    return render_template('login.html')
# ---------------- FORGOT PASSWORD ----------------
@app.route("/forgot", methods=["GET", "POST"])
def forgot():

    if request.method == "POST":

        email = request.form["email"]

        cursor = con.cursor()

        cursor.execute(
            "SELECT * FROM admin WHERE emailid=?",
            (email,)
        )

        user = cursor.fetchone()

        cursor.close()

        # EMAIL EXISTS

        if user:

            otp = random.randint(100000, 999999)

            otp_store[email] = otp

            send_otp(email, otp)

            session["reset_email"] = email

            flash(
                "OTP sent successfully to your email!",
                "success"
            )

            return redirect("/verify")

        # EMAIL NOT FOUND

        flash(
            "Email not found!",
            "danger"
        )

        return redirect("/forgot")

    return render_template("forgot.html")


# ---------------- VERIFY OTP ----------------
@app.route("/verify", methods=["GET", "POST"])
def verify():

    email = session.get("reset_email")

    if not email:
        flash("Session expired. Please enter your email again.", "danger")
        return redirect("/forgot")

    if request.method == "POST":

        user_otp = request.form.get("otp")
        resend = request.form.get("resend")

        if resend:

            otp = random.randint(100000, 999999)
            otp_store[email] = otp
            send_otp(email, otp)

            flash("OTP resent successfully!", "success")
            return redirect("/verify")

        elif user_otp:

            if email in otp_store and str(otp_store[email]) == user_otp:

                flash("OTP verified successfully!", "success")
                return redirect("/reset")

            else:

                flash("Invalid OTP. Please try again.", "danger")
                return redirect("/verify")

    return render_template("verify.html")


# ---------------- RESET PASSWORD ----------------
@app.route("/reset", methods=["GET", "POST"])
def reset():

    if "reset_email" not in session:

        flash(
            "Session expired. Please try again.",
            "danger"
        )

        return redirect("/forgot")

    if request.method == "POST":

        new_password = request.form["password"]

        email = session["reset_email"]

        cursor = con.cursor()

        cursor.execute(
            "UPDATE admin SET password=? WHERE emailid=?",
            (new_password, email)
        )

        con.commit()

        cursor.close()

        session.pop("reset_email", None)

        flash(
            "Password updated successfully! Please login.",
            "success"
        )

        return redirect("/login")

    return render_template("reset.html")


# ---------------- DASHBOARD (WITH SEARCH) ----------------
@app.route('/dashboard')
def dashboard():
    if "admin" not in session:
        return redirect('/')

    search = request.args.get('search')

    cursor = con.cursor()

    if search:
        query = """
        SELECT * FROM employee 
        WHERE ename LIKE ? OR edept LIKE ? OR ephone LIKE ?
        """
        values = ("%" + search + "%", "%" + search + "%", "%" + search + "%")
        cursor.execute(query, values)
    else:
        cursor.execute("SELECT * FROM employee")

    employees = cursor.fetchall()
    cursor.close()

    return render_template("dashboard.html", employees=employees)


# ---------------- CONTACT ----------------
@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        phone = request.form["phone"]
        message = request.form["message"]

        body = f"""
New Message

Name: {name}
Email: {email}
Phone: {phone}

Message:
{message}
"""

        msg = MIMEText(body)
        msg["Subject"] = "Contact Form"
        msg["From"] = "narendralenka553@gmail.com"
        msg["To"] = "lenkanarendra536@gmail.com"

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login("narendralenka553@gmail.com", "jjveqxphbbzentof")
        server.send_message(msg)
        server.quit()

        # ✅ Flash message instead of returning text
        flash("Message sent successfully!", "success")
        return redirect("/contact")

    return render_template("contact.html")


# ---------------- VIEW EMPLOYEE ----------------
@app.route('/view')
def View():
    if "admin" not in session:
        return redirect('/')

    cursor = con.cursor()
    cursor.execute("SELECT * FROM employee")
    employees = cursor.fetchall()
    cursor.close()

    return render_template("view_emp.html", employees=employees)

@app.route('/view/<int:id>')
def single_view(id):

    if "admin" not in session:
        return redirect('/')

    cursor = con.cursor()

    cursor.execute(
        "SELECT * FROM employee WHERE eid=?",
        (id,)
    )

    employee = cursor.fetchone()

    cursor.close()

    if not employee:
        flash("Employee not found!", "danger")
        return redirect('/view')

    return render_template(
        "emp_details.html",
        employee=employee
    )


# ---------------- ABOUT ----------------
@app.route('/about')
def about():
    return render_template("about.html")


# ---------------- ADD EMPLOYEE ----------------
@app.route('/add', methods=['GET', 'POST'])
def Addemployee():

    if "admin" not in session:

        flash(
            "Please login first!",
            "danger"
        )

        return redirect('/')

    if request.method == 'POST':

        eid = request.form['eid']
        ename = request.form['ename']
        edept = request.form['edept']
        esalary = request.form['esalary']
        ephone = request.form['ephone']

        cursor = con.cursor()

        # CHECK EMPLOYEE ID EXISTS

        cursor.execute(
            "SELECT * FROM employee WHERE eid=?",
            (eid,)
        )

        existing_employee = cursor.fetchone()

        if existing_employee:

            flash(
                "Employee ID already exists!",
                "warning"
            )

            cursor.close()

            return redirect('/add')

        # INSERT EMPLOYEE

        cursor.execute(
            """
            INSERT INTO employee
            (eid,ename,edept,esalary,ephone)

            VALUES (?,?,?,?,?)
            """,

            (eid, ename, edept, esalary, ephone)
        )

        con.commit()

        cursor.close()

        flash(
            "Employee added successfully!",
            "success"
        )

        return redirect("/dashboard")

    return render_template("add_emp.html")


# ---------------- EDIT EMPLOYEE ----------------
@app.route('/edit/<eid>')
def Edit(eid):
    cursor = con.cursor()
    cursor.execute("SELECT * FROM employee WHERE eid=?", (eid,))
    emp = cursor.fetchone()
    cursor.close()

    return render_template("edit_emp.html", e=emp)


# ---------------- UPDATE EMPLOYEE ----------------
@app.route('/update', methods=['POST'])
def Update():

    if "admin" not in session:

        flash(
            "Please login first!",
            "danger"
        )

        return redirect('/')

    eid = request.form['eid']
    name = request.form['ename']
    dept = request.form['edept']
    salary = request.form['esalary']
    phone = request.form['ephone']

    cursor = con.cursor()

    cursor.execute(
        """
        UPDATE employee

        SET
        ename=?,
        edept=?,
        esalary=?,
        ephone=?

        WHERE eid=?
        """,

        (name, dept, salary, phone, eid)
    )

    con.commit()

    cursor.close()

    flash(
        "Employee updated successfully!",
        "success"
    )

    return redirect("/dashboard")


# ---------------- DELETE EMPLOYEE ----------------
@app.route('/delete/<eid>')
def Delete(eid):

    if "admin" not in session:

        flash(
            "Please login first!",
            "danger"
        )

        return redirect('/')

    cursor = con.cursor()

    # CHECK EMPLOYEE EXISTS

    cursor.execute(
        "SELECT * FROM employee WHERE eid=?",
        (eid,)
    )

    employee = cursor.fetchone()

    if not employee:

        flash(
            "Employee not found!",
            "danger"
        )

        cursor.close()

        return redirect('/dashboard')

    # DELETE EMPLOYEE

    cursor.execute(
        "DELETE FROM employee WHERE eid=?",
        (eid,)
    )

    con.commit()

    cursor.close()

    flash(
        "Employee deleted successfully!",
        "success"
    )

    return redirect('/dashboard')


# ---------------- LOGOUT ----------------
@app.route('/logout')
def Logout():

    session.pop('admin', None)

    flash(
        "Logged out successfully!",
        "success"
    )

    return redirect('/')

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(debug=True)