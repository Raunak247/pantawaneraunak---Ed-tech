from fastapi import APIRouter, HTTPException, Body, Depends
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from ..database import db_manager
from ..config import settings
from datetime import datetime
import uuid
import hashlib

router = APIRouter(prefix="/api/users", tags=["users"])

class UserCreate(BaseModel):
    email: str
    username: str
    password: str
    name: Optional[str] = None

class UserLogin(BaseModel):
    email: str
    password: str

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    current_password: Optional[str] = None
    new_password: Optional[str] = None

def hash_password(password: str) -> str:
    """Create a SHA-256 hash of a password"""
    return hashlib.sha256(password.encode()).hexdigest()

@router.post("/register", response_model=Dict[str, Any])
async def register_user(user_data: UserCreate):
    """
    Register a new user account.
    """
    users_col = db_manager.get_collection("users")
    
    # Check if email already exists
    existing_email = await users_col.find_one({"email": user_data.email})
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Check if username already exists
    existing_username = await users_col.find_one({"username": user_data.username})
    if existing_username:
        raise HTTPException(status_code=400, detail="Username already taken")
    
    # Create user
    user_id = str(uuid.uuid4())
    timestamp = datetime.utcnow().isoformat()
    
    new_user = {
        "user_id": user_id,
        "email": user_data.email,
        "username": user_data.username,
        "password_hash": hash_password(user_data.password),
        "name": user_data.name or user_data.username,
        "created_at": timestamp,
        "updated_at": timestamp,
        "last_active": timestamp
    }
    
    await users_col.insert_one(new_user)
    
    # Return user without password
    user_response = {
        "user_id": user_id,
        "email": user_data.email,
        "username": user_data.username,
        "name": new_user["name"],
        "created_at": timestamp
    }
    
    return {
        "message": "User registered successfully",
        "user": user_response
    }

@router.post("/login", response_model=Dict[str, Any])
async def login_user(login_data: UserLogin):
    """
    Login with email and password.
    """
    users_col = db_manager.get_collection("users")
    
    # Find user by email
    user = await users_col.find_one({"email": login_data.email})
    
    if not user or user.get("password_hash") != hash_password(login_data.password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Update last active timestamp
    timestamp = datetime.utcnow().isoformat()
    await users_col.update_one(
        {"user_id": user["user_id"]},
        {"$set": {"last_active": timestamp}}
    )
    
    # Return user without password
    user_response = {
        "user_id": user["user_id"],
        "email": user["email"],
        "username": user["username"],
        "name": user.get("name", user["username"]),
        "created_at": user["created_at"]
    }
    
    return {
        "message": "Login successful",
        "user": user_response,
        "session": {
            "user_id": user["user_id"],
            "timestamp": timestamp
        }
    }

@router.get("/{user_id}", response_model=Dict[str, Any])
async def get_user_profile(user_id: str):
    """
    Get user profile information.
    """
    users_col = db_manager.get_collection("users")
    
    # Find user by ID
    user = await users_col.find_one({"user_id": user_id})
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Return user without password
    return {
        "user_id": user["user_id"],
        "email": user["email"],
        "username": user["username"],
        "name": user.get("name", user["username"]),
        "created_at": user["created_at"],
        "last_active": user.get("last_active")
    }

@router.put("/{user_id}", response_model=Dict[str, Any])
async def update_user_profile(user_id: str, user_data: UserUpdate):
    """
    Update user profile information.
    """
    users_col = db_manager.get_collection("users")
    
    # Find user by ID
    user = await users_col.find_one({"user_id": user_id})
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Prepare update data
    update_data = {}
    
    if user_data.name is not None:
        update_data["name"] = user_data.name
    
    if user_data.email is not None:
        # Check if email already used by another user
        existing_email = await users_col.find_one({
            "email": user_data.email,
            "user_id": {"$ne": user_id}  # not equal to current user
        })
        if existing_email:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        update_data["email"] = user_data.email
    
    # Handle password change
    if user_data.current_password and user_data.new_password:
        if user.get("password_hash") != hash_password(user_data.current_password):
            raise HTTPException(status_code=400, detail="Current password is incorrect")
        
        update_data["password_hash"] = hash_password(user_data.new_password)
    
    # If there are updates, apply them
    if update_data:
        update_data["updated_at"] = datetime.utcnow().isoformat()
        
        await users_col.update_one(
            {"user_id": user_id},
            {"$set": update_data}
        )
    
    # Get updated user
    updated_user = await users_col.find_one({"user_id": user_id})
    
    # Return updated user without password
    return {
        "message": "Profile updated successfully",
        "user": {
            "user_id": updated_user["user_id"],
            "email": updated_user["email"],
            "username": updated_user["username"],
            "name": updated_user.get("name", updated_user["username"]),
            "updated_at": updated_user["updated_at"]
        }
    }

@router.get("/{user_id}/stats", response_model=Dict[str, Any])
async def get_user_stats(user_id: str):
    """
    Get learning statistics for a user.
    """
    users_col = db_manager.get_collection("users")
    assessments_col = db_manager.get_collection("assessments")
    progress_col = db_manager.get_collection("user_progress")
    
    # Check if user exists
    user = await users_col.find_one({"user_id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get assessment data
    assessments = await assessments_col.find({"user_id": user_id}).to_list()
    
    # Get progress data
    progress = await progress_col.find({"user_id": user_id}).to_list()
    
    # Calculate assessment stats
    total_assessments = len(assessments)
    completed_assessments = sum(1 for a in assessments if a.get("status") == "completed")
    
    assessment_scores = []
    for assessment in assessments:
        if assessment.get("status") == "completed":
            correct = sum(1 for a in assessment.get("answers", {}).values() if a.get("is_correct", False))
            total = len(assessment.get("questions", []))
            if total > 0:
                assessment_scores.append((correct / total) * 100)
    
    avg_score = sum(assessment_scores) / len(assessment_scores) if assessment_scores else 0
    
    # Calculate learning progress
    modules_started = len(progress)
    modules_completed = sum(1 for p in progress if p.get("completed", False))
    total_time_spent = sum(p.get("time_spent_minutes", 0) for p in progress)
    
    # Calculate subject-specific stats
    subjects = {}
    
    # Add subjects from assessments
    for assessment in assessments:
        subject = assessment.get("subject")
        if subject and subject not in subjects:
            subjects[subject] = {
                "name": subject,
                "assessments_taken": 0,
                "assessments_completed": 0,
                "average_score": 0,
                "modules_started": 0,
                "modules_completed": 0,
                "time_spent_minutes": 0
            }
        
        if subject:
            subjects[subject]["assessments_taken"] += 1
            if assessment.get("status") == "completed":
                subjects[subject]["assessments_completed"] += 1
    
    # Calculate assessment scores by subject
    for subject in subjects:
        subject_scores = []
        for assessment in assessments:
            if assessment.get("subject") == subject and assessment.get("status") == "completed":
                correct = sum(1 for a in assessment.get("answers", {}).values() if a.get("is_correct", False))
                total = len(assessment.get("questions", []))
                if total > 0:
                    subject_scores.append((correct / total) * 100)
        
        if subject_scores:
            subjects[subject]["average_score"] = sum(subject_scores) / len(subject_scores)
    
    # Add progress data by subject
    for entry in progress:
        # Find which subject this belongs to by checking the module ID
        # This assumes module IDs follow a pattern like "subject_level_skill"
        module_id = entry.get("module_id", "")
        if "_" in module_id:
            subject = module_id.split("_")[0]  # Extract subject from module ID
            
            if subject in subjects:
                subjects[subject]["modules_started"] += 1
                subjects[subject]["time_spent_minutes"] += entry.get("time_spent_minutes", 0)
                
                if entry.get("completed", False):
                    subjects[subject]["modules_completed"] += 1
    
    return {
        "user_id": user_id,
        "username": user.get("username"),
        "assessment_stats": {
            "total": total_assessments,
            "completed": completed_assessments,
            "completion_rate": (completed_assessments / total_assessments * 100) if total_assessments > 0 else 0,
            "average_score": avg_score
        },
        "learning_stats": {
            "modules_started": modules_started,
            "modules_completed": modules_completed,
            "completion_rate": (modules_completed / modules_started * 100) if modules_started > 0 else 0,
            "total_time_spent_minutes": total_time_spent
        },
        "by_subject": list(subjects.values()),
        "generated_at": datetime.utcnow().isoformat()
    }