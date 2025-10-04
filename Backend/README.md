# Adaptive Learning Backend

A FastAPI backend implementing a Bayesian Knowledge Tracing (BKT) algorithm for adaptive learning.

## Quick Start

1. **One-Command Setup & Run** (Recommended):
   ```bash
   # Run server in foreground with in-memory database
   ./run_backend.sh
   
   # Or run in background
   ./run_backend.sh -b
   
   # To use Firebase database instead of in-memory
   ./run_backend.sh -f
   
   # To see all options
   ./run_backend.sh --help
   ```
   This comprehensive script handles everything: virtual environment setup, 
   dependency installation, environment configuration, and server startup.

2. **For Frontend Developers**:
   ```bash
   # Option 1: Start the server in the foreground
   ./start_server.sh
   
   # Option 2: Start the server in the background (better for frontend development)
   ./frontend_dev.sh  # Start the server in the background
   ./frontend_start.sh  # Check the server status and access API
   ```
   These scripts automatically set up and start the server with an in-memory database.
   See the [Frontend Developer Guide](docs/frontend-guide.md) for more details.

3. **Manual Setup**:
   ```bash
   python -m venv backend
   source backend/bin/activate  # On Windows: backend\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Environment configuration**:
   ```bash
   cp .env.example .env
   # Edit .env file with your settings
   ```

4. **Run the application**:
   ```bash
   cd backend
   python main.py
   ```

5. **Access the API**:
   - API documentation: http://localhost:5000/docs
   - API endpoints: http://localhost:5000/api/...

## Documentation

- [Frontend Developer Guide](docs/frontend-guide.md)
- [API Documentation](docs/api/README.md)
- [Firebase Setup](docs/firebase/README.md)
- [Deployment Guide](docs/deployment/README.md)

## Features

- **Adaptive Assessment**: Dynamically adjusts question difficulty based on user responses
- **BKT Model**: Tracks knowledge state using Bayesian Knowledge Tracing
- **Learning Path Generation**: Creates personalized learning paths based on assessment results
- **In-Memory Fallback**: Can operate without Firebase for testing and development

## Development Options

### Using In-Memory Database (for frontend development)

```bash
# In your .env file
USE_IN_MEMORY=true
```

### Using Firebase Database

1. Set up Firebase credentials following the [Firebase Setup Guide](docs/firebase/README.md)
2. Update your .env file:
```bash
USE_IN_MEMORY=false
FIREBASE_CREDENTIALS_PATH=firebase/credentials/firebase-credentials.json
```