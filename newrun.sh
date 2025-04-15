#!/bin/bash
set -e

echo "###########################################"
echo "#  SnapLogic SEs MBO Tracker Deployment   #"
echo "###########################################"
echo ""

# Set environment variables
export FLASK_APP=run:app
export FLASK_ENV=development

# Free port 5000 if it is in use
echo "Freeing port 5000..."
lsof -ti:5000 | xargs kill -9 || echo "No process using port 5000."

# Activate the virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Start the Flask application on port 5000
echo "Starting Flask app on port 5000..."
python -m flask run --port 5000
