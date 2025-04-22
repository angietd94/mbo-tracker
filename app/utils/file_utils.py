"""
Utility functions for handling file uploads locally.
"""
import os
import uuid
import time
import glob
from werkzeug.utils import secure_filename
from flask import url_for

# Upload folder for profile pictures
UPLOAD_FOLDER = 'app/static/uploads/profile_pictures'

def upload_file_locally(file):
    """
    Upload a file to local storage and return the URL.
    
    Args:
        file: File object to upload
        
    Returns:
        URL of the uploaded file
    """
    if not file:
        return None
    
    # Create a unique filename
    filename = secure_filename(file.filename)
    unique_filename = f"{uuid.uuid4().hex}_{filename}"
    
    # Ensure upload directory exists
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    
    try:
        # Save file to local storage
        file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
        file.save(file_path)
        
        # Generate URL
        url = url_for('static', filename=f'uploads/profile_pictures/{unique_filename}')
        return url
    except Exception as e:
        print(f"Error uploading file locally: {e}")
        return "/static/img/default_profile.svg"

def save_profile_picture(file, user_id=None):
    """
    Save a user's profile picture, ensuring only one exists per user.
    Deletes any previous profile pictures for this user.
    
    Args:
        file: File object to upload
        user_id: The user's ID (required for proper file management)
        
    Returns:
        URL path to the saved profile picture
    """
    if not file or not user_id:
        return "/static/img/Sample_User_Icon.png"
    
    try:
        # Get file extension from original filename
        original_filename = secure_filename(file.filename)
        _, extension = os.path.splitext(original_filename)
        if not extension:
            extension = ".png"  # Default to PNG if no extension
        
        # First, delete any existing profile pictures for this user
        delete_user_profile_pictures(user_id)
        
        # Create a standardized filename that includes the user ID and timestamp
        # This makes it easier to identify and manage user profile pictures
        timestamp = int(time.time())
        filename = f"profile-{user_id}-{timestamp}{extension}"
        
        # Ensure upload directory exists
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        
        # Save file to local storage
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)
        
        # Return the relative path for storage in the database
        return f"/static/uploads/profile_pictures/{filename}"
    except Exception as e:
        print(f"Error saving profile picture: {e}")
        return "/static/img/Sample_User_Icon.png"

def delete_user_profile_pictures(user_id):
    """
    Delete all existing profile pictures for a specific user.
    
    Args:
        user_id: The user's ID
    """
    if not user_id:
        return
    
    try:
        # Find all profile pictures for this user using a pattern match
        pattern = os.path.join(UPLOAD_FOLDER, f"profile-{user_id}-*")
        existing_files = glob.glob(pattern)
        
        # Delete each file found
        for file_path in existing_files:
            print(f"Deleting old profile picture: {file_path}")
            os.remove(file_path)
    except Exception as e:
        print(f"Error deleting old profile pictures: {e}")