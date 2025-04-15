#!/bin/bash

<<<<<<< HEAD
# Script to upload the MBO Tracker project to an existing GitHub repository.
# This overwrites any local .git history and reinitializes from scratch.

GITHUB_USERNAME="angietd94"
REPO_NAME="mbo-tracker"
BRANCH_NAME="master"   # or "main", if your repo uses "main"
=======
# Script to upload the MBO Tracker project to GitHub
# This script will create a new repository and push the code to it

# Set variables
GITHUB_USERNAME="angietd94"
REPO_NAME="mbo-tracker"
>>>>>>> a6a29bae4bb6e51517b81b41b9cdf7b89a26a842

# Ask for GitHub token
echo "Please enter your GitHub Personal Access Token:"
read -s GITHUB_TOKEN

if [ -z "$GITHUB_TOKEN" ]; then
    echo "Error: GitHub token is required."
    exit 1
fi

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo "Git is not installed. Please install git and try again."
    exit 1
fi

<<<<<<< HEAD
# Optional: Remove existing .git directory (WARNING: erases local history)
if [ -d ".git" ]; then
    echo "Removing existing .git repository..."
=======
# Remove existing .git directory if it exists
if [ -d ".git" ]; then
    echo "Removing existing git repository..."
>>>>>>> a6a29bae4bb6e51517b81b41b9cdf7b89a26a842
    rm -rf .git
fi

# Initialize a new git repository
echo "Initializing git repository..."
git init

# Create .env.example file if it doesn't exist
if [ ! -f ".env.example" ]; then
    echo "Creating .env.example file..."
    cat > .env.example << EOL
# Flask application settings
SECRET_KEY=your_secret_key_here
DEBUG=False

# Database settings
DATABASE_URL=sqlite:///app.db

# Email settings
MAIL_SERVER=smtp.example.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your_email@example.com
MAIL_PASSWORD=your_email_password
MAIL_DEFAULT_SENDER=your_email@example.com

# Admin user settings
ADMIN_EMAIL=admin@example.com
ADMIN_PASSWORD=your_admin_password

# Security settings
SECURITY_PASSWORD_SALT=your_password_salt_here

<<<<<<< HEAD
# S3 settings
=======
# S3 settings (if using S3 for file storage)
>>>>>>> a6a29bae4bb6e51517b81b41b9cdf7b89a26a842
S3_BUCKET=your_bucket_name
S3_KEY=your_s3_key
S3_SECRET=your_s3_secret
S3_LOCATION=https://your_bucket_name.s3.amazonaws.com/

# Application URL
BASE_URL=http://localhost:5000
EOL
fi

<<<<<<< HEAD
# Check for and remove any .env files (optional)
echo "Checking for .env files..."
if [ -f ".env" ]; then
    echo "WARNING: Found .env file. This file contains sensitive information and will not be committed."
    echo "Creating a backup of .env as .env.backup..."
    cp .env .env.backup
fi

# Check for other sensitive files (optional)
echo "Checking for other sensitive files..."
SENSITIVE_FILES=$(find . -name "*.pem" -o -name "*.key" -o -name "*.crt" -o -name "*.log" -o -name "*.db" -o -name "*.sqlite")
if [ ! -z "$SENSITIVE_FILES" ]; then
    echo "WARNING: Found sensitive files that may contain secrets and won't be pushed if listed in .gitignore:"
=======
# Check for and remove any .env files
echo "Checking for .env files..."
if [ -f ".env" ]; then
    echo "WARNING: Found .env file. This file contains sensitive information and will not be included in the repository."
    echo "Creating a backup of .env file as .env.backup..."
    cp .env .env.backup
fi

# Check for any other sensitive files
echo "Checking for other sensitive files..."
SENSITIVE_FILES=$(find . -name "*.pem" -o -name "*.key" -o -name "*.crt" -o -name "*.log" -o -name "*.db" -o -name "*.sqlite")
if [ ! -z "$SENSITIVE_FILES" ]; then
    echo "WARNING: Found sensitive files that will not be included in the repository:"
>>>>>>> a6a29bae4bb6e51517b81b41b9cdf7b89a26a842
    echo "$SENSITIVE_FILES"
fi

# Add all files to git
echo "Adding files to git..."
git add .

# Commit changes
echo "Committing changes..."
<<<<<<< HEAD
git commit -m "Update MBO Tracker application"

# Add the remote repository (with token for initial push)
echo "Adding remote repository..."
git remote add origin https://$GITHUB_TOKEN@github.com/$GITHUB_USERNAME/$REPO_NAME.git

# Push to GitHub (first push)
echo "Pushing to GitHub..."
git push -u origin $BRANCH_NAME

# Remove token-based remote to avoid storing token in .git/config
git remote remove origin

# Re-add remote without the token
git remote add origin https://github.com/$GITHUB_USERNAME/$REPO_NAME.git

echo "Upload complete! View your repo at: https://github.com/$GITHUB_USERNAME/$REPO_NAME"
=======
git commit -m "Initial commit of MBO Tracker application"

# Create a new repository on GitHub using the GitHub API
echo "Creating new repository on GitHub..."
curl -X POST -H "Authorization: token $GITHUB_TOKEN" \
    -H "Accept: application/vnd.github.v3+json" \
    https://api.github.com/user/repos \
    -d "{\"name\":\"$REPO_NAME\",\"description\":\"Solutions Engineer MBO Tracker Application\",\"private\":false}"

# Add the remote repository
echo "Adding remote repository..."
git remote add origin https://$GITHUB_TOKEN@github.com/$GITHUB_USERNAME/$REPO_NAME.git

# Push to GitHub
echo "Pushing to GitHub..."
git push -u origin master

# Remove the remote with token to avoid leaking it in .git/config
git remote remove origin
git remote add origin https://github.com/$GITHUB_USERNAME/$REPO_NAME.git

echo "Upload complete! Your repository is now available at: https://github.com/$GITHUB_USERNAME/$REPO_NAME"
>>>>>>> a6a29bae4bb6e51517b81b41b9cdf7b89a26a842
