# app/models.py

from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
<<<<<<< HEAD
<<<<<<< HEAD
=======
import json
import os
>>>>>>> 6b472e0 (Update MBO Tracker application)
=======
>>>>>>> a6a29bae4bb6e51517b81b41b9cdf7b89a26a842

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

<<<<<<< HEAD
<<<<<<< HEAD
=======
class UserSettings(db.Model):
    """Model for storing user settings that don't require schema changes to the User model."""
    __tablename__ = 'user_settings'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    key = db.Column(db.String(64), nullable=False)
    value = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Composite unique constraint to ensure one setting per user
    __table_args__ = (db.UniqueConstraint('user_id', 'key', name='_user_key_uc'),)
    
    user = db.relationship('User', backref=db.backref('settings', lazy=True))

>>>>>>> 6b472e0 (Update MBO Tracker application)
=======
>>>>>>> a6a29bae4bb6e51517b81b41b9cdf7b89a26a842
class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(64))
    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))
    position = db.Column(db.String(64))
    role = db.Column(db.String(20), default='Employee')
    password_hash = db.Column(db.String(256))  # Password hash storage
    profile_picture = db.Column(db.String(256), default='default.jpg')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # New fields
    region = db.Column(db.String(10), default='EMEA')  # EMEA, AMER, or APAC
    manager_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # These fields are commented out because they require database migrations
    # email_notifications = db.Column(db.Boolean, nullable=True)
    # quarter_compensation = db.Column(db.Float, nullable=True)
    
    def get_email_notifications(self):
        """Get email notification preference with fallback to True for existing users"""
<<<<<<< HEAD
<<<<<<< HEAD
        # Since the column doesn't exist in the database, always return True
        return True
=======
        # First try to get from UserSettings
        setting = UserSettings.query.filter_by(user_id=self.id, key='email_notifications').first()
        if setting:
            return setting.value.lower() == 'true'
        
        # Fall back to session
        from flask import session
        return session.get(f'user_{self.id}_email_notifications', True)
>>>>>>> 6b472e0 (Update MBO Tracker application)
=======
        # Since the column doesn't exist in the database, always return True
        return True
>>>>>>> a6a29bae4bb6e51517b81b41b9cdf7b89a26a842
        
    @property
    def email_notifications(self):
        """Virtual property for email_notifications"""
        from flask import session
        # Get from session if available, otherwise default to True
        return session.get(f'user_{self.id}_email_notifications', True)
        
    @email_notifications.setter
    def email_notifications(self, value):
        """Setter for email_notifications - stores in session since column doesn't exist"""
        from flask import session
        session[f'user_{self.id}_email_notifications'] = value
        
<<<<<<< HEAD
<<<<<<< HEAD
=======
        # Also save to the UserSettings table for persistence
        setting = UserSettings.query.filter_by(user_id=self.id, key='email_notifications').first()
        if setting:
            setting.value = str(value).lower()
        else:
            setting = UserSettings(user_id=self.id, key='email_notifications', value=str(value).lower())
            db.session.add(setting)
        db.session.commit()
        
>>>>>>> 6b472e0 (Update MBO Tracker application)
=======
>>>>>>> a6a29bae4bb6e51517b81b41b9cdf7b89a26a842
    @property
    def quarter_compensation(self):
        """Virtual property for quarter_compensation"""
        return 0.0
        
    @quarter_compensation.setter
    def quarter_compensation(self, value):
        """Setter for quarter_compensation - does nothing since column doesn't exist"""
        pass
    
    # Relationships
    # Relationship with MBO
    mbos = db.relationship('MBO', back_populates='creator', lazy='dynamic')
    
    # Manager relationship (self-referential)
    manager = db.relationship('User', remote_side=[id], backref=db.backref('team_members', lazy='dynamic'), foreign_keys=[manager_id])
    
    def set_password(self, password):
        """Set the password hash for the user."""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if the provided password matches the hash."""
        return check_password_hash(self.password_hash, password)
    
    def get_full_name(self):
        """Return the user's full name."""
        return f"{self.first_name} {self.last_name}"
    
    def get_manager_name(self):
        """Return the manager's full name or None if no manager."""
        if self.manager:
            return f"{self.manager.first_name} {self.manager.last_name}"
        return None
    
    def __repr__(self):
        return f'<User {self.email}>'

class MBO(db.Model):
    __tablename__ = 'mbo'

    id = db.Column(db.Integer, primary_key=True)
    mbo_type = db.Column(db.String(100))
    title = db.Column(db.String(200))
    description = db.Column(db.Text)
    optional_link = db.Column(db.String(300))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    points = db.Column(db.Integer)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    progress_status = db.Column(db.String(50), default="New")
    approval_status = db.Column(db.String(50), default="Pending Approval")

    # Relationship with User
    creator = db.relationship('User', back_populates='mbos')
    
    def is_approved(self):
        """Check if the MBO is approved."""
        return self.approval_status == "Approved"
    
    def is_pending(self):
        """Check if the MBO is pending approval."""
        return self.approval_status == "Pending Approval"
    
    def is_rejected(self):
        """Check if the MBO is rejected."""
        return self.approval_status == "Rejected"

    def __repr__(self):
        return f'<MBO {self.title}>'
