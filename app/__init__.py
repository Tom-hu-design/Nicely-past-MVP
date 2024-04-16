from flask import Flask
from flask_sqlalchemy import SQLAlchemy

UPLOAD_FOLDER = 'app/static/upload'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

app.config ['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///userdata.sqlite3'
app.config['SECRET_KEY'] = "kljgT755GH65s"

def getApp():
    return app          

db = SQLAlchemy(app)
db.create_all()

print(" ")
print("################################################################################################################################################################")
print("")
print("Welcome to Nicely Beta!")
print("Nicely is a real time emotion indicator that uses your public social media activities to regulate your mood. Please visit /login to start the website")
print("version number: v0.6.0")
print("please make sure your device can connect to Twitter, if not use a VPN to do so")
print("")
print("helpful links ...")
print("/logout to logout current user")
print("/dashboard to personal dashboard page")
print("/community to Nicely Community")

from app import routes