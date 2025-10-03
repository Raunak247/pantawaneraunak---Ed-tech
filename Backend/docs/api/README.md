# API Documentation

This document describes the endpoints available in the Adaptive Learning API.

## Base URL

All endpoints are prefixed with `/api`

## Authentication

Currently, endpoints are not authenticated, but user_id is required for most operations.

## Endpoints

### Subjects

#### GET `/api/subjects/`

Returns all available subjects with their skills and statistics.

**Response**:
```json
{
  "subjects": [
    {
      "id": "python",
      "name": "Python",
      "description": "Learn and master Python",
      "question_count": 14,
      "skills": {
        "basic_syntax": {
          "name": "Basic Syntax",
          "question_count": 4
        },
        // more skills...
      },
      "difficulty_distribution": {
        "very_easy": 3,
        "easy": 4,
        "medium": 4,
        "hard": 3
      }
    },
    // more subjects...
  ]
}
```

### Assessment

#### POST `/api/assessment/start`

Start an assessment for a user in a specific subject.

**Request**:
```json
{
  "user_id": "test_user",
  "subject": "python",
  "question_count": 5
}
```

**Response**:
```json
{
  "assessment_id": "ea8ac512-bfd0-45e7-8fa1-bd3690a56b28",
  "subject": "python",
  "total_questions": 5,
  "current_question_index": 0,
  "question": {
    "id": "py_basics_1",
    "text": "What is the correct way to create a variable in Python?",
    "options": ["var x = 5;", "x := 5", "x = 5", "int x = 5;"],
    "skill": "basic_syntax"
  }
}
```

#### POST `/api/assessment/answer`

Submit an answer for a question in an ongoing assessment.

**Request**:
```json
{
  "assessment_id": "ea8ac512-bfd0-45e7-8fa1-bd3690a56b28",
  "question_id": "py_basics_1",
  "answer": "x = 5"
}
```

**Response**:
```json
{
  "is_correct": true,
  "correct_answer": "x = 5",
  "skill": "basic_syntax",
  "assessment_id": "ea8ac512-bfd0-45e7-8fa1-bd3690a56b28",
  "is_complete": false,
  "current_question_index": 1,
  "total_questions": 5,
  "next_question": {
    "id": "py_loops_1",
    "text": "Which statement is used to create a loop in Python?",
    "options": ["loop:", "while:", "for:", "repeat:"],
    "skill": "loops"
  }
}
```

#### GET `/api/assessment/{assessment_id}/results`

Get the results of a completed assessment.

**Response**:
```json
{
  "assessment_id": "ea8ac512-bfd0-45e7-8fa1-bd3690a56b28",
  "user_id": "test_user",
  "subject": "python",
  "score": {
    "correct": 4,
    "total": 5,
    "percentage": 80.0
  },
  "skill_masteries": {
    "basic_syntax": 0.75,
    "loops": 0.65
    // more skills...
  },
  "learning_path": {
    // learning path details...
  }
}
```

For more details, see the [complete API specification](https://localhost:5000/docs) when the server is running.