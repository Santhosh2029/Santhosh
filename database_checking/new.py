# from flask import Flask, render_template, request, url_for, redirect, session
# from flask_sqlalchemy import SQLAlchemy
# import bcrypt
# import smtplib
# import random
# import string
# from flask_mail import Mail, Message
# import os

# # Create Flask app
# app = Flask(__name__)
# app.secret_key = os.urandom(24)  # Set a secret key

# # Configure Flask-Mail
# app.config['MAIL_SERVER'] = 'smtp.gmail.com'
# app.config['MAIL_PORT'] = 587
# app.config['MAIL_USE_TLS'] = True
# app.config['MAIL_USERNAME'] = 'sunnyprince9533@gmail.com'
# app.config['MAIL_PASSWORD'] = 'hctadxyjyvgjbqoy'

# mail = Mail(app)

# # Configuring the database
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Otsi@123@localhost:5432/postgres'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# # Installing SQLAlchemy
# db = SQLAlchemy(app)

# # Importing the models
# # from models import UserAuthent, ExampleStudents, StudentMarks

# # UserAuthent model
# class UserAuthent(db.Model):
#     __tablename__ = 'user_authent'

#     id = db.Column(db.Integer, primary_key=True)
#     mail_id = db.Column(db.String(255), unique=True, nullable=False)
#     password = db.Column(db.String(255), nullable=False)
#     name = db.Column(db.String(255), nullable=False)
#     phone_number = db.Column(db.String(20), nullable=False)
#     otp = db.Column(db.String(4))

# # ExampleStudents model
# class ExampleStudents(db.Model):
#     __tablename__ = 'example_students'

#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(255), nullable=False)
#     class_info = db.Column(db.String(50), nullable=False)
#     address = db.Column(db.String(255), nullable=False)
#     phone_number = db.Column(db.String(20), nullable=False)

# # StudentMarks model
# class StudentMarks(db.Model):
#     __tablename__ = 'student_marks'

#     id = db.Column(db.Integer, primary_key=True)
#     student_id = db.Column(db.Integer, db.ForeignKey('example_students.id'), nullable=False)
#     subject = db.Column(db.String(100), nullable=False)
#     marks = db.Column(db.Float, nullable=False)

#     student = db.relationship('ExampleStudents', backref=db.backref('marks', lazy=True))

# # Routes

# @app.route('/')
# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     return render_template('login.html')

# # For Login
# @app.route('/after_login', methods=['POST'])
# def after_login():
#     email = request.form['username']
#     password = request.form['password']

#     user = UserAuthent.query.filter_by(mail_id=email).first()

#     if user and bcrypt.checkpw(password.encode('utf-8'), user.password):
#         session['username'] = email
#         return redirect('/home')
#     else:
#         return render_template('login.html')

# # Forgot Password
# @app.route('/forgot_password', methods=['GET', 'POST'])
# def forgot_password():
#     return render_template('otp_send.html')

# @app.route('/send_otp', methods=['POST'])
# def send_otp():
#     mail_address = request.form['email']

#     user = UserAuthent.query.filter_by(mail_id=mail_address).first()

#     if user:
#         otp = generate_otp()
#         user.otp = otp
#         db.session.commit()
#         send_email(mail_address, otp)
#         return render_template('enterotp.html', mail_address=mail_address)
#     else:
#         return 'Email not found'

# def generate_otp():
#     digits = string.digits
#     otp = ''.join(random.choice(digits) for _ in range(4))
#     return otp

# def send_email(mail_address, otp):
#     smtp_server = app.config['MAIL_SERVER']
#     smtp_port = app.config['MAIL_PORT']
#     smtp_username = app.config['MAIL_USERNAME']
#     smtp_password = app.config['MAIL_PASSWORD']

#     subject = 'OTP Verification'
#     message = f'Your OTP is: {otp}'

#     try:
#         with smtplib.SMTP(smtp_server, smtp_port) as server:
#             server.starttls()
#             server.login(smtp_username, smtp_password)
#             msg = Message(subject=subject, sender=smtp_username, recipients=[mail_address])
#             msg.body = message
#             mail.send(msg)
#         print('Email sent successfully')
#     except Exception as e:
#         print(f'Error while sending email: {e}')

# @app.route('/after_enter_otp', methods=['POST'])
# def after_enter_otp():
#     otp = request.form['otp']
#     mail = request.args.get('mail')

#     user = UserAuthent.query.filter_by(mail_id=mail).first()

#     if user and user.otp == otp:
#         return render_template('enter_new_password.html')
#     else:
#         return render_template('otp_send.html', mail=mail)

# @app.route('/reset_password', methods=['POST'])
# def reset_password():
#     new_password = request.form['new_password']
#     confirm_password = request.form['confirm_password']
#     mail = request.args.get('mail')

#     if new_password == confirm_password:
#         hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
#         user = UserAuthent.query.filter_by(mail_id=mail).first()
#         user.password = hashed_password
#         db.session.commit()
#         return redirect(url_for('login'))
#     else:
#         return render_template('enter_new_password.html')

# @app.route('/register', methods=['GET', 'POST'])
# def register():
#     return render_template('register.html')

# @app.route('/after_register', methods=['POST'])
# def after_register():
#     email = request.form['email']
#     password = request.form['password']
#     confirm_password = request.form['confirm_password']
#     name = request.form['name']
#     phone_number = request.form['phone_number']

#     if password == confirm_password:
#         hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
#         new_user = UserAuthent(mail_id=email, password=hashed_password, name=name, phone_number=phone_number)
#         db.session.add(new_user)
#         db.session.commit()
#         return redirect(url_for('login'))
#     else:
#         return render_template('register.html')

# @app.route('/home')
# def home():
#     if 'username' in session:
#         return render_template('home.html')
#     else:
#         return redirect(url_for('login'))

# @app.route('/student_info', methods=['POST'])
# def student_info():
#     class_info = request.form['class']
#     students = ExampleStudents.query.filter_by(class_info=class_info).all()
#     return render_template('student_info.html', students=students)

# @app.route('/student_info_update', methods=['POST'])
# def student_info_update():
#     student_id = request.form['student_id']
#     student = ExampleStudents.query.get(student_id)
#     return render_template('update_student_info.html', student=student)

# @app.route('/after_student_info_update', methods=['POST'])
# def after_student_info_update():
#     student_id = request.form['student_id']
#     student = ExampleStudents.query.get(student_id)
#     student.name = request.form['name']
#     student.class_info = request.form['class_info']
#     student.address = request.form['address']
#     student.phone_number = request.form['phone_number']
#     db.session.commit()
#     return redirect(url_for('student_info'))

# if __name__ == '__main__':
#     db.create_all()
#     app.run(debug=True)

