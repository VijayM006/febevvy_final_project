from flask import Flask, redirect, render_template, url_for, request, session
from flask_mysqldb import MySQL
import re
from flask_bcrypt import Bcrypt

App = Flask(__name__)
App.secret_key = "Vijay@006"

App.config['MYSQL_HOST'] = 'localhost'
App.config['MYSQL_USER'] = 'root'
App.config['MYSQL_PASSWORD'] = 'Vijay@006'
App.config['MYSQL_DB'] = 'final_project'
App.config["MYSQL_CURSORCLASS"] = "DictCursor"

mysql = MySQL(App)
bcrypt = Bcrypt(App)

def hash_password_check(password):
    if len(password) <= 5:
        return False
    if not re.search(r"[a-z]", password) or not re.search(r"[A-Z]", password):
        return False
    return True

@App.route("/Home")
def Home():
    return render_template("home.html")

@App.route("/Signup", methods=["GET", "POST"])
def Signup():
    if request.method == "POST":
        Email = request.form.get("email")
        Password = request.form.get("password")
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM signup WHERE email=%s", (Email,))
        data = cur.fetchone()
        cur.connection.commit()
        cur.close()
        if data:
            return "Already Email Exists"
        else:
            if not hash_password_check(Password):
                return "Check The Password Given Character"
            else:
                hash_password = bcrypt.generate_password_hash(Password).decode('utf-8')
                cur = mysql.connection.cursor()
                cur.execute("INSERT INTO signup (email, password) VALUES (%s, %s)", (Email, hash_password))
                cur.connection.commit()
                cur.close()
                return redirect(url_for('Login'))
    return render_template("signup.html")

@App.route("/", methods=["GET", "POST"])
def Login():
    if request.method == "POST":
        Email = request.form.get('email')
        Password = request.form.get('password')
        cur = mysql.connection.cursor()
        cur.execute("SELECT id, email, password FROM signup WHERE email=%s", (Email,))
        data = cur.fetchone()
        if data and bcrypt.check_password_hash(data['password'], Password):
            return redirect(url_for('Home'))
        cur.connection.commit()
        cur.close()
        
    return render_template("login.html")

@App.route("/Edit/<int:id>", methods=["GET", "POST"])
def Edit(id):
    if request.method == "POST":
        date = request.form['date']
        start_time = request.form['start_time']
        end_time = request.form['end_time']
        job_name = request.form['job_name']
        job_code = request.form['job_code']
        department = request.form['department']
        project = request.form['project']
        modules = request.form['modules']
        
        cur = mysql.connection.cursor()
        cur.execute("""
            UPDATE timesheet
            SET login_date=%s, start_time=%s, end_time=%s, job_name=%s, job_code=%s, department=%s, project=%s, modules=%s
            WHERE id=%s
        """, (date, start_time, end_time, job_name, job_code, department, project, modules, id))
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('Table'))

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM timesheet WHERE id=%s", (id,))
    data = cur.fetchone()
    cur.close()
    return render_template("edit.html", data=data)


@App.route("/Table", methods=["GET", "POST"])
def Table():
    date = session.get("login_date")
    if date:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM timesheet WHERE login_date=%s", (date,))
        data = cur.fetchall()
        cur.close()
    else:
        data = []

    if request.method == "POST":
        login_date = request.form.get("date")
        session["login_date"] = login_date
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM timesheet WHERE login_date=%s", (login_date,))
        data = cur.fetchall()
        cur.connection.commit()
        cur.close()

    return render_template("table.html", data=data)


@App.route("/Timesheet", methods=["GET", "POST"])
def Timesheet():
    if request.method == "POST":
        date = request.form.get("date")
        start_time = request.form.get("start_time")
        end_time = request.form.get("end_time")
        job_name = request.form.get("job_name")
        job_code = request.form.get("job_code")
        department = request.form.get("department")
        project = request.form.get("project")
        modules = request.form.get("modules")
        session["login_date"] = date
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO timesheet (login_date, start_time, end_time, job_name, job_code, department, project, modules) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", (date, start_time, end_time, job_name, job_code, department, project, modules))
        cur.connection.commit()
        cur.close()
        return redirect(url_for('Table'))
    
    return render_template("timesheet.html")

@App.route("/Sheet", methods=["GET", "POST"])
def Sheet():
    if request.method == "POST":
        date = request.form.get("date")
        session["login_date"] = date
        return redirect(url_for('Table'))
    return render_template("sheet.html")

@App.route("/Delete/<string:id>", methods=["GET", "POST"])
def Delete(id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM timesheet WHERE id=%s", (id,))
    cur.connection.commit()
    cur.close()
    return redirect(url_for('Table'))

if __name__ == "__main__":
    App.run(debug=True, port=2012)
