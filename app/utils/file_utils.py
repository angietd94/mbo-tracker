"""
Utility functions for handling file uploads locally.
"""
import os
import uuid
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