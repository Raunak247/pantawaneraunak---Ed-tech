from fastapi import APIRouter, HTTPException, Body, Depends
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from ..database import db_manager
from ..bkt_model import BKTModel
from ..config import settings
from datetime import datetime
import uuid

router = APIRouter(prefix="/api/assessment", tags=["assessment"])

# Initialize BKT model
bkt = BKTModel()

class AssessmentStartRequest(BaseModel):
    user_id: str
    subject: str
    question_count: Optional[int] = 10  # Default number of assessment questions

class AssessmentAnswerRequest(BaseModel):
    assessment_id: str
    question_id: str
    answer: str

@router.post("/start", response_model=Dict[str, Any])
async def start_assessment(request: AssessmentStartRequest):
    """
    Start an assessment test for a user in a specific subject.
    Returns the first assessment question and a session ID.
    """
    # Create assessment session
    assessment_id = str(uuid.uuid4())
    
    # Get questions for the subject
    questions_col = db_manager.get_collection("questions")
    questions = await questions_col.find({"subject": request.subject}).to_list()
    
    if not questions:
        raise HTTPException(status_code=404, detail=f"No questions found for subject: {request.subject}")
    
    # Extract unique skills and create initial mastery levels
    skills = list(set(q.get('skill', 'unknown') for q in questions))
    skill_masteries = {skill: bkt.initialize_skill(skill) for skill in skills}
    
    # Get a balanced set of questions for assessment
    # Try to include different skills and difficulty levels
    selected_questions = select_assessment_questions(questions, request.question_count)
    
    if not selected_questions:
        raise HTTPException(status_code=500, detail="Failed to select assessment questions")
    
    # Store assessment state
    assessment_session = {
        'assessment_id': assessment_id,
        'user_id': request.user_id,
        'subject': request.subject,
        'questions': [q["id"] for q in selected_questions],
        'current_index': 0,
        'answers': {},
        'skill_masteries': skill_masteries,
        'status': 'in_progress',
        'created_at': datetime.utcnow().isoformat(),
        'updated_at': datetime.utcnow().isoformat()
    }
    
    # Save to database
    assessments_col = db_manager.get_collection("assessments")
    await assessments_col.insert_one(assessment_session)
    
    # Return first question
    first_question = selected_questions[0]
    return {
        'assessment_id': assessment_id,
        'subject': request.subject,
        'total_questions': len(selected_questions),
        'current_question_index': 0,
        'question': {
            'id': first_question['id'],
            'text': first_question['text'],
            'options': first_question.get('options', []),
            'skill': first_question.get('skill')
        }
    }

@router.post("/answer", response_model=Dict[str, Any])
async def submit_assessment_answer(request: AssessmentAnswerRequest):
    """
    Submit an answer for an assessment question and get the next question.
    """
    assessments_col = db_manager.get_collection("assessments")
    assessment = await assessments_col.find_one({"assessment_id": request.assessment_id})
    
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")
    
    if assessment['status'] != 'in_progress':
        raise HTTPException(status_code=400, detail="Assessment is already complete")
    
    # Check if question is valid
    questions_col = db_manager.get_collection("questions")
    question = await questions_col.find_one({"id": request.question_id})
    
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    # Verify this is the correct question for this step
    current_index = assessment['current_index']
    if current_index >= len(assessment['questions']) or assessment['questions'][current_index] != request.question_id:
        raise HTTPException(status_code=400, detail="Invalid question for this assessment step")
    
    # Process answer
    is_correct = request.answer.strip().lower() == question['correct_answer'].strip().lower()
    skill = question.get('skill', 'unknown')
    difficulty = question.get('difficulty', 'medium')
    
    # Update skill mastery using BKT
    current_mastery = assessment['skill_masteries'].get(skill, bkt.initialize_skill(skill))
    new_mastery = bkt.update_mastery(current_mastery, is_correct, difficulty)
    assessment['skill_masteries'][skill] = new_mastery
    
    # Store answer
    assessment['answers'][request.question_id] = {
        'user_answer': request.answer,
        'is_correct': is_correct,
        'timestamp': datetime.utcnow().isoformat()
    }
    
    # Update current index
    assessment['current_index'] += 1
    is_complete = assessment['current_index'] >= len(assessment['questions'])
    
    if is_complete:
        assessment['status'] = 'completed'
        assessment['completed_at'] = datetime.utcnow().isoformat()
    
    assessment['updated_at'] = datetime.utcnow().isoformat()
    
    # Save updated assessment
    await assessments_col.update_one(
        {"assessment_id": request.assessment_id},
        {"$set": assessment}
    )
    
    result = {
        'is_correct': is_correct,
        'correct_answer': question['correct_answer'],
        'skill': skill,
        'assessment_id': request.assessment_id
    }
    
    # If assessment is not complete, return next question
    if not is_complete:
        next_question_id = assessment['questions'][assessment['current_index']]
        next_question = await questions_col.find_one({"id": next_question_id})
        
        result.update({
            'is_complete': False,
            'current_question_index': assessment['current_index'],
            'total_questions': len(assessment['questions']),
            'next_question': {
                'id': next_question['id'],
                'text': next_question['text'],
                'options': next_question.get('options', []),
                'skill': next_question.get('skill')
            }
        })
    else:
        # Return completion info if assessment is done
        result.update({
            'is_complete': True,
            'message': 'Assessment complete!'
        })
    
    return result

@router.get("/{assessment_id}/results", response_model=Dict[str, Any])
async def get_assessment_results(assessment_id: str):
    """
    Get the results of a completed assessment, including skill masteries
    and recommended learning path.
    """
    assessments_col = db_manager.get_collection("assessments")
    assessment = await assessments_col.find_one({"assessment_id": assessment_id})
    
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")
    
    if assessment['status'] != 'completed':
        raise HTTPException(status_code=400, detail="Assessment is not complete")
    
    # Calculate overall score
    total_questions = len(assessment['questions'])
    correct_answers = sum(1 for answer in assessment['answers'].values() if answer.get('is_correct', False))
    score_percentage = (correct_answers / total_questions) * 100 if total_questions > 0 else 0
    
    # Get question details
    questions_col = db_manager.get_collection("questions")
    question_details = {}
    
    for question_id in assessment['questions']:
        question = await questions_col.find_one({"id": question_id})
        if question:
            question_details[question_id] = {
                'text': question['text'],
                'skill': question.get('skill', 'unknown'),
                'difficulty': question.get('difficulty', 'medium')
            }
    
    # Analyze results and generate learning path using BKT model
    analysis = bkt.analyze_assessment_results(
        assessment['skill_masteries'],
        assessment['answers'],
        question_details
    )
    
    # Get recommendations from BKT model
    recommendations = bkt.generate_learning_recommendations(
        assessment['skill_masteries'],
        assessment['subject']
    )
    
    # Generate learning path using model outputs
    learning_path = generate_learning_path(
        assessment['skill_masteries'], 
        assessment['answers'],
        question_details,
        assessment['subject']
    )
    
    # Save learning path to database
    user_id = assessment['user_id']
    learning_paths_col = db_manager.get_collection("learning_paths")
    
    learning_path_record = {
        'user_id': user_id,
        'assessment_id': assessment_id,
        'subject': assessment['subject'],
        'learning_path': learning_path,
        'created_at': datetime.utcnow().isoformat()
    }
    
    await learning_paths_col.insert_one(learning_path_record)
    
    # Return assessment results with learning path
    return {
        'assessment_id': assessment_id,
        'user_id': user_id,
        'subject': assessment['subject'],
        'score': {
            'correct': correct_answers,
            'total': total_questions,
            'percentage': round(score_percentage, 1)
        },
        'skill_masteries': {
            skill: round(mastery, 3) for skill, mastery in assessment['skill_masteries'].items()
        },
        'completed_at': assessment.get('completed_at'),
        'learning_path': learning_path
    }

def select_assessment_questions(questions, count=10):
    """
    Select a balanced set of questions for assessment.
    - Attempts to include questions from each skill
    - Balances different difficulty levels
    """
    if not questions or len(questions) == 0:
        return []
    
    # Make sure we don't ask for more questions than available
    count = min(count, len(questions))
    
    # Group questions by skill
    skills = {}
    for q in questions:
        skill = q.get('skill', 'unknown')
        if skill not in skills:
            skills[skill] = []
        skills[skill].append(q)
    
    # First pass: Select questions from each skill
    selected = []
    skills_count = len(skills)
    questions_per_skill = max(1, count // skills_count)
    
    for skill, skill_questions in skills.items():
        # Sort by difficulty to get a balanced selection
        skill_questions.sort(key=lambda q: {
            'very_easy': 0, 
            'easy': 1, 
            'medium': 2, 
            'hard': 3
        }.get(q.get('difficulty', 'medium'), 2))
        
        # Take questions_per_skill questions, evenly distributed by difficulty
        step = max(1, len(skill_questions) // questions_per_skill)
        selected.extend(skill_questions[::step][:questions_per_skill])
    
    # If we still need more questions, add more from any skill
    if len(selected) < count:
        # Flatten the remaining questions
        remaining = [q for qs in skills.values() for q in qs if q not in selected]
        # Sort by difficulty
        remaining.sort(key=lambda q: {
            'very_easy': 0, 
            'easy': 1, 
            'medium': 2, 
            'hard': 3
        }.get(q.get('difficulty', 'medium'), 2))
        
        # Add remaining questions up to count
        selected.extend(remaining[:count-len(selected)])
    
    # Limit to count and shuffle
    import random
    selected = selected[:count]
    random.shuffle(selected)
    
    return selected

def generate_learning_path(skill_masteries, answers, question_details, subject):
    """
    Generate a personalized learning path based on assessment results.
    Uses the enhanced BKT model to analyze results and generate recommendations.
    
    Parameters:
    - skill_masteries: Dictionary of skill masteries after assessment
    - answers: Dictionary mapping question IDs to answer details
    - question_details: Dictionary mapping question IDs to question metadata
    - subject: The subject of the assessment
    
    Returns:
    - Dictionary containing personalized learning path information
    """
    from ..bkt_model import BKTModel
    
    # Initialize the BKT model
    bkt = BKTModel()
    
    # Analyze assessment results in detail
    analysis = bkt.analyze_assessment_results(
        skill_masteries=skill_masteries,
        answers=answers,
        question_details=question_details
    )
    
    # Generate module recommendations using BKT model
    modules = bkt.generate_learning_recommendations(
        skill_masteries=skill_masteries,
        subject=subject
    )
    
    # Add duration estimates to modules based on difficulty
    for module in modules:
        if module['type'] == 'remedial':
            module['recommended_duration'] = '2 hours'
        elif module['type'] == 'practice':
            module['recommended_duration'] = '3 hours'
        else:  # advanced
            module['recommended_duration'] = '4 hours'
    
    # Calculate estimated completion time
    total_hours = sum(int(module['recommended_duration'].split()[0]) for module in modules)
    
    # Create a complete learning path
    return {
        'subject': subject,
        'strengths': analysis['skill_analysis']['strengths'],
        'areas_for_improvement': analysis['skill_analysis']['weaknesses'],
        'estimated_completion_time': f"{total_hours} hours",
        'modules': modules,
        'recommendation_reason': (
            "This personalized learning path is designed based on your assessment results. "
            f"You showed strong understanding in {', '.join(analysis['skill_analysis']['strengths']) or 'some areas'} "
            f"and need more practice in {', '.join(analysis['skill_analysis']['weaknesses']) or 'a few topics'}. "
            f"Overall mastery: {analysis['overall_mastery']:.1%}."
        ),
        'performance_by_difficulty': analysis['difficulty_analysis'],
        'overall_score': analysis['score']
    }