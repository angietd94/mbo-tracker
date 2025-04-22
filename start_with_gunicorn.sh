#!/bin/bash

# Kill any process using port 5000
echo "Checking for processes using port 5000..."
sudo lsof -ti:5000 | xargs sudo kill -9 2>/dev/null || echo "No process found using port 5000."

# Start the application with gunicorn
echo "Starting the application with gunicorn..."
cd "$(dirname "$0")"
gunicorn -w 4 -b 0.0.0.0:5000 "run:app"