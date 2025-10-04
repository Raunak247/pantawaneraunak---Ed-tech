# Adaptive Learning Backend

A FastAPI backend implementing a Bayesian Knowledge Tracing (BKT) algorithm for adaptive learning.

## Quick Start

1. **For Frontend Developers**:
   ```bash
   ./start_server.sh
   ```
   This script automatically sets up and starts the server with an in-memory database.
   See the [Frontend Developer Guide](docs/frontend-guide.md) for more details.

2. **Manual Setup**:
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