#!/bin/bash

# run_backend.sh - One-command script to run the Adaptive Learning Backend
# This script handles environment setup, dependency installation, and server startup

# Color codes for better readability
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Display banner
echo -e "${BLUE}====================================="
echo "  Adaptive Learning Backend Runner  "
echo -e "=====================================${NC}"

# Function to check if Python virtual environment exists
check_venv() {
  if [ ! -d "backend/bin" ]; then
    echo -e "${YELLOW}Virtual environment not found. Creating...${NC}"
    python -m venv backend
    return 1
  fi
  return 0
}

# Function to check if dependencies are installed
check_deps() {
  source backend/bin/activate
  if ! pip freeze | grep -q "fastapi"; then
    echo -e "${YELLOW}Dependencies not installed. Installing...${NC}"
    pip install -r requirements.txt
    echo -e "${GREEN}Dependencies installed successfully.${NC}"
  fi
}

# Function to create .env file if it doesn't exist
setup_env() {
  if [ ! -f ".env" ]; then
    echo -e "${YELLOW}Creating default .env file...${NC}"
    cat > .env << EOF
# API Configuration
API_PORT=5000
API_HOST=0.0.0.0
LOG_LEVEL=info

# Database Configuration
USE_IN_MEMORY=true
FALLBACK_QUESTIONS_PATH=sample_questions.json

# Adaptive Learning Settings
DEFAULT_QUESTION_COUNT=5
BKT_INIT_MASTERY=0.4
EOF
    echo -e "${GREEN}.env file created successfully.${NC}"
  fi
}

# Parse arguments
mode="foreground"
use_firebase=false
install_only=false
help=false

for arg in "$@"; do
  case $arg in
    --background|-b)
      mode="background"
      shift
      ;;
    --firebase|-f)
      use_firebase=true
      shift
      ;;
    --install|-i)
      install_only=true
      shift
      ;;
    --help|-h)
      help=true
      shift
      ;;
    *)
      # Unknown option
      ;;
  esac
done

# Show help
if [ "$help" = true ]; then
  echo -e "${BLUE}Usage: ./run_backend.sh [OPTIONS]${NC}"
  echo ""
  echo "Options:"
  echo "  --background, -b    Run the server in the background"
  echo "  --firebase, -f      Use Firebase database instead of in-memory database"
  echo "  --install, -i       Only install dependencies, don't start server"
  echo "  --help, -h          Show this help message"
  echo ""
  echo "Examples:"
  echo "  ./run_backend.sh              # Run in foreground with in-memory database"
  echo "  ./run_backend.sh -b           # Run in background with in-memory database"
  echo "  ./run_backend.sh -f           # Run in foreground with Firebase database"
  echo "  ./run_backend.sh -b -f        # Run in background with Firebase database"
  echo "  ./run_backend.sh -i           # Only install dependencies"
  exit 0
fi

# Setup virtual environment and dependencies
check_venv
venv_created=$?
if [ $venv_created -eq 1 ]; then
  source backend/bin/activate
  echo -e "${YELLOW}Installing dependencies...${NC}"
  pip install -r requirements.txt
  echo -e "${GREEN}Dependencies installed successfully.${NC}"
else
  check_deps
fi

# If install only, exit after dependencies are installed
if [ "$install_only" = true ]; then
  echo -e "${GREEN}Installation completed. Use './run_backend.sh' to start the server.${NC}"
  exit 0
fi

# Setup environment
setup_env

# Activate virtual environment
source backend/bin/activate

# Configure database mode
if [ "$use_firebase" = true ]; then
  echo -e "${YELLOW}Using Firebase database${NC}"
  export USE_IN_MEMORY=false
  
  # Check for Firebase credentials
  if [ ! -f "firebase/credentials/firebase-credentials.json" ]; then
    echo -e "${YELLOW}Warning: Firebase credentials not found. Please make sure to set up Firebase credentials.${NC}"
    echo "See docs/firebase/README.md for instructions."
  fi
else
  echo -e "${YELLOW}Using in-memory database${NC}"
  export USE_IN_MEMORY=true
  export FALLBACK_QUESTIONS_PATH=sample_questions.json
fi

# Run server
cd backend

if [ "$mode" = "background" ]; then
  echo -e "${YELLOW}Starting server in the background...${NC}"
  nohup python main.py > server.log 2>&1 &
  SERVER_PID=$!
  echo -e "${GREEN}Server is running in the background. Process ID: ${SERVER_PID}${NC}"
  echo "API available at: http://localhost:5000"
  echo "API Documentation: http://localhost:5000/docs"
  echo ""
  echo "To view logs: tail -f backend/server.log"
  echo "To stop the server: pkill -f 'python main.py'"
else
  echo -e "${YELLOW}Starting server in the foreground...${NC}"
  echo "API will be available at: http://localhost:5000"
  echo "API Documentation: http://localhost:5000/docs"
  echo -e "${YELLOW}Press Ctrl+C to stop the server${NC}"
  echo ""
  python main.py
  # The script will wait here until the server is stopped
fi

# Deactivate virtual environment when done (only reaches here if running in foreground)
if [ "$mode" = "foreground" ]; then
  deactivate
fi