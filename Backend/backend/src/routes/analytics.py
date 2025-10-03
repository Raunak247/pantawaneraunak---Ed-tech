from fastapi import APIRouter, HTTPException, Body, Depends
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from ..database import db_manager
from ..config import settings
from datetime import datetime, timedelta

router = APIRouter(prefix="/api/analytics", tags=["analytics"])

@router.get("/dashboard/overview", response_model=Dict[str, Any])
async def get_dashboard_overview():
    """
    Get overall platform analytics for PowerBI dashboard.
    This endpoint provides data for the main dashboard overview.
    """
    # Get collections
    assessments_col = db_manager.get_collection("assessments")
    progress_col = db_manager.get_collection("user_progress")
    users_col = db_manager.get_collection("users")
    
    # Calculate time periods
    now = datetime.utcnow()
    today = now.replace(hour=0, minute=0, second=0, microsecond=0)
    yesterday = today - timedelta(days=1)
    this_week = today - timedelta(days=today.weekday())
    last_week = this_week - timedelta(days=7)
    this_month = today.replace(day=1)
    
    # Get basic counts
    total_users = await users_col.count_documents({})
    total_assessments = await assessments_col.count_documents({})
    completed_assessments = await assessments_col.count_documents({"status": "completed"})
    
    # Get new users today
    new_users_today = await users_col.count_documents({
        "created_at": {"$gte": today.isoformat()}
    })
    
    # Get assessments today
    assessments_today = await assessments_col.count_documents({
        "created_at": {"$gte": today.isoformat()}
    })
    
    # Get assessments by subject
    all_assessments = await assessments_col.find().to_list()
    subjects = {}
    for assessment in all_assessments:
        subject = assessment.get("subject", "unknown")
        if subject not in subjects:
            subjects[subject] = 0
        subjects[subject] += 1
    
    # Get all progress entries
    all_progress = await progress_col.find().to_list()
    
    # Calculate completion rate and time spent
    total_modules = len(all_progress)
    completed_modules = sum(1 for p in all_progress if p.get("completed", False))
    completion_rate = (completed_modules / total_modules) * 100 if total_modules > 0 else 0
    
    total_time_spent = sum(p.get("time_spent_minutes", 0) for p in all_progress)
    avg_time_per_module = total_time_spent / total_modules if total_modules > 0 else 0
    
    return {
        "user_metrics": {
            "total_users": total_users,
            "new_users_today": new_users_today,
            "active_last_week": await users_col.count_documents({
                "last_active": {"$gte": last_week.isoformat()}
            })
        },
        "assessment_metrics": {
            "total_assessments": total_assessments,
            "completed_assessments": completed_assessments,
            "completion_rate": (completed_assessments / total_assessments) * 100 if total_assessments > 0 else 0,
            "assessments_today": assessments_today,
            "by_subject": subjects
        },
        "learning_metrics": {
            "total_modules_started": total_modules,
            "modules_completed": completed_modules,
            "completion_rate": completion_rate,
            "total_time_spent_minutes": total_time_spent,
            "avg_time_per_module_minutes": avg_time_per_module
        },
        "generated_at": datetime.utcnow().isoformat()
    }

@router.get("/dashboard/subject/{subject}", response_model=Dict[str, Any])
async def get_subject_analytics(subject: str):
    """
    Get analytics for a specific subject.
    This endpoint provides detailed data for subject-specific dashboards.
    """
    # Get collections
    assessments_col = db_manager.get_collection("assessments")
    questions_col = db_manager.get_collection("questions")
    
    # Get assessments for this subject
    assessments = await assessments_col.find({"subject": subject}).to_list()
    
    if not assessments:
        raise HTTPException(status_code=404, detail=f"No data found for subject: {subject}")
    
    # Get questions for this subject
    questions = await questions_col.find({"subject": subject}).to_list()
    
    # Extract unique skills
    skills = set()
    for question in questions:
        skill = question.get("skill")
        if skill:
            skills.add(skill)
    
    # Calculate assessment metrics by skill
    skill_metrics = {skill: {
        "assessment_count": 0,
        "correct_count": 0,
        "incorrect_count": 0,
        "mastery_average": 0
    } for skill in skills}
    
    for assessment in assessments:
        # Process answers
        for q_id, answer in assessment.get("answers", {}).items():
            # Find the question to get its skill
            question = next((q for q in questions if q.get("id") == q_id), None)
            if question:
                skill = question.get("skill", "unknown")
                if skill in skill_metrics:
                    skill_metrics[skill]["assessment_count"] += 1
                    if answer.get("is_correct", False):
                        skill_metrics[skill]["correct_count"] += 1
                    else:
                        skill_metrics[skill]["incorrect_count"] += 1
        
        # Process skill masteries
        for skill, mastery in assessment.get("skill_masteries", {}).items():
            if skill in skill_metrics:
                current_avg = skill_metrics[skill]["mastery_average"]
                current_count = skill_metrics[skill]["assessment_count"]
                
                # Update running average
                if current_count > 0:
                    skill_metrics[skill]["mastery_average"] = (
                        (current_avg * (current_count - 1) + mastery) / current_count
                    )
    
    # Calculate difficulty distribution
    difficulty_counts = {
        "very_easy": 0,
        "easy": 0,
        "medium": 0,
        "hard": 0
    }
    
    for question in questions:
        difficulty = question.get("difficulty", "medium")
        if difficulty in difficulty_counts:
            difficulty_counts[difficulty] += 1
    
    # Calculate assessment completion metrics
    completed_assessments = [a for a in assessments if a.get("status") == "completed"]
    completion_rate = (len(completed_assessments) / len(assessments)) * 100 if assessments else 0
    
    # Calculate average scores
    scores = []
    for assessment in completed_assessments:
        correct = sum(1 for a in assessment.get("answers", {}).values() if a.get("is_correct", False))
        total = len(assessment.get("questions", []))
        if total > 0:
            scores.append((correct / total) * 100)
    
    avg_score = sum(scores) / len(scores) if scores else 0
    
    return {
        "subject": subject,
        "assessment_metrics": {
            "total_assessments": len(assessments),
            "completed_assessments": len(completed_assessments),
            "completion_rate": completion_rate,
            "average_score": avg_score
        },
        "question_metrics": {
            "total_questions": len(questions),
            "by_difficulty": difficulty_counts
        },
        "skill_metrics": {
            skill: {
                **metrics,
                "correct_percentage": (metrics["correct_count"] / metrics["assessment_count"]) * 100 
                                     if metrics["assessment_count"] > 0 else 0,
                "mastery_average": round(metrics["mastery_average"], 3)
            }
            for skill, metrics in skill_metrics.items()
        },
        "generated_at": datetime.utcnow().isoformat()
    }

@router.get("/user/{user_id}", response_model=Dict[str, Any])
async def get_user_analytics(user_id: str):
    """
    Get detailed analytics for a specific user.
    This endpoint provides data for user-specific dashboards and reports.
    """
    # Get collections
    assessments_col = db_manager.get_collection("assessments")
    progress_col = db_manager.get_collection("user_progress")
    learning_paths_col = db_manager.get_collection("learning_paths")
    users_col = db_manager.get_collection("users")
    
    # Get user data
    user = await users_col.find_one({"user_id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail=f"User not found: {user_id}")
    
    # Get user assessments
    assessments = await assessments_col.find({"user_id": user_id}).to_list()
    
    # Get learning paths
    learning_paths = await learning_paths_col.find({"user_id": user_id}).to_list()
    
    # Get progress data
    progress_entries = await progress_col.find({"user_id": user_id}).to_list()
    
    # Calculate assessment metrics
    assessment_metrics = {
        "total": len(assessments),
        "completed": sum(1 for a in assessments if a.get("status") == "completed"),
        "by_subject": {}
    }
    
    for assessment in assessments:
        subject = assessment.get("subject", "unknown")
        if subject not in assessment_metrics["by_subject"]:
            assessment_metrics["by_subject"][subject] = {
                "total": 0,
                "completed": 0,
                "average_score": 0,
                "scores": []
            }
        
        assessment_metrics["by_subject"][subject]["total"] += 1
        
        if assessment.get("status") == "completed":
            assessment_metrics["by_subject"][subject]["completed"] += 1
            
            # Calculate score
            correct = sum(1 for a in assessment.get("answers", {}).values() if a.get("is_correct", False))
            total = len(assessment.get("questions", []))
            if total > 0:
                score = (correct / total) * 100
                assessment_metrics["by_subject"][subject]["scores"].append(score)
    
    # Calculate average scores
    for subject, data in assessment_metrics["by_subject"].items():
        if data["scores"]:
            data["average_score"] = sum(data["scores"]) / len(data["scores"])
        del data["scores"]  # Remove raw scores from response
    
    # Calculate learning progress
    learning_metrics = {
        "paths_count": len(learning_paths),
        "by_subject": {},
        "total_time_spent_minutes": sum(p.get("time_spent_minutes", 0) for p in progress_entries),
        "modules_started": len(progress_entries),
        "modules_completed": sum(1 for p in progress_entries if p.get("completed", False))
    }
    
    # Calculate progress by subject
    subject_progress = {}
    
    for path in learning_paths:
        subject = path.get("subject", "unknown")
        if subject not in subject_progress:
            subject_progress[subject] = {
                "modules_total": 0,
                "modules_started": 0,
                "modules_completed": 0,
                "time_spent_minutes": 0
            }
        
        # Count modules in path
        modules = path.get("learning_path", {}).get("modules", [])
        subject_progress[subject]["modules_total"] += len(modules)
        
        # Get module IDs for this path
        module_ids = [m.get("id") for m in modules if "id" in m]
        
        # Find progress for these modules
        for entry in progress_entries:
            if entry.get("module_id") in module_ids:
                subject_progress[subject]["modules_started"] += 1
                subject_progress[subject]["time_spent_minutes"] += entry.get("time_spent_minutes", 0)
                
                if entry.get("completed", False):
                    subject_progress[subject]["modules_completed"] += 1
    
    # Calculate completion percentages
    for subject, data in subject_progress.items():
        if data["modules_total"] > 0:
            data["completion_percentage"] = (data["modules_completed"] / data["modules_total"]) * 100
        else:
            data["completion_percentage"] = 0
    
    learning_metrics["by_subject"] = subject_progress
    
    # Add skill masteries from latest assessments
    skill_masteries = {}
    
    for assessment in sorted(assessments, key=lambda a: a.get("updated_at", ""), reverse=True):
        subject = assessment.get("subject", "unknown")
        if subject not in skill_masteries:
            skill_masteries[subject] = {}
        
        # Add any new skills from this assessment
        for skill, mastery in assessment.get("skill_masteries", {}).items():
            if skill not in skill_masteries[subject]:
                skill_masteries[subject][skill] = round(mastery, 3)
    
    return {
        "user_id": user_id,
        "assessment_metrics": assessment_metrics,
        "learning_metrics": learning_metrics,
        "skill_masteries": skill_masteries,
        "generated_at": datetime.utcnow().isoformat()
    }