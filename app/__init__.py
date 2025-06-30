# app/__init__.py

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
from flask_wtf.csrf import CSRFProtect
import os

# Load environment variables from .env file if python-dotenv is available
try:
    from dotenv import load_dotenv
    basedir = os.path.abspath(os.path.dirname(__file__))
    parent_dir = os.path.dirname(basedir)
    load_dotenv(os.path.join(parent_dir, '.env'))
    print("Loaded environment variables from .env file")
except ImportError:
    print("python-dotenv not installed. Using environment variables from system.")

# Import config
from config import config

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(config.get(os.getenv('FLASK_ENV', 'default')))
print(f"SQLALCHEMY_DATABASE_URI: {app.config.get('SQLALCHEMY_DATABASE_URI')}")

# Initialize extensions
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.session_protection = 'strong'
login_manager.refresh_view = 'login'
login_manager.needs_refresh_message = 'Please login again to confirm your identity'

# Enhance session security
app.config['SESSION_COOKIE_SECURE'] = os.environ.get('FLASK_ENV') == 'production'  # Secure in production
app.config['SESSION_COOKIE_HTTPONLY'] = True  # Prevent JavaScript access
app.config['PERMANENT_SESSION_LIFETIME'] = 3600  # Session timeout in seconds (1 hour)
app.config['SESSION_USE_SIGNER'] = True  # Sign the session cookie
mail = Mail(app)
csrf = CSRFProtect(app)

# Initialize Talisman for secure headers if available
try:
    from flask_talisman import Talisman
    csp = {
        'default-src': "'self'",
        'img-src': ["'self'", 'data:'],
        'script-src': ["'self'", "'unsafe-inline'"],
        'style-src': ["'self'", "'unsafe-inline'"],
    }
    # In development, set force_https=False
    force_https = os.environ.get('FLASK_ENV') == 'production'
    Talisman(app, content_security_policy=csp, force_https=force_https)
    print("Talisman initialized for secure headers")
except ImportError:
    print("flask-talisman not installed. Secure headers not enabled.")

# Import models
from app import models

# Initialize notifications
from app import notifications
notifications.init_app(app)

# Import routes package
from app.routes import *
