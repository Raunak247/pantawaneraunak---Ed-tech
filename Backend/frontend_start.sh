#!/bin/bash

# frontend_start.sh - Script to check status and provide information about the backend API
# This script is designed to work alongside frontend_dev.sh

echo "====================================="
echo "  Adaptive Learning Backend Status   "
echo "====================================="

# Check if server is running
if pgrep -f "python main.py" > /dev/null; then
    echo "✅ API Server is RUNNING"
    SERVER_PID=$(pgrep -f "python main.py")
    echo "   Process ID: $SERVER_PID"
    echo ""
    echo "API is available at: http://localhost:5000"
    echo "API Documentation: http://localhost:5000/docs"
    echo ""
    echo "Last few lines from the server log:"
    echo "-----------------------------------"
    tail -n 5 backend/server.log
    echo "-----------------------------------"
    echo ""
    echo "📖 To view full logs: tail -f backend/server.log"
    echo "🛑 To stop the server: pkill -f 'python main.py'"

    # Attempt to open the API docs in the default browser
    echo ""
    echo "Would you like to open the API documentation in your browser? (y/n)"
    read -r response
    if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        if command -v xdg-open > /dev/null; then
            xdg-open http://localhost:5000/docs &
        elif command -v open > /dev/null; then
            open http://localhost:5000/docs &
        else
            echo "Could not open browser automatically. Please visit http://localhost:5000/docs"
        fi
    fi
else
    echo "❌ API Server is NOT RUNNING"
    echo ""
    echo "To start the server, run: ./frontend_dev.sh"
    echo ""
fi