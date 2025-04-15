#!/bin/bash

# Script to clean up unnecessary files in the project root directory

echo "Cleaning up unnecessary files..."

# Remove macOS system files
rm -f .DS_Store

# Remove backup and test files
rm -f dashboard-that-works.html
rm -f "layout copy.html"

# Remove redundant scripts
rm -f cleandeploy.sh
rm -f newrun.sh
rm -f run-ec2.sh
rm -f run.sh

# Keep only the necessary files:
# - .env.example (for reference)
# - .gitignore
# - README.md
# - requirements.txt
# - restart_app.sh (main script to restart the app)
# - run.py (main Python entry point)
# - security-implementation-plan.md (documentation)
# - upload_to_github.sh (for GitHub uploads)

echo "Cleanup complete!"