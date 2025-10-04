#!/bin/bash

# start_server.sh - Script to start the Adaptive Learning Backend
# Created for frontend developers to easily run the API server

# Display header
echo "====================================="
echo "  Adaptive Learning Backend Starter  "
echo "====================================="

# Define color codes for better readability
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if the virtual environment exists
if [ ! -d "backend" ]; then
    echo -e "${RED}Error: Virtual environment 'backend' not found.${NC}"
    echo "Creating a new virtual environment..."
    python3 -m venv backend
    if [ $? -ne 0 ]; then
        echo -e "${RED}Failed to create virtual environment. Please install python3-venv package.${NC}"
        exit 1
    fi
fi

# Activate the virtual environment
echo -e "${YELLOW}Activating virtual environment...${NC}"
source backend/bin/activate

# Check if activation was successful
if [ $? -ne 0 ]; then
    echo -e "${RED}Failed to activate virtual environment.${NC}"
    exit 1
fi

# Install requirements if needed
if [ "$1" == "--install" ] || [ "$1" == "-i" ]; then
    echo -e "${YELLOW}Installing required packages...${NC}"
    pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo -e "${RED}Failed to install requirements.${NC}"
        exit 1
    fi
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}No .env file found. Creating from .env.example...${NC}"
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo -e "${GREEN}Created .env file from template. Using in-memory database by default.${NC}"
        # Ensure USE_IN_MEMORY is set to true for frontend development
        sed -i 's/USE_IN_MEMORY=.*/USE_IN_MEMORY=true/' .env
        # Comment out Firebase credentials path for frontend development
        sed -i 's/^FIREBASE_CREDENTIALS_PATH/#FIREBASE_CREDENTIALS_PATH/' .env
    else
        echo -e "${RED}No .env.example found. Creating a basic .env file...${NC}"
        echo "USE_IN_MEMORY=true" > .env
        echo "FALLBACK_QUESTIONS_PATH=sample_questions.json" >> .env
    fi
fi

# Start the server
echo -e "${YELLOW}Starting the server...${NC}"
echo -e "The API will be available at ${GREEN}http://localhost:5000${NC}"
echo -e "API Documentation is at ${GREEN}http://localhost:5000/docs${NC}"
echo -e "${YELLOW}Press Ctrl+C to stop the server${NC}"
echo ""

# Change to the backend directory
cd backend

# Start the server
python main.py

# If we get here, the server has stopped
echo ""
echo -e "${RED}Server has been stopped.${NC}"

# Deactivate the virtual environment
deactivate