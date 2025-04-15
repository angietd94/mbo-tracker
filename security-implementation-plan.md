# Security and Architecture Implementation Plan

This document outlines the step-by-step implementation plan for improving the security and architecture of the MBO application.

## Phase 1: Environment Variables and Configuration

### 1.1 Environment Variables Setup

#### Create `.env.example` file
```
# Flask Application Settings
FLASK_APP=run:app
FLASK_ENV=development
SECRET_KEY=change_this_to_a_secure_random_string

# Database Settings
DATABASE_URL=postgresql://postgres:postgres@localhost/snaplogic_db

# Email Settings
MAIL_SERVER=smtp.example.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your_email@example.com
MAIL_PASSWORD=your_email_password

# Admin User Settings (for initial setup only)
ADMIN_EMAIL=admin@example.com
ADMIN_PASSWORD=change_this_to_a_secure_password
```

#### Update `.gitignore` file
Add the following to `.gitignore`:
```
# Environment variables
.env
*.env

# Instance folder
instance/

# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# Distribution / packaging
dist/
build/
*.egg-info/

# Virtual environments
venv/
env/
ENV/

# IDE specific files
.idea/
.vscode/
*.swp
*.swo
```

### 1.2 Configuration Management

#### Create unified `config.py`
Replace both existing config files with a single, class-based configuration system:

```python
import os
from dotenv import load_dotenv

# Load environment variables from .env file
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    """Base configuration."""
    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY')
    if not SECRET_KEY:
        raise ValueError("No SECRET_KEY set for Flask application")
    
    # SQLAlchemy
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Mail
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'True').lower() in ['true', 'yes', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    
    # Admin user
    ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL')
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD')

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'instance', 'dev.db')

class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    if not SQLALCHEMY_DATABASE_URI:
        raise ValueError("No DATABASE_URL set for Production environment")

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
```

### 1.3 Application Factory Pattern

#### Update `__init__.py`
Refactor the application initialization to use the factory pattern:

```python
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
from flask_wtf.csrf import CSRFProtect

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
mail = Mail()
csrf = CSRFProtect()

def create_app(config_name='default'):
    """Application factory function."""
    from config import config
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    mail.init_app(app)
    csrf.init_app(app)
    
    # Register blueprints
    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp)
    
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)
    
    from app.mbo import bp as mbo_bp
    app.register_blueprint(mbo_bp)
    
    return app
```

#### Update `run.py`
Modify the entry point to use the factory pattern and remove hardcoded credentials:

```python
import os
from app import create_app, db
from app.models import User
from werkzeug.security import generate_password_hash

app = create_app(os.environ.get('FLASK_ENV', 'default'))

@app.cli.command('init-admin')
def create_default_admin():
    """Create the admin user from environment variables."""
    from flask import current_app
    
    admin_email = current_app.config.get('ADMIN_EMAIL')
    admin_password = current_app.config.get('ADMIN_PASSWORD')
    
    if not admin_email or not admin_password:
        print("Admin credentials not set in environment variables.")
        return
    
    admin = User.query.filter_by(email=admin_email).first()
    if not admin:
        admin = User(
            email=admin_email,
            first_name='Admin',
            last_name='User',
            role='Manager',
            password_hash=generate_password_hash(admin_password)
        )
        db.session.add(admin)
        db.session.commit()
        print("Admin user created successfully.")
    else:
        print("Admin user already exists.")

if __name__ == '__main__':
    app.run()
```

## Phase 2: Code Organization with Blueprints

### 2.1 Create Blueprint Structure

Create the following directory structure:
```
app/
  ├── __init__.py
  ├── models.py
  ├── auth/
  │   ├── __init__.py
  │   └── routes.py
  ├── main/
  │   ├── __init__.py
  │   └── routes.py
  ├── mbo/
  │   ├── __init__.py
  │   └── routes.py
  ├── static/
  │   └── css/
  │       └── style.css
  ├── templates/
  │   ├── auth/
  │   │   ├── login.html
  │   │   └── profile.html
  │   ├── main/
  │   │   ├── dashboard.html
  │   │   └── index.html
  │   ├── mbo/
  │   │   ├── mbo_details.html
  │   │   ├── mbo_form.html
  │   │   └── my_mbos.html
  │   ├── layout.html
  │   └── auth_layout.html
  └── utils/
      ├── __init__.py
      ├── date_utils.py
      └── security_utils.py
```

### 2.2 Refactor Routes into Blueprints

Move routes from the main routes.py file into their respective blueprint files.

## Phase 3: Security Enhancements

### 3.1 Password Policy Implementation

Create a password validation utility in `app/utils/security_utils.py`:

```python
import re
from datetime import datetime, timedelta

def validate_password(password):
    """
    Validate password complexity.
    
    Requirements:
    - At least 8 characters
    - Contains at least one uppercase letter
    - Contains at least one lowercase letter
    - Contains at least one digit
    - Contains at least one special character
    
    Returns:
    - (bool, str): (is_valid, error_message)
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long."
    
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter."
    
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter."
    
    if not re.search(r'[0-9]', password):
        return False, "Password must contain at least one digit."
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Password must contain at least one special character."
    
    return True, "Password meets complexity requirements."
```

### 3.2 Secure Headers Implementation

Add secure headers configuration to `create_app` function:

```python
from flask_talisman import Talisman

def create_app(config_name='default'):
    # ... existing code ...
    
    # Initialize Talisman for secure headers
    csp = {
        'default-src': '\'self\'',
        'img-src': ['\'self\'', 'data:'],
        'script-src': ['\'self\''],
        'style-src': ['\'self\'', '\'unsafe-inline\''],
    }
    Talisman(app, content_security_policy=csp, force_https=False)  # Set force_https=True in production
    
    # ... rest of the function ...
```

### 3.3 Audit Logging

Create a logging utility in `app/utils/logging_utils.py`:

```python
import logging
from flask import request, current_app, g

def setup_logging(app):
    """Configure application logging."""
    handler = logging.FileHandler('app.log')
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    
    app.logger.addHandler(handler)
    app.logger.setLevel(logging.INFO)
    
    # Create security logger
    security_logger = logging.getLogger('security')
    security_logger.addHandler(handler)
    security_logger.setLevel(logging.INFO)
    
    return security_logger

def log_auth_event(event_type, user_id=None, success=True, details=None):
    """Log authentication events."""
    logger = logging.getLogger('security')
    
    # Don't log sensitive information
    if details and 'password' in details:
        details.pop('password')
    
    ip_address = request.remote_addr
    user_agent = request.user_agent.string
    
    logger.info(
        f"AUTH EVENT: {event_type} | User ID: {user_id} | Success: {success} | "
        f"IP: {ip_address} | User-Agent: {user_agent} | Details: {details}"
    )
```

## Implementation Timeline

1. **Week 1**: Environment Variables and Configuration
   - Set up .env and .gitignore
   - Refactor configuration system
   - Implement application factory pattern

2. **Week 2**: Code Organization
   - Create blueprint structure
   - Refactor routes into blueprints
   - Organize utility functions

3. **Week 3**: Security Enhancements
   - Implement password policies
   - Add secure headers
   - Set up audit logging

4. **Week 4**: Testing and Documentation
   - Add comprehensive tests
   - Update documentation