from fastapi import APIRouter, HTTPException, Body, Depends
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from ..database import db_manager
from ..config import settings
from datetime import datetime
import uuid

router = APIRouter(prefix="/api/learning", tags=["learning"])

class CourseProgressUpdate(BaseModel):
    user_id: str
    module_id: str
    progress_percentage: float
    completed: bool = False
    time_spent_minutes: Optional[int] = None
    
@router.get("/path/{user_id}/{subject}", response_model=Dict[str, Any])
async def get_user_learning_path(user_id: str, subject: str):
    """
    Get the user's current learning path for a specific subject.
    This is created after assessment and can be updated as the user progresses.
    """
    learning_paths_col = db_manager.get_collection("learning_paths")
    
    # Get the most recent learning path for this user and subject
    paths = await learning_paths_col.find({
        "user_id": user_id,
        "subject": subject
    }).sort("created_at", -1).to_list(1)  # Most recent first, limit 1
    
    if not paths:
        raise HTTPException(status_code=404, detail="No learning path found. Complete an assessment first.")
    
    path = paths[0]
    
    # Get progress data
    progress_col = db_manager.get_collection("user_progress")
    progress_entries = await progress_col.find({
        "user_id": user_id,
        "learning_path_id": path.get("_id")
    }).to_list()
    
    # Calculate overall progress
    modules = path.get("learning_path", {}).get("modules", [])
    if not modules:
        return {
            "learning_path": path.get("learning_path", {}),
            "overall_progress": 0,
            "completed": False
        }
    
    # Map progress to modules
    module_progress = {}
    for entry in progress_entries:
        module_id = entry.get("module_id")
        if module_id:
            module_progress[module_id] = entry
    
    # Calculate progress for each module and overall progress
    completed_modules = 0
    total_progress = 0
    
    for module in modules:
        module_id = module.get("id")
        if module_id in module_progress:
            progress = module_progress[module_id].get("progress_percentage", 0)
            module["current_progress"] = progress
            module["completed"] = module_progress[module_id].get("completed", False)
            
            if module["completed"]:
                completed_modules += 1
        else:
            module["current_progress"] = 0
            module["completed"] = False
        
        total_progress += module["current_progress"]
    
    overall_progress = total_progress / len(modules) if modules else 0
    
    return {
        "learning_path": path.get("learning_path", {}),
        "overall_progress": round(overall_progress, 2),
        "completed": completed_modules == len(modules)
    }

@router.post("/progress/update", response_model=Dict[str, Any])
async def update_course_progress(update: CourseProgressUpdate):
    """
    Update user's progress for a specific learning module.
    """
    progress_col = db_manager.get_collection("user_progress")
    
    # Find existing progress entry
    existing = await progress_col.find_one({
        "user_id": update.user_id,
        "module_id": update.module_id
    })
    
    timestamp = datetime.utcnow().isoformat()
    
    if existing:
        # Update existing entry
        await progress_col.update_one(
            {"_id": existing["_id"]},
            {"$set": {
                "progress_percentage": update.progress_percentage,
                "completed": update.completed,
                "time_spent_minutes": existing.get("time_spent_minutes", 0) + (update.time_spent_minutes or 0),
                "updated_at": timestamp
            }}
        )
        progress_id = existing["_id"]
    else:
        # Create new entry
        learning_paths_col = db_manager.get_collection("learning_paths")
        
        # Find which learning path contains this module
        # We search all learning paths for this user
        paths = await learning_paths_col.find({
            "user_id": update.user_id
        }).to_list()
        
        learning_path_id = None
        for path in paths:
            modules = path.get("learning_path", {}).get("modules", [])
            if any(mod.get("id") == update.module_id for mod in modules):
                learning_path_id = path.get("_id")
                break
        
        progress_entry = {
            "user_id": update.user_id,
            "module_id": update.module_id,
            "learning_path_id": learning_path_id,
            "progress_percentage": update.progress_percentage,
            "completed": update.completed,
            "time_spent_minutes": update.time_spent_minutes or 0,
            "created_at": timestamp,
            "updated_at": timestamp
        }
        
        result = await progress_col.insert_one(progress_entry)
        progress_id = result.inserted_id
    
    # Return updated progress
    updated = await progress_col.find_one({"_id": progress_id})
    
    return {
        "user_id": update.user_id,
        "module_id": update.module_id,
        "progress_percentage": updated.get("progress_percentage", 0),
        "completed": updated.get("completed", False),
        "time_spent_minutes": updated.get("time_spent_minutes", 0),
        "updated_at": updated.get("updated_at")
    }

@router.get("/content/{module_id}", response_model=Dict[str, Any])
async def get_module_content(module_id: str):
    """
    Get the detailed content for a specific learning module.
    """
    module_content_col = db_manager.get_collection("module_content")
    
    content = await module_content_col.find_one({"module_id": module_id})
    
    if not content:
        # If no specific content is found, generate placeholder content
        # In a real system, this would be replaced with actual content from a CMS
        content = {
            "module_id": module_id,
            "title": f"Module content for {module_id}",
            "sections": [
                {
                    "section_id": f"{module_id}_section_1",
                    "title": "Introduction",
                    "content_type": "text",
                    "content": f"This is introductory content for module {module_id}."
                },
                {
                    "section_id": f"{module_id}_section_2",
                    "title": "Concepts",
                    "content_type": "text",
                    "content": "Core concepts explanation would go here."
                },
                {
                    "section_id": f"{module_id}_section_3",
                    "title": "Practice",
                    "content_type": "quiz",
                    "questions": [
                        {
                            "id": f"{module_id}_q1",
                            "text": "This is a practice question?",
                            "options": ["Option A", "Option B", "Option C", "Option D"],
                            "correct_answer": "Option B"
                        }
                    ]
                }
            ],
            "estimated_completion_time": "45 minutes"
        }
    
    return content

@router.get("/next-question/{user_id}/{subject}", response_model=Dict[str, Any])
async def get_next_question(user_id: str, subject: str):
    """
    Get the next recommended question for a user based on their current skill mastery.
    Uses the BKT model to adaptively select the most appropriate question.
    """
    from ..bkt_model import BKTModel
    
    # Initialize the BKT model
    bkt = BKTModel()
    
    # Get the user's current skill masteries
    user_col = db_manager.get_collection("users")
    user_data = await user_col.find_one({"_id": user_id})
    
    if not user_data:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get user's skill masteries for the subject
    skill_masteries = user_data.get("skill_masteries", {}).get(subject, {})
    
    if not skill_masteries:
        # If no skill masteries exist yet, initialize with default values
        skill_masteries = {}
        
        # Get all skills for the subject
        questions_col = db_manager.get_collection("questions")
        questions = await questions_col.find({"subject": subject}).to_list()
        
        # Extract unique skills
        all_skills = set()
        for question in questions:
            if "skill" in question:
                all_skills.add(question["skill"])
        
        # Initialize masteries
        for skill in all_skills:
            skill_masteries[skill] = bkt.initialize_skill(skill)
    
    # Get all available questions for the subject
    questions_col = db_manager.get_collection("questions")
    available_questions = await questions_col.find({"subject": subject}).to_list()
    
    # Get questions the user has already answered
    answers_col = db_manager.get_collection("assessment_answers")
    answered_questions = await answers_col.find({
        "user_id": user_id,
        "subject": subject
    }).to_list()
    
    # Extract IDs of already answered questions
    exclude_ids = [answer.get("question_id") for answer in answered_questions if "question_id" in answer]
    
    # Select the next question using BKT model
    next_question, selection_reason = bkt.select_next_question(
        skill_masteries=skill_masteries,
        available_questions=available_questions,
        exclude_ids=exclude_ids
    )
    
    if not next_question:
        raise HTTPException(status_code=404, detail="No suitable questions found")
    
    # Remove correct answer before returning to client
    question_for_client = {**next_question}
    question_for_client.pop("correct_answer", None)
    
    return {
        "question": question_for_client,
        "selection_reason": selection_reason,
        "question_id": next_question.get("id"),
        "skill": next_question.get("skill"),
        "difficulty": next_question.get("difficulty", "medium")
    }

@router.get("/progress/{user_id}", response_model=Dict[str, Any])
async def get_user_progress_summary(user_id: str):
    """
    Get a summary of the user's progress across all subjects.
    For PowerBI dashboards and analytics.
    """
    progress_col = db_manager.get_collection("user_progress")
    learning_paths_col = db_manager.get_collection("learning_paths")
    
    # Get all user's learning paths
    paths = await learning_paths_col.find({"user_id": user_id}).to_list()
    
    # Get all progress entries
    progress_entries = await progress_col.find({"user_id": user_id}).to_list()
    
    # Organize by subject
    subjects = {}
    
    for path in paths:
        subject = path.get("subject", "unknown")
        if subject not in subjects:
            subjects[subject] = {
                "subject": subject,
                "paths": [],
                "modules_total": 0,
                "modules_completed": 0,
                "overall_progress": 0,
                "time_spent_minutes": 0
            }
        
        subjects[subject]["paths"].append(path)
        
        # Count modules
        modules = path.get("learning_path", {}).get("modules", [])
        subjects[subject]["modules_total"] += len(modules)
    
    # Calculate progress
    for entry in progress_entries:
        module_id = entry.get("module_id", "")
        learning_path_id = entry.get("learning_path_id")
        
        # Find which subject this belongs to
        for subject_data in subjects.values():
            for path in subject_data["paths"]:
                if path.get("_id") == learning_path_id:
                    if entry.get("completed", False):
                        subject_data["modules_completed"] += 1
                    subject_data["time_spent_minutes"] += entry.get("time_spent_minutes", 0)
                    break
    
    # Calculate overall progress percentages
    for subject_data in subjects.values():
        if subject_data["modules_total"] > 0:
            subject_data["overall_progress"] = round(
                (subject_data["modules_completed"] / subject_data["modules_total"]) * 100, 2
            )
    
    # Convert to list and add timestamps
    result = list(subjects.values())
    timestamp = datetime.utcnow().isoformat()
    
    return {
        "user_id": user_id,
        "generated_at": timestamp,
        "subjects": result
    }

class AnswerSubmission(BaseModel):
    user_id: str
    question_id: str
    answer: str
    time_taken_seconds: Optional[int] = None

@router.post("/submit-answer", response_model=Dict[str, Any])
async def submit_answer(submission: AnswerSubmission):
    """
    Submit an answer to a question and update the user's skill mastery using BKT.
    """
    from ..bkt_model import BKTModel
    
    # Initialize BKT model
    bkt = BKTModel()
    
    # Get question details
    questions_col = db_manager.get_collection("questions")
    question = await questions_col.find_one({"id": submission.question_id})
    
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    # Check if answer is correct
    correct_answer = question.get("correct_answer")
    is_correct = submission.answer == correct_answer
    skill = question.get("skill", "unknown")
    subject = question.get("subject", "unknown")
    difficulty = question.get("difficulty", "medium")
    
    # Get user's current skill mastery
    user_col = db_manager.get_collection("users")
    user_data = await user_col.find_one({"_id": submission.user_id})
    
    if not user_data:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Initialize skill masteries structure if not exists
    if "skill_masteries" not in user_data:
        user_data["skill_masteries"] = {}
    
    if subject not in user_data["skill_masteries"]:
        user_data["skill_masteries"][subject] = {}
    
    # Get current mastery or initialize if new
    current_mastery = user_data["skill_masteries"][subject].get(skill, bkt.initialize_skill(skill))
    
    # Update mastery using BKT model
    new_mastery = bkt.update_mastery(
        current_mastery=current_mastery,
        is_correct=is_correct,
        question_difficulty=difficulty
    )
    
    # Save the answer in assessment_answers collection
    answers_col = db_manager.get_collection("assessment_answers")
    timestamp = datetime.utcnow().isoformat()
    
    answer_entry = {
        "user_id": submission.user_id,
        "question_id": submission.question_id,
        "answer": submission.answer,
        "is_correct": is_correct,
        "skill": skill,
        "subject": subject,
        "difficulty": difficulty,
        "time_taken_seconds": submission.time_taken_seconds,
        "previous_mastery": current_mastery,
        "new_mastery": new_mastery,
        "created_at": timestamp
    }
    
    await answers_col.insert_one(answer_entry)
    
    # Update user's skill mastery
    user_data["skill_masteries"][subject][skill] = new_mastery
    await user_col.update_one(
        {"_id": submission.user_id},
        {"$set": {"skill_masteries": user_data["skill_masteries"]}}
    )
    
    # Provide feedback and next steps
    feedback = "Correct! " if is_correct else f"Incorrect. The correct answer was: {correct_answer}. "
    
    if new_mastery > 0.9:
        next_step = f"You've achieved high mastery in {skill}. Consider exploring advanced topics."
    elif new_mastery > 0.7:
        next_step = f"You're making good progress in {skill}. Keep practicing to reinforce your knowledge."
    else:
        next_step = f"You should focus more on {skill}. Consider reviewing the fundamentals."
    
    return {
        "user_id": submission.user_id,
        "question_id": submission.question_id,
        "is_correct": is_correct,
        "skill": skill,
        "subject": subject,
        "previous_mastery": round(current_mastery, 3),
        "new_mastery": round(new_mastery, 3),
        "mastery_change": round(new_mastery - current_mastery, 3),
        "feedback": feedback + next_step
    }