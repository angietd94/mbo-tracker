# app/models.py

from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from sqlalchemy import func

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

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
    email_notifications = db.Column(db.Boolean, default=True)
    quarter_compensation = db.Column(db.Float, nullable=True)
    
    # Relationships
    mbos = db.relationship('MBO', back_populates='creator', lazy='dynamic')
    manager = db.relationship('User', remote_side=[id], backref=db.backref('team_members', lazy='dynamic'), foreign_keys=[manager_id])
    
    def get_profile_picture_url(self):
        """Return the profile picture URL without cache busting."""
        return self.profile_picture or '/static/path/to/default.jpg'
    
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

    def count_mbos_by_type(self, mbo_type):
        """Count the number of approved MBOs for a specific type"""
        return self.mbos.filter(
            MBO.mbo_type == mbo_type,
            MBO.approval_status == "Approved"
        ).count()

    def validate_mbo_count(self, mbo_type):
        """Validate if user can add more MBOs of a specific type"""
        current_count = self.count_mbos_by_type(mbo_type)
        
        limits = {
            'Learning and Certification': {'goal': 4, 'max': 6},
            'Demo and Assets': {'goal': 2, 'max': 4},
            'Impact': {'goal': 4, 'max': 8}
        }
        
        if mbo_type in limits:
            return {
                'current': current_count,
                'goal': limits[mbo_type]['goal'],
                'max': limits[mbo_type]['max'],
                'can_add': current_count < limits[mbo_type]['max'],
                'exceeds_goal': current_count > limits[mbo_type]['goal']
            }
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
    progress_status = db.Column(db.String(50), default="In progress")
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
    
    def has_attachment(self):
        """Check if the MBO has an attachment.
        Always returns False since attachments are no longer supported.
        """
        return False
    
    def __repr__(self):
        return f'<MBO {self.title}>'

class UserSettings(db.Model):
    __tablename__ = 'user_settings'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    key = db.Column(db.String(64), nullable=False)
    value = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship with User
    user = db.relationship('User', backref=db.backref('settings', lazy='dynamic'))
    
    # Ensure user_id and key combination is unique
    __table_args__ = (db.UniqueConstraint('user_id', 'key', name='_user_key_uc'),)
    
    def __repr__(self):
        return f'<UserSettings {self.user_id}:{self.key}>'
