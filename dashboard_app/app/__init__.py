from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config

import logging

# Initialize the app
app = Flask(__name__)
app.config.from_object("config.Config")
app.logger.setLevel(logging.DEBUG)
# app.config['SECRET_KEY'] = 'your-secret-key'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://myuser:mypassword@db:5432/mydb'

# Initialize the database
db = SQLAlchemy(app)

# Initialize the login manager
login_manager = LoginManager(app)
login_manager.init_app(app)
login_manager.login_view = 'login'

# Import the views (routes) and models
from app import routes, models
