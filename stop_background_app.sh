#!/bin/bash

# Check if the PID file exists
if [ -f "gunicorn.pid" ]; then
    # Read the PID from the file
    pid=$(cat gunicorn.pid)
    
    # Check if the process is still running
    if ps -p $pid > /dev/null; then
        echo "Stopping application with PID: $pid"
        kill -9 $pid
        echo "Application stopped."
    else
        echo "Application is not running (PID: $pid)."
    fi
    
    # Remove the PID file
    rm gunicorn.pid
    echo "PID file removed."
else
    # Check if there's any process using port 5000
    pid=$(lsof -t -i:5000)
    if [ -n "$pid" ]; then
        echo "Found process using port 5000 with PID: $pid"
        echo "Stopping process..."
        kill -9 $pid
        echo "Process stopped."
    else
        echo "No application found running on port 5000."
    fi
fi

echo "If you want to start the application again, run: ./run_in_background.sh"