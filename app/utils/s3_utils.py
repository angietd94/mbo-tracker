"""
Utility functions for interacting with AWS S3.
"""
import os
import uuid
import boto3
from werkzeug.utils import secure_filename

# S3 bucket name
S3_BUCKET = "mbo-solutions-engineer-data"
S3_REGION = "eu-west-3"

def get_s3_client():
    """
    Create and return an S3 client.
    """
    try:
        return boto3.client(
            's3',
            region_name=S3_REGION,
            aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY')
        )
    except Exception as e:
        print(f"Error creating S3 client: {e}")
        return None

def upload_file_to_s3(file, acl="public-read"):
    """
    Upload a file to S3 bucket and return the URL.
    
    Args:
        file: File object to upload
        acl: Access control list for the file (default: public-read)
        
    Returns:
        URL of the uploaded file
    """
    if not file:
        return None
    
    # Create a unique filename
    filename = secure_filename(file.filename)
    unique_filename = f"{uuid.uuid4().hex}_{filename}"
    
    # Get S3 client
    s3_client = get_s3_client()
    
    # If S3 client is not available, return a default profile picture URL
    if not s3_client:
        print("S3 client not available, using default profile picture")
        return "/static/img/default_profile.svg"
    
    try:
        # Upload file to S3
        s3_client.upload_fileobj(
            file,
            S3_BUCKET,
            f"profile_pictures/{unique_filename}",
            ExtraArgs={
                "ACL": acl,
                "ContentType": file.content_type
            }
        )
        
        # Generate URL
        url = f"https://{S3_BUCKET}.s3.{S3_REGION}.amazonaws.com/profile_pictures/{unique_filename}"
        return url
    except Exception as e:
        print(f"Error uploading file to S3: {e}")
        # Return a default profile picture URL in case of error
        return "/static/img/default_profile.svg"