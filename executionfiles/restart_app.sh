#!/bin/bash

# Kill any process using port 5000
echo "Checking for processes using port 5000..."
lsof -ti:5000 | xargs kill -9 2>/dev/null || echo "No process found using port 5000."

# Start the application
echo "Starting the application..."
cd "$(dirname "$0")"
python3 run.py
