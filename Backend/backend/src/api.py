from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, List
import os
import json
from datetime import datetime
import uuid

from .bkt_model import BKTModel

try:
    from pymongo import MongoClient
    MONGO_AVAILABLE = True
except ImportError:
    MONGO_AVAILABLE = False
    MongoClient = None


class StartSessionRequest(BaseModel):
    user_id: Optional[str] = None
    subject: Optional[str] = "python"


class AnswerRequest(BaseModel):
    session_id: str
    question_id: str
    answer: str


class DataStore:
    """Abstraction layer for MongoDB with in-memory fallback."""
    
    def __init__(self):
        self.mongo_uri = os.environ.get('MONGO_URI')
        self.using_mongo = False
        self.sessions = {}
        self.attempts = []
        self.questions = []
        
        if self.mongo_uri and MONGO_AVAILABLE:
            try:
                self.client = MongoClient(self.mongo_uri, serverSelectionTimeoutMS=5000)  # type: ignore
                self.db = self.client.adaptive_learning
                self.sessions_col = self.db.sessions
                self.attempts_col = self.db.attempts
                self.questions_col = self.db.questions
                self.client.admin.command('ping')
                self.using_mongo = True
                print("✓ Connected to MongoDB")
            except Exception as e:
                print(f"✗ MongoDB connection failed: {e}")
                print("→ Using in-memory fallback")
                self.using_mongo = False
                self._load_questions_from_file()
        else:
            print("→ MONGO_URI not set or pymongo unavailable, using in-memory storage")
            self._load_questions_from_file()
    
    def _load_questions_from_file(self):
        """Load questions from local JSON file if MongoDB is unavailable."""
        try:
            # First try to load questions.json, fall back to sample_questions.json
            try:
                with open('questions.json', 'r') as f:
                    self.questions = json.load(f)
                    print(f"✓ Loaded {len(self.questions)} questions from questions.json")
            except FileNotFoundError:
                # Fall back to sample_questions.json
                with open('sample_questions.json', 'r') as f:
                    self.questions = json.load(f)
                    print(f"✓ Loaded {len(self.questions)} questions from sample_questions.json (fallback)")
        except FileNotFoundError:
            print("✗ Both questions.json and sample_questions.json not found. Using empty question set.")
            self.questions = []
    
    def save_session(self, session: dict) -> str:
        """Save or update a session."""
        if self.using_mongo:
            result = self.sessions_col.update_one(
                {'session_id': session['session_id']},
                {'$set': session},
                upsert=True
            )
            return session['session_id']
        else:
            self.sessions[session['session_id']] = session
            return session['session_id']
    
    def get_session(self, session_id: str) -> Optional[dict]:
        """Retrieve a session by ID."""
        if self.using_mongo:
            return self.sessions_col.find_one({'session_id': session_id}, {'_id': 0})
        else:
            return self.sessions.get(session_id)
    
    def save_attempt(self, attempt: dict):
        """Save a question attempt."""
        if self.using_mongo:
            self.attempts_col.insert_one(attempt)
        else:
            self.attempts.append(attempt)
    
    def get_questions(self, subject: Optional[str] = None) -> List[dict]:
        """Get questions, optionally filtered by subject."""
        if self.using_mongo:
            query = {'subject': subject} if subject else {}
            return list(self.questions_col.find(query, {'_id': 0}))
        else:
            if subject:
                return [q for q in self.questions if q.get('subject') == subject]
            return self.questions


app = FastAPI(
    title="Adaptive Learning API",
    description="BKT-based adaptive learning system with skill mastery tracking",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

store = DataStore()
bkt = BKTModel()


@app.get("/")
def root():
    return {
        "name": "Adaptive Learning API",
        "version": "1.0.0",
        "description": "BKT-based adaptive learning system",
        "storage": "MongoDB" if store.using_mongo else "In-Memory",
        "docs": "/docs"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "storage": "MongoDB" if store.using_mongo else "In-Memory",
        "questions_loaded": len(store.questions) if not store.using_mongo else "database"
    }


@app.post("/api/adaptive/start")
def start_session(request: StartSessionRequest):
    """
    Start a new adaptive learning session.
    
    Returns a session ID and the first question.
    """
    session_id = str(uuid.uuid4())
    user_id = request.user_id or f"user_{uuid.uuid4().hex[:8]}"
    
    questions = store.get_questions(request.subject)
    if not questions:
        raise HTTPException(
            status_code=404,
            detail=f"No questions found for subject: {request.subject}"
        )
    
    skills = list(set(q.get('skill', 'unknown') for q in questions))
    skill_masteries = {skill: bkt.initialize_skill() for skill in skills}
    
    session = {
        'session_id': session_id,
        'user_id': user_id,
        'subject': request.subject,
        'skill_masteries': skill_masteries,
        'answered_questions': [],
        'created_at': datetime.utcnow().isoformat(),
        'updated_at': datetime.utcnow().isoformat()
    }
    
    store.save_session(session)
    
    available_questions = [q for q in questions if q['id'] not in session['answered_questions']]
    next_question, reason = bkt.select_next_question(skill_masteries, available_questions)
    
    if not next_question:
        raise HTTPException(status_code=404, detail="No questions available")
    
    return {
        'session_id': session_id,
        'user_id': user_id,
        'question': {
            'id': next_question['id'],
            'text': next_question['text'],
            'options': next_question.get('options', []),
            'skill': next_question.get('skill')
        },
        'skill_masteries': skill_masteries,
        'selection_reason': reason
    }


@app.post("/api/adaptive/answer")
def submit_answer(request: AnswerRequest):
    """
    Submit an answer and get the next question.
    
    Updates skill mastery based on BKT and returns the next adaptive question.
    """
    session = store.get_session(request.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    questions = store.get_questions(session['subject'])
    question = next((q for q in questions if q['id'] == request.question_id), None)
    
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    is_correct = request.answer.strip().lower() == question['correct_answer'].strip().lower()
    skill = question.get('skill', 'unknown')
    
    current_mastery = session['skill_masteries'].get(skill, bkt.initialize_skill())
    new_mastery = bkt.update_mastery(current_mastery, is_correct)
    session['skill_masteries'][skill] = new_mastery
    
    session['answered_questions'].append(request.question_id)
    session['updated_at'] = datetime.utcnow().isoformat()
    
    attempt = {
        'session_id': request.session_id,
        'question_id': request.question_id,
        'user_answer': request.answer,
        'correct_answer': question['correct_answer'],
        'is_correct': is_correct,
        'skill': skill,
        'mastery_before': current_mastery,
        'mastery_after': new_mastery,
        'timestamp': datetime.utcnow().isoformat()
    }
    store.save_attempt(attempt)
    store.save_session(session)
    
    available_questions = [q for q in questions if q['id'] not in session['answered_questions']]
    
    result = {
        'is_correct': is_correct,
        'correct_answer': question['correct_answer'],
        'skill': skill,
        'mastery_before': round(current_mastery, 3),
        'mastery_after': round(new_mastery, 3),
        'skill_masteries': {k: round(v, 3) for k, v in session['skill_masteries'].items()}
    }
    
    if available_questions:
        next_question, reason = bkt.select_next_question(
            session['skill_masteries'],
            available_questions
        )
        
        if next_question:
            result['next_question'] = {
                'id': next_question['id'],
                'text': next_question['text'],
                'options': next_question.get('options', []),
                'skill': next_question.get('skill')
            }
            result['selection_reason'] = reason
    else:
        result['message'] = 'Session complete! All questions answered.'
    
    return result


@app.get("/api/sessions/{session_id}")
def get_session(session_id: str):
    """Get session details including progress and skill masteries."""
    session = store.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    questions = store.get_questions(session['subject'])
    total_questions = len(questions)
    answered_count = len(session['answered_questions'])
    
    return {
        'session_id': session['session_id'],
        'user_id': session['user_id'],
        'subject': session['subject'],
        'skill_masteries': {k: round(v, 3) for k, v in session['skill_masteries'].items()},
        'progress': {
            'answered': answered_count,
            'total': total_questions,
            'percentage': round((answered_count / total_questions * 100), 1) if total_questions > 0 else 0
        },
        'created_at': session['created_at'],
        'updated_at': session['updated_at']
    }


@app.get("/api/sessions/{session_id}/attempts")
def get_session_attempts(session_id: str):
    """Get all attempts for a session."""
    session = store.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if store.using_mongo:
        attempts = list(store.attempts_col.find({'session_id': session_id}, {'_id': 0}))
    else:
        attempts = [a for a in store.attempts if a['session_id'] == session_id]
    
    return {
        'session_id': session_id,
        'attempts': attempts,
        'total_attempts': len(attempts),
        'correct_count': sum(1 for a in attempts if a['is_correct']),
        'accuracy': round(sum(1 for a in attempts if a['is_correct']) / len(attempts) * 100, 1) if attempts else 0
    }


@app.get("/api/questions")
def list_questions(subject: Optional[str] = None, skill: Optional[str] = None):
    """List available questions, optionally filtered by subject or skill."""
    questions = store.get_questions(subject)
    
    if skill:
        questions = [q for q in questions if q.get('skill') == skill]
    
    return {
        'questions': [
            {
                'id': q['id'],
                'text': q['text'],
                'skill': q.get('skill'),
                'subject': q.get('subject')
            }
            for q in questions
        ],
        'total': len(questions)
    }


@app.get("/api/skills")
def list_skills(subject: Optional[str] = None):
    """List all available skills, optionally filtered by subject."""
    questions = store.get_questions(subject)
    skills = list(set(q.get('skill', 'unknown') for q in questions))
    
    skill_stats = {}
    for skill in skills:
        skill_questions = [q for q in questions if q.get('skill') == skill]
        skill_stats[skill] = {
            'question_count': len(skill_questions),
            'initial_mastery': bkt.initialize_skill()
        }
    
    return {
        'skills': skill_stats,
        'total_skills': len(skills)
    }


