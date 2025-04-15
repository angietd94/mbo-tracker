import os

# Load environment variables from .env file if python-dotenv is available
basedir = os.path.abspath(os.path.dirname(__file__))
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(basedir, '.env'))
    print("Loaded environment variables from .env file")
except ImportError:
    print("python-dotenv not installed. Using environment variables from system.")

class Config:
    """Base configuration."""
    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY')
    if not SECRET_KEY:
        SECRET_KEY = 'default-dev-key-replace-in-production'
        print("WARNING: Using default SECRET_KEY. Set it in .env file or environment variables.")
    
    # SQLAlchemy - Always set a default
    # Direct PostgreSQL connection with correct password
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:postgres@database-mbo-project-solutions-engineers.cluster-cnpur7nyk8zh.eu-west-3.rds.amazonaws.com/postgres'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Mail
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.example.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'True').lower() in ['true', 'yes', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME', '')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', '')
    
    # Admin user
    ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL', 'admin@example.com')
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'Admin@Secure123!')

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    # Use the same PostgreSQL connection
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:postgres@database-mbo-project-solutions-engineers.cluster-cnpur7nyk8zh.eu-west-3.rds.amazonaws.com/postgres'

class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    # Use the same PostgreSQL connection
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:postgres@database-mbo-project-solutions-engineers.cluster-cnpur7nyk8zh.eu-west-3.rds.amazonaws.com/postgres'

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
