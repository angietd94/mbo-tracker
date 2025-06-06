from flask import render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename
from app import app, db
from app.models import User, MBO  # Added MBO import to fix the error on line 131
from app.utils.file_utils import upload_file_locally
from datetime import datetime
import os
import time
import uuid
from werkzeug.utils import secure_filename

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """User profile page."""
    managers = User.query.filter_by(role='Manager').all()

    if request.method == 'POST':
        user = current_user
        user.first_name = request.form['first_name']
        user.last_name = request.form['last_name']
        user.position = request.form.get('position', '')
        user.region = request.form.get('region', 'EMEA')
        
        
        
        manager_id = request.form.get('manager_id')
        if manager_id:
            user.manager_id = int(manager_id)
        
        password = request.form.get('password')
        if password:
            user.set_password(password)
        
        # ---- New: Process file upload ----
        file = request.files.get('profile_picture')
        if file and file.filename:
            filename = secure_filename(file.filename)
            upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(upload_path)
            user.profile_picture = f'/uploads/{filename}'
            # Optionally update a timestamp (if you later add profile_picture_updated_at)
        
        db.session.commit()
        flash('Profile updated successfully!')
        return redirect(url_for('profile'))
    
    return render_template('profile.html', managers=managers)

@app.route('/user_profile', methods=['GET', 'POST'], endpoint='user_profile')
@login_required
def user_profile():
    """User profile page."""
    # Get all managers for the dropdown
    managers = User.query.filter_by(role='Manager').all()
    
    if request.method == 'POST':
        current_user.first_name = request.form['first_name']
        current_user.last_name = request.form['last_name']
        current_user.position = request.form.get('position', '')
        current_user.region = request.form.get('region', 'EMEA')
        
        
        
        # Handle manager selection
        manager_id = request.form.get('manager_id')
        if manager_id:
            current_user.manager_id = int(manager_id)
        
        # Handle password change if provided
        new_password = request.form.get('new_password')
        if new_password:
            current_user.set_password(new_password)
        
        # Handle profile picture upload
        profile_pic = request.files.get('profile_picture')
        if profile_pic and profile_pic.filename:
            print(f"Processing profile picture upload: {profile_pic.filename}")
            
            # Make sure the file is not empty
            profile_pic.seek(0, 2)  # Go to the end of the file
            file_size = profile_pic.tell()  # Get current position (file size)
            profile_pic.seek(0)  # Reset to the beginning
            
            if file_size == 0:
                flash('Error: The uploaded file is empty', 'error')
            else:
                # Check if file is an allowed image format
                filename = secure_filename(profile_pic.filename)
                extension = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
                
                if extension not in ['png', 'jpg', 'jpeg', 'gif']:
                    flash('Error: Only image files (PNG, JPG, JPEG, GIF) are allowed', 'error')
                else:
                    try:
                        # Using the improved local file storage for profile pictures
                        from app.utils.file_utils import save_profile_picture
                        
                        # Save the profile picture locally with standardized naming
                        path = save_profile_picture(profile_pic, current_user.id)
                        
                        if path:
                            # S3 references have been removed
                            
                            # Update the profile picture path
                            current_user.profile_picture = path
                            
                            # Update timestamp for cache busting
                            current_user.profile_picture_updated_at = datetime.utcnow()
                            
                            print(f"Profile picture saved: {path}")
                            flash('Profile picture updated successfully!', 'success')
                        else:
                            print("Failed to save profile picture")
                            flash('Failed to save profile picture', 'error')
                    except Exception as e:
                        print(f"Error saving profile picture: {str(e)}")
                        flash(f'Error: {str(e)}', 'error')
        
        db.session.commit()
        flash('Profile updated successfully!')
        return redirect(url_for('user_profile'))
    
    return render_template('user_profile.html', managers=managers)

@app.route('/users')
@login_required
def users():
    """Users list page."""
    # Allow all users to view the users page
    users = User.query.all()
    return render_template('users.html', users=users)

@app.route('/add_user', methods=['GET', 'POST'])
@login_required
def add_user():
    """Add a new user."""
    if current_user.role != 'Manager':
        flash('You do not have permission to add users.')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        email = request.form['email']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        position = request.form.get('position', '')
        role = request.form.get('role', 'Employee')
        region = request.form.get('region', 'EMEA')
        manager_id = request.form.get('manager_id')
        
        # Check if user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('A user with that email already exists.')
            return redirect(url_for('add_user'))
        
        # Create new user
        new_user = User(
            email=email,
            first_name=first_name,
            last_name=last_name,
            position=position,
            role=role,
            region=region
        )
        
        # Set default password
        new_user.set_password('ChangeMe123!')
        
        # Set manager if provided
        if manager_id:
            new_user.manager_id = int(manager_id)
        
        db.session.add(new_user)
        db.session.commit()
        
        flash(f'User {first_name} {last_name} added successfully with default password "ChangeMe123!"')
        return redirect(url_for('users'))
    
    # Get all managers for the dropdown
    managers = User.query.filter_by(role='Manager').all()
    return render_template('add_user.html', managers=managers)

@app.route('/delete_user/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    """Delete a user."""
    if current_user.role != 'Manager':
        flash('You do not have permission to delete users.')
        return redirect(url_for('dashboard'))
    
    user = User.query.get_or_404(user_id)
    
    # Don't allow deleting yourself
    if user.id == current_user.id:
        flash('You cannot delete your own account.')
        return redirect(url_for('users'))
    
    # Delete all MBOs associated with the user
    MBO.query.filter_by(user_id=user.id).delete()
    
    db.session.delete(user)
    db.session.commit()
    
    flash(f'User {user.first_name} {user.last_name} and all associated MBOs have been deleted.')
    return redirect(url_for('users'))

@app.route('/reset_password/<int:user_id>', methods=['POST'])
@login_required
def reset_password(user_id):
    """Reset a user's password to a default value (admin function)."""
    if current_user.role != 'Manager':
        flash('You do not have permission to reset passwords.')
        return redirect(url_for('dashboard'))
    
    user = User.query.get_or_404(user_id)
    
    # Only allow resetting Admin user passwords
    if user.role != 'Admin':
        flash('You can only reset Admin user passwords.')
        return redirect(url_for('users'))
    
    # Set a default password
    default_password = 'ChangeMe123!'
    user.set_password(default_password)
    
    db.session.commit()
    flash(f'Password for {user.first_name} {user.last_name} has been reset to "{default_password}"')
    return redirect(url_for('users'))

@app.route('/upload_profile_picture', methods=['POST'])
@login_required
def upload_profile_picture():
    """Upload a profile picture."""
    if 'profile_picture' not in request.files:
        flash('No file part')
        return redirect(url_for('profile'))
    
    file = request.files['profile_picture']
    
    if file.filename == '':
        flash('No selected file')
        return redirect(url_for('profile'))
    
    if file:
        try:
            # Using the improved local file storage for profile pictures
            from app.utils.file_utils import save_profile_picture
            
            # Save the profile picture locally with standardized naming
            path = save_profile_picture(file, current_user.id)
            
            if path:
                # S3 references have been removed
                
                # Update the profile picture path
                current_user.profile_picture = path
                
                # Update timestamp for cache busting
                current_user.profile_picture_updated_at = datetime.utcnow()
                
                db.session.commit()
                flash('Profile picture updated successfully!')
            else:
                flash('Failed to save profile picture', 'error')
        except Exception as e:
            flash(f'Error: {str(e)}', 'error')
    
    return redirect(url_for('profile'))

@app.route('/remove_profile_picture', methods=['POST'])
@login_required
def remove_profile_picture():
    """Remove the user's profile picture and revert to default."""
    try:
        # S3 functionality has been removed
        
        # Check if user has a local profile picture
        if current_user.profile_picture and current_user.profile_picture.startswith('/static/uploads/'):
            try:
                # Import here to avoid circular imports
                from app.utils.file_utils import delete_user_profile_pictures
                
                # Delete local profile pictures
                delete_user_profile_pictures(current_user.id)
            except Exception as e:
                print(f"Warning: Failed to delete local profile picture: {str(e)}")
        
        # Reset profile picture fields
        current_user.profile_picture = 'default.jpg'  # Set to default.jpg instead of None to match template condition
        
        db.session.commit()
        flash('Profile picture removed successfully!')
    except Exception as e:
        flash(f'Error removing profile picture: {str(e)}', 'error')
    
    # Check which page the user came from
    referer = request.referrer
    if referer and 'profile' in referer:
        return redirect(url_for('profile'))
    else:
        return redirect(url_for('user_profile'))

@app.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    """Edit a user's profile (manager function)."""
    # Check if current user is a manager
    if current_user.role != 'Manager':
        flash('You do not have permission to edit user profiles.')
        return redirect(url_for('dashboard'))
    
    # Get the user to edit
    user = User.query.get_or_404(user_id)
    
    # Get all managers for the dropdown
    managers = User.query.filter_by(role='Manager').all()
    
    if request.method == 'POST':
        # Update user information
        user.first_name = request.form['first_name']
        user.last_name = request.form['last_name']
        user.position = request.form.get('position', '')
        user.region = request.form.get('region', 'EMEA')
        user.role = request.form.get('role', 'Employee')
        user.email_notifications = 'email_notifications' in request.form
        
        # Update quarter compensation if provided
        quarter_compensation = request.form.get('quarter_compensation', '')
        if quarter_compensation:
            try:
                user.quarter_compensation = float(quarter_compensation)
            except ValueError:
                flash('Invalid compensation value. Please enter a valid number.', 'error')
        else:
            user.quarter_compensation = None
        
        # Handle manager selection
        manager_id = request.form.get('manager_id')
        if manager_id:
            user.manager_id = int(manager_id)
        else:
            user.manager_id = None
        
        # Handle password change if provided
        new_password = request.form.get('new_password')
        if new_password:
            user.set_password(new_password)
        
        db.session.commit()
        flash(f'Profile for {user.first_name} {user.last_name} updated successfully!')
        return redirect(url_for('users'))
    
    return render_template('edit_user_profile.html', user=user, managers=managers)