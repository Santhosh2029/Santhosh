from flask import Flask, render_template, request, url_for, redirect, abort, session
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
import psycopg2
import bcrypt
from cryptography.fernet import Fernet
import json
from flask import jsonify
import string
import smtplib
import random
import mailtrap as mt
from flask_mail import Mail, Message
import os



password = 'Otsi@123'
# giving connection to the database
def connect_to_db():
    conn = psycopg2.connect(host='localhost',
                            database="postgres",
                            user="postgres",
                            password="Otsi@123")
    return conn

#create flask app
app = Flask(__name__)
app.secret_key = os.urandom(24)  # Set a secret key
# app.config['SECRET_KEY']  = os.urandom(24)



# Configure Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'sunnyprince9533@gmail.com'
app.config['MAIL_PASSWORD'] = 'hctadxyjyvgjbqoy'

mail = Mail(app)

#configuring the database
app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://postgres:{password}@localhost:5432/postgres'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# app.config['SESSION_TYPE'] = 'sqlalchemy'

# Session(app)
#Installing SQLAlchemy
db = SQLAlchemy(app)


@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('login.html')

# For Login 

@app.route('/after_login', methods=['GET','POST'])
def after_login():
    if request.method == 'POST':
        email = request.form['username']
        password = request.form['password']

        con = connect_to_db()
        cur = con.cursor()
        query = f'''SELECT "Password" FROM public.user_authent WHERE "Mail Id"= '{email}' '''
        cur.execute(query)
        hash_password = cur.fetchone()[0]
        # Convert the hash_password from hexadecimal to bytes
        hash_bytes = bytes.fromhex(hash_password[2:])


        # Compare the hashed password with the provided password
        if bcrypt.checkpw(password.encode('utf-8'), hash_bytes):
            # return render_template('home.html',username = email)
            session['username'] = email
            return redirect('/home')
        else:
            return render_template('login.html')

    return render_template('login.html')

#forgot password
@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    return render_template('otp_send.html')

@app.route('/send_otp', methods=['GET', 'POST'])
def send_otp():
    mail_address = request.form['email']

    con = connect_to_db()
    cur = con.cursor()
    query = f'SELECT COUNT(*) FROM public.user_authent WHERE "Mail Id" = \'{mail_address}\''
    cur.execute(query)
    count = cur.fetchall()[0][0]
    
    if count == 1:
        otp = generate_otp()
        save_otp(mail_address, otp)
        send_email(mail_address, otp)
        return render_template('enterotp.html',mail_address=mail_address)
    else:
        return 'Email not found'

def generate_otp():
    # Generate a random 4-digit OTP
    digits = string.digits
    otp = ''.join(random.choice(digits) for _ in range(4))
    return otp

def save_otp(mail_address, otp):
    con = connect_to_db()
    cur = con.cursor()
    query = f'UPDATE public.user_authent SET "OTP" = \'{otp}\' WHERE "Mail Id" = \'{mail_address}\''
    cur.execute(query)
    con.commit()
    cur.close()
    con.close()

def send_email(mail_address, otp):
    smtp_server = app.config['MAIL_SERVER']
    smtp_port = app.config['MAIL_PORT']
    smtp_username = app.config['MAIL_USERNAME']
    smtp_password = app.config['MAIL_PASSWORD']

    subject = 'OTP Verification'
    message = f'Your OTP is: {otp}'

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_username, smtp_password)
            msg = Message(subject=subject,
                          sender=smtp_username,
                          recipients=[mail_address])
            msg.body = message
            mail.send(msg)
        print('Email sent successfully')
    except Exception as e:
        print(f'Error while sending email: {e}')


@app.route('/after_enter_otp', methods=['GET','POST'])
def after_enter_otp():
    otp = request.form['otp']
    mail = request.args.get('mail')

    con = connect_to_db()
    cur = con.cursor()
    query = f'SELECT * FROM public.user_authent WHERE "Mail Id" = \'{mail}\''
    cur.execute(query)
    rec = cur.fetchall()
    con.commit()
    cur.close()
    con.close()
    db_otp = str(rec[0][-1])

    if db_otp == otp:
        return render_template('enter_new_password.html')
    else:
        return render_template('otp_send.html', mail = mail)

@app.route('/reset_password', methods = ['GET','POST'])
def reset_password():
    password1 = request.form['confirm_password']
    password2 = request.form['new_password']
    mail = request.args.get('mail')

    if password1 == password2:
        hashed_password = bcrypt.hashpw(password1.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        con = connect_to_db()
        cur = con.cursor()
        query = f'''UPDATE public.user_authent SET "Password" = '{hashed_password}' WHERE "Mail Id" = '{mail}' '''
        cur.execute(query)
        con.commit()
        cur.close()
        con.close()
        return render_template('login.html')
    else:
        return render_template('otp_send.html')

       


# For Rigistration

@app.route('/register',methods = ['GET','POST'])
def register():
    return render_template('rigistration.html')

@app.route('/after_register', methods=['GET','POST'])
def after_register():
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    username = request.form['username']
    email = request.form['email']
    password = request.form['password']
    confirm_password = request.form['confirm_password']

    if password == confirm_password:
        #hashing password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        con = connect_to_db()
        cur = con.cursor()
        query = "INSERT INTO public.user_authent( \"First Name\", \"Last Name\", \"User Name\", \"Mail Id\", \"Password\") VALUES ( %s, %s, %s, %s, %s)"
        cur.execute(query, (first_name, last_name, username, email, hashed_password))
        con.commit()
        cur.close()
        con.close()
        
        print('Registered successfully')
        return redirect(url_for('login'))
    else:
        print('Entered details are not correct')
        return render_template('registration.html')
    

# To go to Home page 

@app.route('/home')
def home():
    # username = request.args.get('username')
    return render_template('home.html',username = session.get('username'))


# To get the information of the students in the class

@app.route('/student_info', methods=['GET','POST'])
def student_info():

    classs = request.form['class_info']
    # username = request.args.get('username')

    con = connect_to_db()
    cur = con.cursor()
    query = f'SELECT * FROM public.example_students WHERE "Class" = \'{classs}\' ORDER BY "Roll No"'
    cur.execute(query)
    students = cur.fetchall()
    con.commit()
    cur.close()
    con.close()
    return render_template('stud_info.html', students=students, result=classs,username = session.get('username'))

#To Record new student information
@app.route('/student_info_update', methods = ['GET','POST'])
def student_info_update():
    # username = request.args.get('username')
    return render_template('stud_info_update_form.html',username = session.get('username'))

@app.route('/after_student_info_update', methods = ['GET','POST'])
def after_student_info_update():
    classs = request.form['class_info']
    rollNo = request.form['rollNo']
    studentName = request.form['studentName']
    section = request.form['section']
    fatherName = request.form['fatherName']
    motherName = request.form['motherName']
    username = request.args.get('username')


    con = connect_to_db()
    cur = con.cursor()
    query = "INSERT INTO public.example_students( \"Class\", \"Roll No\", \"Student Name\", \"Section\", \"Father Name\", \"Mother Name\") VALUES ( %s, %s, %s, %s, %s, %s)"
    cur.execute(query,(classs, rollNo, studentName, section, fatherName, motherName))
    con.commit()
    cur.close()
    con.close()
     # Retrieve the updated student information after the update
    con = connect_to_db()
    cur = con.cursor()

    query = f'SELECT * FROM public.example_students WHERE "Class" = \'{classs}\''
    cur.execute(query)
    students = cur.fetchall()

    cur.close()
    con.close()

    return render_template('stud_info.html', students=students, result=classs,username = session.get('username'))

#To edit the exisisting Students information.
@app.route('/student_info_edit')
def student_info_edit():
    username = request.args.get('username')
    classs = request.args.get('class_info')
    con = connect_to_db()
    cur = con.cursor()
    query = f'SELECT * FROM public.example_students WHERE "Class" = \'{classs}\''
    cur.execute(query)
    students = cur.fetchall()
    con.commit()
    cur.close()
    con.close()
    return render_template('student_info_edit.html', students=students, result=classs, username=session.get('username'))
    

@app.route('/after_student_info_edit', methods=['POST', 'GET'])
def after_student_info_edit():
    classs = request.args.get('class_info')
    edited_data = request.form['edited-data']
    edited_rows = json.loads(edited_data)

    for i in edited_rows:
        con = connect_to_db()
        cur = con.cursor()

        rollNo = i['0']
        studentName = i['1']
        section = i['2']
        fatherName = i['3']
        motherName = i['4']

        query = "UPDATE public.example_students SET \"Class\" = %s,\"Roll No\" = %s, \"Student Name\" = %s, \"Section\" = %s, \"Father Name\" = %s, \"Mother Name\" = %s WHERE \"Roll No\" = %s"
        values = (classs,rollNo, studentName, section, fatherName, motherName, rollNo)
        cur.execute(query, values)
        con.commit()
        cur.close()
        con.close()

    # Retrieve the updated student information after the update
    con = connect_to_db()
    cur = con.cursor()

    query = f'SELECT * FROM public.example_students WHERE "Class" = \'{classs}\''
    cur.execute(query)
    students = cur.fetchall()

    cur.close()
    con.close()

    return render_template('stud_info.html', students=students, result=classs,username = session.get('username'))


# To delete the Existing students information.
@app.route('/student_info_delete', methods=['GET','POST'])
def student_info_delete():
    classs = request.form['class_info']
    con = connect_to_db()
    cur = con.cursor()
    query = f'SELECT * FROM public.example_students WHERE "Class" = \'{classs}\''
    cur.execute(query)
    students = cur.fetchall()
    con.commit()
    cur.close()
    con.close()
    

    return render_template('select_delete_info.html', students=students, result=classs,username = session.get('username'))

@app.route('/after_selecting_delte_info', methods=['GET', 'POST'])
def after_selecting_delte_info():
    selected_rows = request.form.getlist('rollNo')
    selected_rows = selected_rows = ', '.join([f"'{row}'" for row in selected_rows])

    con = connect_to_db()
    cur = con.cursor()

    # Delete the selected rows from the database
    query = f'DELETE FROM public.example_students WHERE "Roll No" IN ({selected_rows})'
    cur.execute(query)
    

    # Retrieve the updated student information after deletion
    classs = request.form['class_info']
    query = f'SELECT * FROM public.example_students WHERE "Class" = \'{classs}\''
    cur.execute(query)
    students = cur.fetchall()

    con.commit()
    cur.close()
    con.close()
    return render_template('stud_info.html', students=students, result=classs,username = session.get('username'))


@app.route('/academicinfo')
def academicinfo():
    return render_template('marks_page.html')

@app.route('/view_marks', methods=['GET', 'POST'])
def view_marks():
    classs = int(request.form['class'])
    exam_type = request.form['exam_type']
    
    con = connect_to_db()
    cur = con.cursor()
    query = f"SELECT * FROM student_marks WHERE class = {classs} AND exam_Type = '{exam_type}'"

    cur.execute(query)
    data = cur.fetchall()
    con.commit()
    cur.close()
    con.close()

    return render_template('view_marks.html', data = data, classs = classs,exam_type = exam_type,username = session.get('username'))

@app.route('/add_marks',methods=['GET'])
def add_marks():
    return render_template('add_marks.html')

@app.route('/after_add_marks', methods=['POST'])
def after_add_marks():
    classs = int(request.form['class'])
    rollNo = int(request.form['rollNo'])
    section = request.form['section']
    exam_type = request.form['exam_type']
    studentName = request.form['studentName']
    telugu = request.form['telugu']
    english = request.form['english']
    mathematics = request.form['mathematics']
    science = request.form['science']
    social = request.form['social']


    # insert the data to table
    conn = connect_to_db()
    cur = conn.cursor()
    query = 'INSERT INTO public.student_marks("class", "roll_no", "exam_type", "student_name", "section", "telugu", "english", "mathematics", "science", "social") VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
    values = (classs, rollNo, exam_type, studentName, section, telugu, english, mathematics, science, social)
    cur.execute(query, values)
    conn.commit()
    cur.close()
    conn.close()


    # to display the data form the table.
    con = connect_to_db()
    cur = con.cursor()
    query = f"SELECT * FROM public.student_marks WHERE class = {classs} AND exam_Type = '{exam_type}'"
    cur.execute(query)
    data = cur.fetchall()
    con.commit()
    cur.close()
    con.close()
    return render_template('view_marks.html', data = data, classs = classs,exam_type = exam_type,username = session.get('username'))

@app.route('/edit_marks',methods = ['GET','POST'])
def edit_marks():
    classs = int(request.form['class'])
    exam_type = request.form['exam_type']
    con = connect_to_db()
    cur = con.cursor()
    query = f'SELECT * FROM public.student_marks WHERE "class" = {classs} AND "exam_type" =\'{exam_type}\'' 
    cur.execute(query)
    students = cur.fetchall()
    con.commit()
    cur.close()
    con.close()

    return render_template('edit_marks.html', students=students, result=classs,exam_type=exam_type,username = session.get('username'))

@app.route('/after_edit_marks', methods=['GET', 'POST'])
def after_edit_marks():
    classs = request.args.get('class')
    exam_type = request.args.get('exam_type')
    edited_data = request.form['edited-data']
    edited_rows = json.loads(edited_data)

    if classs is not None:
        # Extract class value from classs string
        class_value = classs.split(',')[0]
        class_value = int(class_value)  # Convert class_value to integer

        for i in edited_rows:
            con = connect_to_db()
            cur = con.cursor()

            rollNo = int(i['0'])
            exam_type = i['1']
            student_name = i['2']
            section = i['3']
            telugu = i['4']
            english = i['5']
            mathematics = i['6']
            science = i['7']
            social = i['8']

            query = "UPDATE public.student_marks SET class = %s, roll_no = %s, exam_type = %s, student_name = %s, section = %s, telugu = %s, english = %s, mathematics = %s, science = %s, social = %s WHERE roll_no = %s and exam_type = %s"
            values = (class_value, rollNo, exam_type, student_name, section, telugu, english, mathematics, science, social, rollNo, exam_type)
            cur.execute(query, values)
            con.commit()
            cur.close()
            con.close()

        # Retrieve the updated student information after the update
        con = connect_to_db()
        cur = con.cursor()
        query = f"SELECT * FROM public.student_marks WHERE class = {class_value} AND exam_type = '{exam_type}'"
        cur.execute(query)
        students = cur.fetchall()
        cur.close()
        con.close()

        return render_template('view_marks.html', data=students, classs=class_value, exam_type=exam_type,username = session.get('username'))
    else:
        abort(400)

if __name__ == '__main__':
    app.run(debug=True)