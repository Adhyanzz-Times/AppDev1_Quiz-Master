from flask import Flask, render_template, request, session, redirect, url_for, flash
from controller.database import db
from controller.models import *
import os
from datetime import datetime
from datetime import timedelta

app = Flask(__name__, template_folder='views')

# Database Config
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Disable warnings
app.config['SECRET_KEY'] = 'thisissecretkey'

# Initialize Database
db.init_app(app)

# Import routes after db is initialized
from controller.routes import *

if __name__ == '__main__':
    with app.app_context():
        if not os.path.exists("db.sqlite3"):  # Ensure DB file exists
            print("Database not found! Creating new one...")
            db.create_all()
            print("Database successfully created ✅")
        else:
            print("Database already exists ✅")
        
    # Run Flask App
    app.run(debug=True)
