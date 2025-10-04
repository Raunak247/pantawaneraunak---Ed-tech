# Frontend Developer Guide

This guide helps frontend developers set up and interact with the Adaptive Learning Backend API.

## Quick Setup

1. **Run the server**:

   **Option A: Run in foreground mode (for debugging)**
   ```bash
   ./start_server.sh
   ```
   This script:
   - Activates the Python virtual environment
   - Creates a `.env` file if needed
   - Starts the server on http://localhost:5000 in the foreground

   **Option B: Run in background mode (better for frontend development)**
   ```bash
   ./frontend_dev.sh
   ```
   This script:
   - Starts the server in the background using nohup
   - Logs output to server.log
   - Configures in-memory database by default
   - Returns control to terminal immediately

   After starting the server in the background, you can check its status:
   ```bash
   ./frontend_start.sh
   ```
   This will:
   - Check if the server is running
   - Display the process ID and status
   - Show the last few lines of the server log
   - Provide commands for viewing full logs
   - Offer to open API documentation in the browser

2. **First time setup**:
   ```bash
   ./start_server.sh --install
   ```
   Use this flag the first time to install all required packages.

## API Overview

The backend provides a RESTful API for adaptive learning functionality:

### Base URL
All endpoints are prefixed with `/api`

### Key Endpoints

#### Subjects
- `GET /api/subjects/` - Get all available subjects with their skills

#### Assessment
- `POST /api/assessment/start` - Start a new assessment
- `POST /api/assessment/answer` - Submit an answer
- `GET /api/assessment/{id}/results` - Get assessment results

#### Learning Paths
- `GET /api/learning/path/{user_id}/{subject}` - Get learning path for a user

### Authentication

Currently, endpoints are not authenticated, but `user_id` is required for most operations.

## Testing the API

1. **API Documentation**:
   - Interactive API documentation is available at http://localhost:5000/docs
   - You can test all endpoints directly from this page

2. **Sample User ID**:
   - Use `"test_user"` for testing
   - The backend uses in-memory storage by default for easy frontend development

3. **Example: Starting an Assessment**:

   ```javascript
   // Sample fetch request
   fetch('http://localhost:5000/api/assessment/start', {
     method: 'POST',
     headers: {
       'Content-Type': 'application/json'
     },
     body: JSON.stringify({
       user_id: 'test_user',
       subject: 'javascript',
       question_count: 5
     })
   })
   .then(response => response.json())
   .then(data => console.log(data));
   ```

4. **CORS Support**:
   - The API has CORS enabled and accepts requests from any origin
   - No additional configuration needed for local development

## Data Structure

Important objects your frontend will work with:

### Subject
```json
{
  "id": "javascript",
  "name": "JavaScript",
  "description": "Learn and master JavaScript",
  "skills": {
    "basic_syntax": { "name": "Basic Syntax", "question_count": 4 },
    "functions": { "name": "Functions", "question_count": 2 }
  }
}
```

### Question
```json
{
  "id": "js_basics_1",
  "text": "How do you declare a variable in JavaScript?",
  "options": ["var x;", "variable x;", "v x;", "x = 5;"],
  "skill": "basic_syntax"
}
```

### Assessment Results
```json
{
  "score": { "correct": 4, "total": 5, "percentage": 80.0 },
  "skill_masteries": { "basic_syntax": 0.75, "functions": 0.65 },
  "learning_path": {
    "modules": [
      {
        "id": "js_basic_syntax",
        "title": "JavaScript Basics",
        "priority": "high"
      }
    ]
  }
}
```

## Need More Help?

See the detailed [API Documentation](api/README.md) or check the full [API Specification](api/FULL_API_SPEC.md).