#!/bin/bash

# frontend_start.sh - Script to start the Adaptive Learning Backend for frontend developers
# This script bypasses Firebase credential checks completely

echo "====================================="
echo "  Adaptive Learning Backend Starter  "
echo "====================================="
echo "  FRONTEND DEVELOPMENT MODE  "
echo "====================================="

# Activate the virtual environment
source backend/bin/activate

# Set environment variables to ensure in-memory database is used
export USE_IN_MEMORY=true
export FALLBACK_QUESTIONS_PATH=sample_questions.json

# Start the server
echo "Starting server in FRONTEND MODE (in-memory database)"
echo "The API will be available at http://localhost:5000"
echo "API Documentation is at http://localhost:5000/docs"
echo "Press Ctrl+C to stop the server"
echo ""

# Change to the backend directory and run the server
cd backend && python main.py

# Deactivate the virtual environment when done
deactivate