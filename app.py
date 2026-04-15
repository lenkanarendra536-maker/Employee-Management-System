from flask import Flask, request, render_template, redirect, session
import mysql.connector
import random
import smtplib
from email.mime.text import MIMEText

app = Flask(__name__)
app.secret_key = 'hello123'

# Database connection
con = mysql.connector.connect(
    host='localhost',
    user='root',
    password='171004',
    database='company'
)

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
        cursor.execute(
            "INSERT INTO admin(name,emailid,username,password,role) VALUES (%s,%s,%s,%s,%s)",
            (name, emailid, username, password, role)
        )
        con.commit()
        cursor.close()

        return redirect('/')
    return render_template("register.html")


# ---------------- LOGIN ----------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cursor = con.cursor()
        cursor.execute(
            "SELECT * FROM admin WHERE username=%s AND password=%s",
            (username, password)
        )
        user = cursor.fetchone()
        cursor.close()

        if user:
            session["admin"] = username
            return redirect("/dashboard")
        else:
            return render_template("login.html", msg="Invalid Login")

    return render_template('login.html')


# ---------------- FORGOT PASSWORD ----------------
@app.route("/forgot", methods=["GET", "POST"])
def forgot():
    if request.method == "POST":
        email = request.form["email"]

        cursor = con.cursor()
        cursor.execute("SELECT * FROM admin WHERE emailid=%s", (email,))
        user = cursor.fetchone()
        cursor.close()

        if user:
            otp = random.randint(100000, 999999)
            otp_store[email] = otp
            send_otp(email, otp)

            session["reset_email"] = email
            return redirect("/verify")

        return render_template("forgot.html", msg="Email not found")

    return render_template("forgot.html")


# ---------------- VERIFY OTP ----------------
@app.route("/verify", methods=["GET", "POST"])
def verify():
    message = ""
    email = session.get("reset_email")

    if request.method == "POST":
        user_otp = request.form.get("otp")
        resend = request.form.get("resend")

        if resend:
            otp = random.randint(100000, 999999)
            otp_store[email] = otp
            send_otp(email, otp)
            message = "OTP resent successfully"

        elif user_otp:
            if email in otp_store and str(otp_store[email]) == user_otp:
                return redirect("/reset")
            else:
                message = "Invalid OTP"

    return render_template("verify.html", msg=message)


# ---------------- RESET PASSWORD ----------------
@app.route("/reset", methods=["GET", "POST"])
def reset():
    if "reset_email" not in session:
        return redirect("/")

    if request.method == "POST":
        new_password = request.form["password"]
        email = session["reset_email"]

        cursor = con.cursor()
        cursor.execute(
            "UPDATE admin SET password=%s WHERE emailid=%s",
            (new_password, email)
        )
        con.commit()
        cursor.close()

        session.pop("reset_email", None)
        return redirect("/")

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
        WHERE ename LIKE %s OR edept LIKE %s OR ephone LIKE %s
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

        return "Message Sent Successfully"

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


# ---------------- ABOUT ----------------
@app.route('/about')
def about():
    return render_template("about.html")


# ---------------- ADD EMPLOYEE ----------------
@app.route('/add', methods=['GET', 'POST'])
def Addemployee():
    if "admin" not in session:
        return redirect('/')

    if request.method == 'POST':
        eid = request.form['eid']
        ename = request.form['ename']
        edept = request.form['edept']
        esalary = request.form['esalary']
        ephone = request.form['ephone']

        cursor = con.cursor()
        cursor.execute(
            "INSERT INTO employee (eid,ename,edept,esalary,ephone) VALUES (%s,%s,%s,%s,%s)",
            (eid, ename, edept, esalary, ephone)
        )
        con.commit()
        cursor.close()

        return redirect("/dashboard")

    return render_template("add_emp.html")


# ---------------- EDIT EMPLOYEE ----------------
@app.route('/edit/<eid>')
def Edit(eid):
    cursor = con.cursor()
    cursor.execute("SELECT * FROM employee WHERE eid=%s", (eid,))
    emp = cursor.fetchone()
    cursor.close()

    return render_template("edit_emp.html", e=emp)


# ---------------- UPDATE EMPLOYEE ----------------
@app.route('/update', methods=['POST'])
def Update():
    eid = request.form['eid']
    name = request.form['ename']
    dept = request.form['edept']
    salary = request.form['esalary']
    phone = request.form['ephone']

    cursor = con.cursor()
    cursor.execute(
        "UPDATE employee SET ename=%s, edept=%s, esalary=%s, ephone=%s WHERE eid=%s",
        (name, dept, salary, phone, eid)
    )
    con.commit()
    cursor.close()

    return redirect("/view")


# ---------------- DELETE EMPLOYEE ----------------
@app.route('/delete/<eid>')
def Delete(eid):
    cursor = con.cursor()
    cursor.execute("DELETE FROM employee WHERE eid=%s", (eid,))
    con.commit()
    cursor.close()

    return redirect('/view')


# ---------------- LOGOUT ----------------
@app.route('/logout')
def Logout():
    session.pop('admin', None)
    return redirect('/')


# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(debug=True)