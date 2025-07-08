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
    WTF_CSRF_ENABLED = False  # Disable CSRF globally
    SECRET_KEY = os.environ.get('SECRET_KEY')
    if not SECRET_KEY:
        SECRET_KEY = 'default-dev-key-replace-in-production'
        print("WARNING: Using default SECRET_KEY. Set it in .env file or environment variables.")

    AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
    AWS_REGION = os.environ.get('AWS_REGION', 'eu-west-3').split('#')[0].strip()
    
    # SQLAlchemy - Use environment variables for sensitive connection info
    DB_USER = os.environ.get('DB_USER', 'postgres')
    DB_PASSWORD = os.environ.get('DB_PASSWORD', '')
    DB_HOST = os.environ.get('DB_HOST', 'localhost')
    DB_NAME = os.environ.get('DB_NAME', 'postgres')
    
    # Construct the database URI from environment variables
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Mail - Use environment variables for sensitive info
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.example.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'True').lower() in ['true', 'yes', '1']
    MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL', 'False').lower() in ['true', 'yes', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME', '')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', '')
    BASE_URL = os.environ.get('BASE_URL', 'http://localhost:5000')
    
    # Admin user - Use environment variables for sensitive info
    ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL', 'admin@example.com')
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'change-me-in-production')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'docx', 'doc', 'gif'}
    S3_BUCKET = os.environ.get('S3_BUCKET', 'mbo-solutions-engineer-data')
class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    # Uses the base SQLALCHEMY_DATABASE_URI from Config

class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    # Uses the base SQLALCHEMY_DATABASE_URI from Config

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
