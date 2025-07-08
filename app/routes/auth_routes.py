from flask import render_template, redirect, url_for, request, flash, session
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from app import app, db
from app.models import User, UserSettings
from app.utils.security_utils import generate_reset_token, verify_reset_token
from app.utils.email_utils import send_password_reset_email
import os

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    # Redirect already authenticated users
    if current_user.is_authenticated:
        # Force logout of current user to prevent session conflicts
        logout_user()
        session.clear()
        print("Logged out previously authenticated user")

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        # Log login attempt (without password)
        print(f"Login attempt for email: {email}")
        
        # Find the user by email
        user = User.query.filter_by(email=email).first()
        
        # Validate credentials
        if user and check_password_hash(user.password_hash, password):
            # Force logout any existing user and clear session
            if current_user.is_authenticated:
                logout_user()
            
            # Clear any existing session data before login
            session.clear()
            
            # Generate a new session token
            session_token = os.urandom(16).hex()
            
            # Store the session token in the database
            # This will invalidate any existing sessions for this user
            existing_setting = UserSettings.query.filter_by(
                user_id=user.id,
                key='current_session_token'
            ).first()
            
            if existing_setting:
                # Update existing token
                existing_setting.value = session_token
            else:
                # Create new token entry
                new_setting = UserSettings(
                    user_id=user.id,
                    key='current_session_token',
                    value=session_token
                )
                db.session.add(new_setting)
            
            # Commit the changes to the database
            db.session.commit()
            
            # Check if "Remember Me" was checked
            remember_me = 'remember_me' in request.form
            
            # Log the user in with remember=True if "Remember Me" was checked
            # This will set a longer session duration (30 days)
            login_user(user, remember=remember_me)
            
            # Log successful login
            print(f"Successful login: ID={user.id}, Email={user.email}")
            
            # Store user ID in session for additional verification
            session['user_id'] = user.id
            session['user_email'] = user.email
            # Add a session token to identify this specific session
            session['session_token'] = session_token
            
            # Redirect to next page or dashboard
            next_page = request.args.get('next')
            return redirect(next_page or url_for('dashboard'))
        
        # Log failed login attempt
        print(f"Failed login attempt for email: {email}")
        
        # Show error message
        flash('Invalid email or password.')
        return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    # Get user info before logout for logging purposes
    user_email = current_user.email if current_user else "Unknown"
    user_id = current_user.id if current_user else "Unknown"
    
    # Clear the session token from the database
    if user_id != "Unknown":
        stored_token = UserSettings.query.filter_by(
            user_id=user_id,
            key='current_session_token'
        ).first()
        
        if stored_token:
            # Set to an invalid token to ensure the session is invalidated
            stored_token.value = 'logged_out_' + os.urandom(8).hex()
            db.session.commit()
    
    # Properly log out the user
    logout_user()
    
    # Clear the session completely
    session.clear()
    
    # Print log message for debugging
    print(f"User logged out: ID={user_id}, Email={user_email}")
    
    # Set a flash message
    flash('You have been successfully logged out.')
    
    # Redirect to login page with cache-busting parameter
    # This helps prevent browser caching issues
    cache_buster = os.urandom(8).hex()
    return redirect(url_for('index', _cb=cache_buster))

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    """Handle forgot password requests."""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()
        
        if user:
            # Generate a secure token
            token = generate_reset_token(user.id)
            
            # Send password reset email
            send_password_reset_email(user, token)
            
        # Don't reveal whether the email exists or not
        flash('If an account exists with that email, a password reset link has been sent.')
        return redirect(url_for('login'))
    
    return render_template('forgot_password.html')

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password_with_token(token):
    """Reset password with a token."""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    # Verify the token
    user_id = verify_reset_token(token)
    if not user_id:
        flash('Invalid or expired token. Please try again.')
        return redirect(url_for('forgot_password'))
    
    user = User.query.get(user_id)
    if not user:
        flash('User not found.')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if not password or not confirm_password:
            flash('Please enter a password and confirm it.')
            return render_template('reset_password.html', token=token)
        
        if password != confirm_password:
            flash('Passwords do not match.')
            return render_template('reset_password.html', token=token)
        
        # Update the user's password
        user.set_password(password)
        db.session.commit()
        
        flash('Your password has been updated. You can now log in with your new password.')
        return redirect(url_for('login'))
    
    return render_template('reset_password.html', token=token)