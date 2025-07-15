from app import app, db
from app.models import User
from werkzeug.security import generate_password_hash
import os

def create_default_admin():
    """
    Create the admin user from environment variables.
    
    Required environment variables:
    - ADMIN_EMAIL: Email address for the admin user
    - ADMIN_PASSWORD: Password for the admin user
    """
    admin_email = app.config.get('ADMIN_EMAIL')
    admin_password = app.config.get('ADMIN_PASSWORD')
    
    if not admin_email or not admin_password:
        print("Error: Admin credentials not set in environment variables.")
        print("Please set ADMIN_EMAIL and ADMIN_PASSWORD in your .env file or environment.")
        return
    
    admin = User.query.filter_by(email=admin_email).first()
    if not admin:
        admin = User(
            email=admin_email,
            first_name='Admin',
            last_name='User',
            role='Manager'
        )
        admin.set_password(admin_password)
        db.session.add(admin)
        db.session.commit()
        print(f"Admin user '{admin_email}' created successfully.")
    else:
        print(f"Admin user '{admin_email}' already exists.")

# Add health check endpoints
@app.route('/health')
def health_check():
    return {'status': 'healthy'}, 200

@app.route('/healthz')
def healthz_check():
    return {'status': 'ok'}, 200

if __name__ == '__main__':
    # Check if admin credentials are set
    if not app.config.get('ADMIN_EMAIL') or not app.config.get('ADMIN_PASSWORD'):
        print("Warning: Admin credentials not set in environment variables.")
        print("You can set them later and run the application with 'flask run' to create the admin user.")
    
    # Create admin user if running in development mode
    if app.config.get('DEBUG', False):
        with app.app_context():
            create_default_admin()

    # Configure app with AWS credentials from environment variables
    app.config['AWS_ACCESS_KEY_ID'] = os.environ.get('AWS_ACCESS_KEY_ID')
    app.config['AWS_SECRET_ACCESS_KEY'] = os.environ.get('AWS_SECRET_ACCESS_KEY')
    app.config['AWS_REGION'] = os.environ.get('AWS_REGION')
    app.config['S3_BUCKET'] = os.environ.get('S3_BUCKET')
    app.config['AWS_SECRET_ACCESS_KEY'] = os.environ.get('AWS_SECRET_ACCESS_KEY')
    app.config['AWS_REGION'] = os.environ.get('AWS_REGION')
    
    # Use the default port 5000
    app.run(host='0.0.0.0', debug=True)
