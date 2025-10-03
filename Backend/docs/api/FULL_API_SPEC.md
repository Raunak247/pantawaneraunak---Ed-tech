# Detailed API Specification

This document provides a complete reference for all API endpoints in the Adaptive Learning Platform.

[Full API documentation moved from API_DOCUMENTATION.md]# API Documentation for Adaptive Learning Platform

This document provides information on how to use the API endpoints for the Adaptive Learning Platform.

## Base URL

All API endpoints are relative to the base URL: `http://localhost:5000`

## Authentication

- For regular users, login using the `/api/users/login` endpoint to get a session
- For AIML team and analytics team, use the `/api/analytics` endpoints

## 1. User Management

### Register a New User
```
POST /api/users/register
```
**Request Body**:
```json
{
  "email": "user@example.com",
  "username": "username",
  "password": "password",
  "name": "Full Name"
}
```
**Response**:
```json
{
  "message": "User registered successfully",
  "user": {
    "user_id": "uuid-string",
    "email": "user@example.com",
    "username": "username",
    "name": "Full Name",
    "created_at": "2025-10-03T12:00:00Z"
  }
}
```

### User Login
```
POST /api/users/login
```
**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "password"
}
```
**Response**:
```json
{
  "message": "Login successful",
  "user": {
    "user_id": "uuid-string",
    "email": "user@example.com",
    "username": "username",
    "name": "Full Name",
    "created_at": "2025-10-03T12:00:00Z"
  },
  "session": {
    "user_id": "uuid-string",
    "timestamp": "2025-10-03T12:00:00Z"
  }
}
```

### Get User Profile
```
GET /api/users/{user_id}
```
**Response**:
```json
{
  "user_id": "uuid-string",
  "email": "user@example.com",
  "username": "username",
  "name": "Full Name",
  "created_at": "2025-10-03T12:00:00Z",
  "last_active": "2025-10-03T12:00:00Z"
}
```

### Update User Profile
```
PUT /api/users/{user_id}
```
**Request Body**:
```json
{
  "name": "New Name",
  "email": "new@example.com",
  "current_password": "current-password",
  "new_password": "new-password"
}
```
**Response**:
```json
{
  "message": "Profile updated successfully",
  "user": {
    "user_id": "uuid-string",
    "email": "new@example.com",
    "username": "username",
    "name": "New Name",
    "updated_at": "2025-10-03T12:00:00Z"
  }
}
```

### Get User Statistics
```
GET /api/users/{user_id}/stats
```
**Response**:
```json
{
  "user_id": "uuid-string",
  "username": "username",
  "assessment_stats": {
    "total": 5,
    "completed": 3,
    "completion_rate": 60.0,
    "average_score": 75.5
  },
  "learning_stats": {
    "modules_started": 10,
    "modules_completed": 6,
    "completion_rate": 60.0,
    "total_time_spent_minutes": 120
  },
  "by_subject": [
    {
      "name": "python",
      "assessments_taken": 3,
      "assessments_completed": 2,
      "average_score": 80.5,
      "modules_started": 6,
      "modules_completed": 4,
      "time_spent_minutes": 80
    },
    {
      "name": "math",
      "assessments_taken": 2,
      "assessments_completed": 1,
      "average_score": 70.0,
      "modules_started": 4,
      "modules_completed": 2,
      "time_spent_minutes": 40
    }
  ],
  "generated_at": "2025-10-03T12:00:00Z"
}
```

## 2. Subject Management

### Get All Subjects
```
GET /api/subjects/
```
**Response**:
```json
{
  "subjects": [
    {
      "id": "python",
      "name": "Python",
      "description": "Learn and master Python",
      "question_count": 24,
      "skills": {
        "basic_syntax": {
          "name": "Basic syntax",
          "question_count": 6
        },
        "functions": {
          "name": "Functions",
          "question_count": 4
        },
        "oop": {
          "name": "Oop",
          "question_count": 4
        }
      },
      "difficulty_distribution": {
        "very_easy": 6,
        "easy": 6,
        "medium": 6,
        "hard": 6
      }
    },
    {
      "id": "math",
      "name": "Math",
      "description": "Learn and master Math",
      "question_count": 20,
      "skills": {
        "algebra": {
          "name": "Algebra",
          "question_count": 5
        },
        "geometry": {
          "name": "Geometry",
          "question_count": 5
        }
      },
      "difficulty_distribution": {
        "very_easy": 5,
        "easy": 5,
        "medium": 5,
        "hard": 5
      }
    }
  ],
  "total": 2
}
```

### Get Subject Details
```
GET /api/subjects/{subject_id}
```
**Response**:
```json
{
  "id": "python",
  "name": "Python",
  "description": "Learn and master Python",
  "question_count": 24,
  "skills": [
    {
      "id": "basic_syntax",
      "name": "Basic syntax",
      "question_count": 6,
      "description": "Master basic syntax in python"
    },
    {
      "id": "functions",
      "name": "Functions",
      "question_count": 4,
      "description": "Master functions in python"
    }
  ],
  "difficulty_distribution": {
    "very_easy": 6,
    "easy": 6,
    "medium": 6,
    "hard": 6
  }
}
```

## 3. Assessment

### Start Assessment
```
POST /api/assessment/start
```
**Request Body**:
```json
{
  "user_id": "uuid-string",
  "subject": "python",
  "question_count": 10
}
```
**Response**:
```json
{
  "assessment_id": "uuid-string",
  "subject": "python",
  "total_questions": 10,
  "current_question_index": 0,
  "question": {
    "id": "python_easy_1",
    "text": "What is the output of print('Hello World')?",
    "options": ["Hello World", "Error", "None", "hello world"],
    "skill": "basic_syntax"
  }
}
```

### Submit Answer
```
POST /api/assessment/answer
```
**Request Body**:
```json
{
  "assessment_id": "uuid-string",
  "question_id": "python_easy_1",
  "answer": "Hello World"
}
```
**Response** (if not last question):
```json
{
  "is_correct": true,
  "correct_answer": "Hello World",
  "skill": "basic_syntax",
  "assessment_id": "uuid-string",
  "is_complete": false,
  "current_question_index": 1,
  "total_questions": 10,
  "next_question": {
    "id": "python_medium_1",
    "text": "What is a decorator in Python?",
    "options": ["A function that modifies another function", "A class method", "A type of loop", "A data structure"],
    "skill": "functions"
  }
}
```
**Response** (if last question):
```json
{
  "is_correct": true,
  "correct_answer": "Hello World",
  "skill": "basic_syntax",
  "assessment_id": "uuid-string",
  "is_complete": true,
  "message": "Assessment complete!"
}
```

### Get Assessment Results (BKT-powered)
```
GET /api/assessment/{assessment_id}/results
```
**Description**: Gets detailed assessment results and a personalized learning path generated by the enhanced BKT model

**Response**:
```json
{
  "assessment_id": "uuid-string",
  "user_id": "uuid-string",
  "subject": "python",
  "score": {
    "correct": 7,
    "total": 10,
    "percentage": 70.0
  },
  "skill_masteries": {
    "basic_syntax": 0.85,
    "functions": 0.65,
    "oop": 0.45
  },
  "completed_at": "2025-10-03T12:00:00Z",
  "learning_path": {
    "subject": "python",
    "strengths": ["basic_syntax"],
    "areas_for_improvement": ["oop"],
    "estimated_completion_time": "12 hours",
    "modules": [
      {
        "id": "python_remedial_oop",
        "title": "Building foundations in oop",
        "type": "remedial",
        "skill": "oop",
        "mastery_level": "basic",
        "recommended_duration": "2 hours",
        "priority": "high",
        "description": "Focus on fundamentals of oop to build a solid foundation"
      },
      {
        "id": "python_intermediate_functions",
        "title": "Strengthening your functions skills",
        "type": "practice",
        "skill": "functions",
        "mastery_level": "intermediate",
        "recommended_duration": "3 hours",
        "priority": "medium",
        "description": "Reinforce your understanding of functions through practice"
      },
      {
        "id": "python_advanced_basic_syntax",
        "title": "Mastering basic syntax",
        "type": "advanced",
        "skill": "basic_syntax",
        "mastery_level": "advanced",
        "recommended_duration": "4 hours",
        "priority": "low",
        "description": "Deepen your expertise in basic syntax with advanced concepts"
      }
    ],
    "performance_by_difficulty": {
      "very_easy": {"total": 3, "correct": 3, "percentage": 100},
      "easy": {"total": 3, "correct": 2, "percentage": 66.7},
      "medium": {"total": 2, "correct": 1, "percentage": 50.0},
      "hard": {"total": 2, "correct": 1, "percentage": 50.0}
    },
    "overall_mastery": 0.65,
    "recommendation_reason": "This personalized learning path is designed based on your assessment results. You showed strong understanding in basic_syntax and need more practice in oop. Overall mastery: 65.0%."
  }
}
```

## 4. Learning Path

### Get User Learning Path
```
GET /api/learning/path/{user_id}/{subject}
```
**Response**:
```json
{
  "learning_path": {
    "subject": "python",
    "strengths": ["basic_syntax"],
    "areas_for_improvement": ["oop"],
    "estimated_completion_time": "12 hours",
    "modules": [
      {
        "id": "python_remedial_oop",
        "title": "Building foundations in oop",
        "type": "remedial",
        "skill": "oop",
        "mastery_level": "basic",
        "recommended_duration": "2 hours",
        "priority": "high",
        "description": "Focus on fundamentals of oop to build a solid foundation",
        "current_progress": 25.0,
        "completed": false
      },
      {
        "id": "python_intermediate_functions",
        "title": "Strengthening your functions skills",
        "type": "practice",
        "skill": "functions",
        "mastery_level": "intermediate",
        "recommended_duration": "3 hours",
        "priority": "medium",
        "description": "Reinforce your understanding of functions through practice",
        "current_progress": 0.0,
        "completed": false
      }
    ],
    "recommendation_reason": "This personalized learning path is designed based on your assessment results."
  },
  "overall_progress": 12.5,
  "completed": false
}
```

### Get Next Question (BKT-powered)
```
GET /api/learning/next-question/{user_id}/{subject}
```
**Description**: Returns the next most appropriate question for a user based on their current skill mastery levels, calculated using the enhanced BKT model

**Response**:
```json
{
  "question": {
    "id": "q123",
    "text": "What is the output of print(2 + 2)?",
    "options": ["2", "4", "22", "Error"],
    "difficulty": "easy",
    "skill": "basic_syntax"
  },
  "selection_reason": "Targeting weak skill: basic_syntax (mastery: 0.45) with easy difficulty",
  "question_id": "q123",
  "skill": "basic_syntax",
  "difficulty": "easy"
}
```

### Submit Answer (BKT-powered)
```
POST /api/learning/submit-answer
```
**Description**: Submit an answer to a question and get updated skill mastery levels using the BKT model

**Request Body**:
```json
{
  "user_id": "uuid-string",
  "question_id": "q123",
  "answer": "4",
  "time_taken_seconds": 45
}
```

**Response**:
```json
{
  "user_id": "uuid-string",
  "question_id": "q123",
  "is_correct": true,
  "skill": "basic_syntax",
  "subject": "python",
  "previous_mastery": 0.450,
  "new_mastery": 0.523,
  "mastery_change": 0.073,
  "feedback": "Correct! You're making good progress in basic_syntax. Keep practicing to reinforce your knowledge."
}
```

### Update Course Progress
```
POST /api/learning/progress/update
```
**Request Body**:
```json
{
  "user_id": "uuid-string",
  "module_id": "python_remedial_oop",
  "progress_percentage": 50.0,
  "completed": false,
  "time_spent_minutes": 30
}
```
**Response**:
```json
{
  "user_id": "uuid-string",
  "module_id": "python_remedial_oop",
  "progress_percentage": 50.0,
  "completed": false,
  "time_spent_minutes": 60,
  "updated_at": "2025-10-03T12:00:00Z"
}
```

### Get Module Content
```
GET /api/learning/content/{module_id}
```
**Response**:
```json
{
  "module_id": "python_remedial_oop",
  "title": "Building foundations in OOP",
  "sections": [
    {
      "section_id": "python_remedial_oop_section_1",
      "title": "Introduction to OOP",
      "content_type": "text",
      "content": "Object-oriented programming (OOP) is a programming paradigm..."
    },
    {
      "section_id": "python_remedial_oop_section_2",
      "title": "Classes and Objects",
      "content_type": "text",
      "content": "A class is a blueprint for creating objects..."
    },
    {
      "section_id": "python_remedial_oop_section_3",
      "title": "Practice Quiz",
      "content_type": "quiz",
      "questions": [
        {
          "id": "python_remedial_oop_q1",
          "text": "What is a class in Python?",
          "options": ["A function", "A blueprint for objects", "A data type", "A loop structure"],
          "correct_answer": "A blueprint for objects"
        }
      ]
    }
  ],
  "estimated_completion_time": "45 minutes"
}
```

## 5. Analytics (for PowerBI and AIML Team)

### Dashboard Overview
```
GET /api/analytics/dashboard/overview
```
**Response**:
```json
{
  "user_metrics": {
    "total_users": 100,
    "new_users_today": 5,
    "active_last_week": 45
  },
  "assessment_metrics": {
    "total_assessments": 250,
    "completed_assessments": 200,
    "completion_rate": 80.0,
    "assessments_today": 12,
    "by_subject": {
      "python": 120,
      "math": 80,
      "science": 50
    }
  },
  "learning_metrics": {
    "total_modules_started": 500,
    "modules_completed": 300,
    "completion_rate": 60.0,
    "total_time_spent_minutes": 12000,
    "avg_time_per_module_minutes": 24
  },
  "generated_at": "2025-10-03T12:00:00Z"
}
```

### Subject Analytics
```
GET /api/analytics/dashboard/subject/{subject}
```
**Response**:
```json
{
  "subject": "python",
  "assessment_metrics": {
    "total_assessments": 120,
    "completed_assessments": 100,
    "completion_rate": 83.3,
    "average_score": 75.5
  },
  "question_metrics": {
    "total_questions": 24,
    "by_difficulty": {
      "very_easy": 6,
      "easy": 6,
      "medium": 6,
      "hard": 6
    }
  },
  "skill_metrics": {
    "basic_syntax": {
      "assessment_count": 100,
      "correct_count": 80,
      "incorrect_count": 20,
      "correct_percentage": 80.0,
      "mastery_average": 0.75
    },
    "functions": {
      "assessment_count": 80,
      "correct_count": 60,
      "incorrect_count": 20,
      "correct_percentage": 75.0,
      "mastery_average": 0.7
    }
  },
  "generated_at": "2025-10-03T12:00:00Z"
}
```

### User Analytics
```
GET /api/analytics/user/{user_id}
```
**Response**:
```json
{
  "user_id": "uuid-string",
  "assessment_metrics": {
    "total": 5,
    "completed": 4,
    "by_subject": {
      "python": {
        "total": 3,
        "completed": 3,
        "average_score": 85.0
      },
      "math": {
        "total": 2,
        "completed": 1,
        "average_score": 70.0
      }
    }
  },
  "learning_metrics": {
    "paths_count": 2,
    "by_subject": {
      "python": {
        "modules_total": 6,
        "modules_started": 6,
        "modules_completed": 4,
        "time_spent_minutes": 180,
        "completion_percentage": 66.7
      },
      "math": {
        "modules_total": 4,
        "modules_started": 3,
        "modules_completed": 1,
        "time_spent_minutes": 90,
        "completion_percentage": 25.0
      }
    },
    "total_time_spent_minutes": 270,
    "modules_started": 9,
    "modules_completed": 5
  },
  "skill_masteries": {
    "python": {
      "basic_syntax": 0.9,
      "functions": 0.8,
      "oop": 0.6
    },
    "math": {
      "algebra": 0.7,
      "geometry": 0.5
    }
  },
  "generated_at": "2025-10-03T12:00:00Z"
}
```

## 6. User Progress for PowerBI

```
GET /api/learning/progress/{user_id}
```
**Response**:
```json
{
  "user_id": "uuid-string",
  "generated_at": "2025-10-03T12:00:00Z",
  "subjects": [
    {
      "subject": "python",
      "paths": [...],
      "modules_total": 6,
      "modules_completed": 4,
      "overall_progress": 66.67,
      "time_spent_minutes": 180
    },
    {
      "subject": "math",
      "paths": [...],
      "modules_total": 4,
      "modules_completed": 1,
      "overall_progress": 25.0,
      "time_spent_minutes": 90
    }
  ]
}
```

## Integration Guidelines

### For Frontend Developers
1. Use the `/api/subjects` endpoints to get subjects for the home page
2. Use the `/api/assessment/start` endpoint to begin an assessment
3. Use the `/api/assessment/answer` endpoint to submit answers and receive the next question
4. Use the `/api/assessment/{id}/results` endpoint to get results and the learning path
5. Use the `/api/learning/path/{user_id}/{subject}` endpoint to show the user's learning progress
6. Use the `/api/learning/content/{module_id}` endpoint to fetch content for each module

### For AIML Team
1. Use the `/api/analytics` endpoints to get data for training your models
2. The assessment results contain skill mastery levels calculated by the BKT algorithm
3. The learning path is generated based on the skill masteries
4. You can enhance the learning path generation algorithm in the `assessment.py` file

### For PowerBI Dashboard Team
1. Use the `/api/analytics/dashboard/overview` endpoint for the main dashboard
2. Use the `/api/analytics/dashboard/subject/{subject}` endpoint for subject-specific dashboards
3. Use the `/api/analytics/user/{user_id}` endpoint for user-specific analytics
4. Use the `/api/learning/progress/{user_id}` endpoint for detailed progress tracking