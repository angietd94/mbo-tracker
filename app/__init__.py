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
from config import Config

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Initialize extensions
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
mail = Mail(app)
csrf = CSRFProtect(app)

# Initialize Talisman for secure headers if available
try:
    from flask_talisman import Talisman
    csp = {
        'default-src': "'self'",
        'img-src': ["'self'", 'data:'],
        'script-src': ["'self'"],
        'style-src': ["'self'", "'unsafe-inline'"],
    }
    # In development, set force_https=False
    force_https = os.environ.get('FLASK_ENV') == 'production'
    Talisman(app, content_security_policy=csp, force_https=force_https)
    print("Talisman initialized for secure headers")
except ImportError:
    print("flask-talisman not installed. Secure headers not enabled.")

# Import routes and models
from app import routes, models
