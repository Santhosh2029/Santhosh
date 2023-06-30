from flask import Flask, render_template, request, redirect,url_for
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)

# Configure to Database.
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Otsi@123@localhost:5432/postgres'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Installing SQLAlchemy
db = SQLAlchemy(app)

# Model for UserAuthent
class UserAuthent(db.Model):
    __tablename__ = 'user_authent'

    id = db.Column(db.Integer, primary_key=True)
    mail_id = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)
    otp = db.Column(db.String(4))




if __name__ == "__main__":
    app.run(debug=True)