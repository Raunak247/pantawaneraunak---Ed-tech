# Adaptive Learning Backend

A FastAPI backend implementing a Bayesian Knowledge Tracing (BKT) algorithm for adaptive learning.

## Quick Start

1. **Setup environment**:
   ```bash
   python -m venv backend
   source backend/bin/activate  # On Windows: backend\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Environment configuration**:
   ```bash
   cp .env.example .env
   # Edit .env file with your settings
   ```

3. **Run the application**:
   ```bash
   cd backend
   python main.py
   ```

4. **Access the API**:
   - API documentation: http://localhost:5000/docs
   - API endpoints: http://localhost:5000/api/...

## Documentation

- [API Documentation](docs/api/README.md)
- [Firebase Setup](docs/firebase/README.md)
- [Deployment Guide](docs/deployment/README.md)

## Features

- **Adaptive Assessment**: Dynamically adjusts question difficulty based on user responses
- **BKT Model**: Tracks knowledge state using Bayesian Knowledge Tracing
- **Learning Path Generation**: Creates personalized learning paths based on assessment results
- **In-Memory Fallback**: Can operate without Firebase for testing and development

4. Update the `.env` file with your Firebase configuration:
```
FIREBASE_CREDENTIALS_PATH=/path/to/your/firebase-credentials.json
FIREBASE_PROJECT_ID=your-firebase-project-id
USE_IN_MEMORY=false
```

5. Test your Firebase connection:
```bash
python test_firebase_connection.py
```

## Fallback Database

This application includes a fallback database mechanism to ensure continuous operation even when the primary database (Firebase) is unavailable:

1. The system first tries to connect to Firebase Firestore using your credentials
2. If Firebase connection fails or if the questions collection is empty, the system falls back to using:
   - Local `questions.json` file (if available)
   - `sample_questions.json` file (if questions.json is not found)

The fallback database contains questions across three subjects:
- Mathematics (various difficulty levels)
- Science (various difficulty levels)
- Python programming (various difficulty levels)

You can customize the fallback database by editing the `sample_questions.json` file or by setting the path in the `.env` file:
```
FALLBACK_QUESTIONS_PATH=/path/to/your/custom-questions.json
```

## Running the Application

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Start the server:
```bash
python -m backend.main
```

3. Access the API at http://localhost:5000

## API Documentation

API documentation is available at http://localhost:5000/docs when the server is running.

## Enhanced Bayesian Knowledge Tracing (BKT) Model

The system implements an enhanced Bayesian Knowledge Tracing model for adaptive learning that:

1. **Tracks Skill Mastery**: Continuously updates a student's mastery level for each skill based on their performance
2. **Adapts to Difficulty**: Adjusts parameters based on question difficulty (very_easy, easy, medium, hard)
3. **Personalizes Learning Paths**: Generates custom learning paths based on assessment results
4. **Recommends Next Questions**: Intelligently selects the next most appropriate question for each learner

### Key Features of the BKT Model:

- **Adaptive Question Selection**: Chooses questions that target a student's weakest skills
- **Mastery Analysis**: Provides detailed analysis of skill masteries and learning progress
- **Learning Recommendations**: Generates personalized learning modules based on performance
- **Difficulty Adjustment**: Takes question difficulty into account when updating skill mastery

### Using the BKT API Endpoints:

1. **Get Next Question**:
   ```
   GET /api/learning/next-question/{user_id}/{subject}
   ```
   Returns the most appropriate next question for a user based on their current skill mastery

2. **Submit Answer**:
   ```
   POST /api/learning/submit-answer
   ```
   Submit an answer and get instant feedback with updated skill mastery levels

3. **Generate Learning Path**:
   ```
   GET /api/assessment/results/{assessment_id}
   ```
   Get a personalized learning path based on assessment results with recommendations by skill