#!/bin/bash

# Frontend development script for Adaptive Learning Backend
# This script forces the use of the in-memory database with sample questions

# Display header
echo "====================================="
echo "  Adaptive Learning API for Frontend "
echo "====================================="

# Activate the virtual environment
source backend/bin/activate

# Create a temporary .env file for frontend development
cat > .env << EOL
# Frontend Development Environment
USE_IN_MEMORY=true
FALLBACK_QUESTIONS_PATH=sample_questions.json
EOL

echo "Created frontend development environment"
echo "Using in-memory database with sample questions"
echo "API will be available at: http://localhost:5000"
echo "API Documentation: http://localhost:5000/docs"
echo ""
echo "Press Ctrl+C to stop the server"

# Run the server in the background with nohup
cd backend
nohup python main.py > server.log 2>&1 &
echo "Server is running in the background. Process ID: $!"
echo "To view logs: tail -f backend/server.log"
echo "To stop the server: pkill -f 'python main.py'"