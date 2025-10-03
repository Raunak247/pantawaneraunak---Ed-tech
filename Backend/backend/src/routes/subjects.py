from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any
from ..database import db_manager
from ..config import settings

router = APIRouter(prefix="/api/subjects", tags=["subjects"])

@router.get("/", response_model=Dict[str, Any])
async def get_all_subjects():
    """
    Get all available subjects with their skills and statistics.
    Used for the home page where users select a subject.
    """
    db = db_manager.get_collection("questions")
    
    # Get all questions
    questions = await db.find().to_list()
    
    # Extract unique subjects with their skills
    subjects = {}
    
    for question in questions:
        subject_id = question.get('subject')
        if not subject_id:
            continue
            
        # Create subject entry if it doesn't exist
        if subject_id not in subjects:
            subjects[subject_id] = {
                "id": subject_id,
                "name": subject_id.capitalize(),
                "description": f"Learn and master {subject_id}",
                "question_count": 0,
                "skills": {},
                "difficulty_distribution": {
                    "very_easy": 0,
                    "easy": 0, 
                    "medium": 0,
                    "hard": 0
                }
            }
        
        # Update question count
        subjects[subject_id]["question_count"] += 1
        
        # Add skill if it doesn't exist
        skill = question.get('skill', 'general')
        if skill not in subjects[subject_id]["skills"]:
            subjects[subject_id]["skills"][skill] = {
                "name": skill.replace('_', ' ').capitalize(),
                "question_count": 0
            }
        
        # Update skill question count
        subjects[subject_id]["skills"][skill]["question_count"] += 1
        
        # Update difficulty distribution
        difficulty = question.get('difficulty', 'medium')
        if difficulty in subjects[subject_id]["difficulty_distribution"]:
            subjects[subject_id]["difficulty_distribution"][difficulty] += 1
    
    # Convert subjects dict to list
    subjects_list = list(subjects.values())
    
    # Sort by question count
    subjects_list.sort(key=lambda x: x["question_count"], reverse=True)
    
    return {
        "subjects": subjects_list,
        "total": len(subjects_list)
    }

@router.get("/{subject_id}", response_model=Dict[str, Any])
async def get_subject_details(subject_id: str):
    """
    Get detailed information about a specific subject including all skills and stats.
    """
    db = db_manager.get_collection("questions")
    
    # Find questions for this subject
    questions = await db.find({"subject": subject_id}).to_list()
    
    if not questions:
        raise HTTPException(status_code=404, detail=f"Subject '{subject_id}' not found")
    
    # Process skills and other metadata
    skills = {}
    difficulty_distribution = {
        "very_easy": 0,
        "easy": 0,
        "medium": 0,
        "hard": 0
    }
    
    for question in questions:
        # Process skills
        skill = question.get('skill', 'general')
        if skill not in skills:
            skills[skill] = {
                "id": skill,
                "name": skill.replace('_', ' ').capitalize(),
                "question_count": 0,
                "description": f"Master {skill.replace('_', ' ')} in {subject_id}"
            }
        
        skills[skill]["question_count"] += 1
        
        # Update difficulty distribution
        difficulty = question.get('difficulty', 'medium')
        if difficulty in difficulty_distribution:
            difficulty_distribution[difficulty] += 1
    
    # Get skills as list and sort by question count
    skills_list = list(skills.values())
    skills_list.sort(key=lambda x: x["question_count"], reverse=True)
    
    return {
        "id": subject_id,
        "name": subject_id.capitalize(),
        "description": f"Learn and master {subject_id}",
        "question_count": len(questions),
        "skills": skills_list,
        "difficulty_distribution": difficulty_distribution
    }