#!/bin/bash

# Kill any process using port 5000
echo "Checking for processes using port 5000..."
pid=$(lsof -t -i:5000)
if [ -n "$pid" ]; then
    echo "Killing process $pid using port 5000..."
    kill -9 $pid
    echo "Process killed."
else
    echo "No process found using port 5000."
fi

# Start the application
echo "Starting the application..."
cd "$(dirname "$0")"
python3 run.py