#!/bin/bash

<<<<<<< HEAD
<<<<<<< HEAD
=======
# Run cleanup script to remove unnecessary files
echo "Running cleanup script..."
cd "$(dirname "$0")"
./cleanup.sh

>>>>>>> 6b472e0 (Update MBO Tracker application)
=======
>>>>>>> a6a29bae4bb6e51517b81b41b9cdf7b89a26a842
# Kill any process using port 5000
echo "Checking for processes using port 5000..."
lsof -ti:5000 | xargs kill -9 2>/dev/null || echo "No process found using port 5000."

<<<<<<< HEAD
<<<<<<< HEAD
# Start the application
echo "Starting the application..."
cd "$(dirname "$0")"
python3 run.py
=======
# Run database migrations
echo "Running database migrations..."
python3 -c "from app import app, db; with app.app_context(): db.create_all()"

# Check if migrations directory exists
if [ -d "migrations" ]; then
    # Fix the multiple heads issue by creating a merge migration
    echo "Creating a merge migration..."
    flask db merge heads -m "merge multiple heads"
    
    # Run the migrations
    echo "Running migrations..."
    flask db upgrade
fi

# Start the application
echo "Starting the application..."
python3 run.py &

# Ask if the user wants to upload to GitHub
echo ""
echo "Do you want to upload the latest changes to GitHub? (y/n)"
read -r upload_choice

if [[ "$upload_choice" =~ ^[Yy]$ ]]; then
    echo "Running upload_to_github.sh script..."
    ./upload_to_github.sh
else
    echo "Skipping GitHub upload."
fi

echo "Application is running in the background. Press Ctrl+C to exit this script."
>>>>>>> 6b472e0 (Update MBO Tracker application)
=======
# Start the application
echo "Starting the application..."
cd "$(dirname "$0")"
python3 run.py
>>>>>>> a6a29bae4bb6e51517b81b41b9cdf7b89a26a842
