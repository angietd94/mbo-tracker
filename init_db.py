#!/usr/bin/env python3
"""
Database initialization script for MBO Tracker.
This script creates the database tables and adds an admin user.
"""

from app import app, db
from app.models import User
from werkzeug.security import generate_password_hash
import os

def init_db():
    """Initialize the database with tables and an admin user."""
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # Check if admin user exists
        admin_email = os.environ.get('ADMIN_EMAIL', 'admin@example.com')
        admin = User.query.filter_by(email=admin_email).first()
        
        # Create admin user if it doesn't exist
        if not admin:
            admin_password = os.environ.get('ADMIN_PASSWORD', 'admin')
            admin = User(
                email=admin_email,
                username='admin',
                first_name='Admin',
                last_name='User',
                position='Administrator',
                role='Manager',
                region='ALL'
            )
            admin.password_hash = generate_password_hash(admin_password)
            db.session.add(admin)
            db.session.commit()
            print(f"Admin user created with email: {admin_email}")
        else:
            print(f"Admin user already exists with email: {admin_email}")
        
        print("Database initialized successfully!")

if __name__ == '__main__':
    init_db()