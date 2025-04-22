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

# Change to the script's directory
cd "$(dirname "$0")"

# Start the application with gunicorn in the background
echo "Starting the application with gunicorn in the background..."
nohup gunicorn -w 4 -b 0.0.0.0:5000 "run:app" > gunicorn.log 2>&1 &

# Save the PID to a file
echo $! > gunicorn.pid
echo "Application started in the background with PID: $!"
echo "You can now close Visual Studio and the application will continue running."
echo "To stop the application, run: ./stop_background_app.sh"