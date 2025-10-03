from typing import Dict, Tuple, Optional, List, Any
import random
import logging

logger = logging.getLogger(__name__)

class BKTModel:
    """
    Bayesian Knowledge Tracing model for adaptive learning.
    This implementation works with the entire backend structure, including
    the Firebase database and the new API endpoints.
    """
    def __init__(
        self,
        p_init: float = 0.3,
        p_learn: float = 0.2,
        p_slip: float = 0.1,
        p_guess: float = 0.25
    ):
        # Probability that a student has initially mastered the skill
        self.p_init = p_init
        # Probability that a student will learn a skill at each opportunity
        self.p_learn = p_learn
        # Probability that a student makes a mistake despite knowing the skill
        self.p_slip = p_slip
        # Probability that a student answers correctly despite not knowing the skill
        self.p_guess = p_guess
        
        logger.debug(f"BKT Model initialized with: p_init={p_init}, p_learn={p_learn}, p_slip={p_slip}, p_guess={p_guess}")
    
    def initialize_skill(self, skill_name: str = None) -> float:
        """
        Initialize the mastery level for a skill.
        
        Parameters:
        - skill_name: Optional skill name to customize initial mastery
        
        Returns:
        - Initial mastery level (0-1)
        """
        # Could customize initial mastery based on skill if needed
        return self.p_init
        
    def analyze_assessment_results(
        self,
        skill_masteries: Dict[str, float],
        answers: Dict[str, Dict],
        question_details: Dict[str, Dict]
    ) -> Dict[str, Any]:
        """
        Analyze assessment results to provide insights and recommendations.
        
        Parameters:
        - skill_masteries: Dictionary of skill masteries after assessment
        - answers: Dictionary mapping question IDs to answer details
        - question_details: Dictionary mapping question IDs to question metadata
        
        Returns:
        - Dictionary with analysis results
        """
        # Calculate overall score
        total_questions = len(answers)
        correct_count = sum(1 for a in answers.values() if a.get('is_correct', False))
        score_percentage = (correct_count / total_questions) * 100 if total_questions > 0 else 0
        
        # Analyze skills
        strengths = []
        weaknesses = []
        needs_practice = []
        
        for skill, mastery in skill_masteries.items():
            if mastery >= 0.75:
                strengths.append(skill)
            elif mastery <= 0.4:
                weaknesses.append(skill)
            else:
                needs_practice.append(skill)
                
        # Analyze performance by difficulty level
        performance_by_difficulty = {
            "very_easy": {"total": 0, "correct": 0},
            "easy": {"total": 0, "correct": 0},
            "medium": {"total": 0, "correct": 0},
            "hard": {"total": 0, "correct": 0}
        }
        
        for q_id, answer in answers.items():
            if q_id in question_details:
                difficulty = question_details[q_id].get('difficulty', 'medium')
                if difficulty in performance_by_difficulty:
                    performance_by_difficulty[difficulty]["total"] += 1
                    if answer.get('is_correct', False):
                        performance_by_difficulty[difficulty]["correct"] += 1
        
        # Calculate percentages
        for difficulty, data in performance_by_difficulty.items():
            if data["total"] > 0:
                data["percentage"] = (data["correct"] / data["total"]) * 100
            else:
                data["percentage"] = 0
                
        return {
            "score": {
                "correct": correct_count,
                "total": total_questions,
                "percentage": score_percentage
            },
            "skill_analysis": {
                "strengths": strengths,
                "weaknesses": weaknesses,
                "needs_practice": needs_practice
            },
            "difficulty_analysis": performance_by_difficulty,
            "overall_mastery": sum(skill_masteries.values()) / len(skill_masteries) if skill_masteries else 0
        }
        
    def generate_learning_recommendations(
        self, 
        skill_masteries: Dict[str, float],
        subject: str
    ) -> List[Dict[str, Any]]:
        """
        Generate learning recommendations based on skill masteries.
        
        Parameters:
        - skill_masteries: Dictionary mapping skills to mastery levels
        - subject: The subject area
        
        Returns:
        - List of recommended learning modules
        """
        recommendations = []
        
        # Sort skills by mastery level
        sorted_skills = sorted(skill_masteries.items(), key=lambda x: x[1])
        
        # Generate recommendations prioritizing weaker skills
        for skill, mastery in sorted_skills:
            if mastery < 0.4:
                # Weak skill - needs foundational content
                recommendations.append({
                    "id": f"{subject}_remedial_{skill}",
                    "title": f"Building foundations in {skill.replace('_', ' ')}",
                    "type": "remedial",
                    "skill": skill,
                    "mastery_level": "basic",
                    "priority": "high",
                    "description": f"Focus on fundamentals of {skill.replace('_', ' ')} to build a solid foundation"
                })
            elif mastery < 0.7:
                # Moderate skill - needs practice
                recommendations.append({
                    "id": f"{subject}_practice_{skill}",
                    "title": f"Practicing {skill.replace('_', ' ')}",
                    "type": "practice",
                    "skill": skill,
                    "mastery_level": "intermediate",
                    "priority": "medium",
                    "description": f"Reinforce your understanding of {skill.replace('_', ' ')} through targeted practice"
                })
            else:
                # Strong skill - can advance
                recommendations.append({
                    "id": f"{subject}_advanced_{skill}",
                    "title": f"Advanced {skill.replace('_', ' ')}",
                    "type": "advanced",
                    "skill": skill,
                    "mastery_level": "advanced",
                    "priority": "low",
                    "description": f"Deepen your expertise in {skill.replace('_', ' ')} with advanced concepts"
                })
                
        return recommendations
    
    def update_mastery(
        self,
        current_mastery: float,
        is_correct: bool,
        question_difficulty: str = None
    ) -> float:
        """
        Update the mastery level based on the student's response.
        
        Parameters:
        - current_mastery: Current mastery level (0-1)
        - is_correct: Whether the student's answer was correct
        - question_difficulty: Optional difficulty level to adjust parameters
        
        Returns:
        - Updated mastery level (0-1)
        """
        # Adjust parameters based on question difficulty if provided
        p_slip = self.p_slip
        p_guess = self.p_guess
        p_learn = self.p_learn
        
        if question_difficulty:
            # Adjust slip probability based on difficulty
            if question_difficulty == "hard":
                p_slip = min(self.p_slip * 1.5, 0.2)  # Higher slip chance for hard questions
                p_learn = min(self.p_learn * 1.2, 0.3)  # Higher learning for hard questions
            elif question_difficulty == "easy":
                p_slip = max(self.p_slip * 0.7, 0.05)  # Lower slip chance for easy questions
                p_learn = max(self.p_learn * 0.8, 0.1)  # Lower learning for easy questions
            elif question_difficulty == "very_easy":
                p_slip = max(self.p_slip * 0.5, 0.03)  # Even lower slip chance for very easy
                p_learn = max(self.p_learn * 0.6, 0.05)  # Even lower learning for very easy
        
        # Calculate posterior probability using Bayes' theorem
        if is_correct:
            numerator = current_mastery * (1 - p_slip)
            denominator = (
                current_mastery * (1 - p_slip) +
                (1 - current_mastery) * p_guess
            )
        else:
            numerator = current_mastery * p_slip
            denominator = (
                current_mastery * p_slip +
                (1 - current_mastery) * (1 - p_guess)
            )
        
        # Update knowledge based on evidence
        p_known_given_response = numerator / denominator if denominator > 0 else current_mastery
        
        # Apply learning probability
        new_mastery = p_known_given_response + (1 - p_known_given_response) * p_learn
        
        # Ensure result is within valid range
        return min(max(new_mastery, 0.0), 1.0)
    
    def select_next_question(
        self,
        skill_masteries: Dict[str, float],
        available_questions: List[Dict[str, Any]],
        threshold: float = 0.8,
        difficulty_weight: float = 0.3,
        exclude_ids: List[str] = None
    ) -> Tuple[Optional[dict], str]:
        """
        Select the next question based on skill masteries.
        
        Parameters:
        - skill_masteries: Dictionary mapping skill names to mastery levels (0-1)
        - available_questions: List of question objects to choose from
        - threshold: Mastery level below which a skill is considered weak
        - difficulty_weight: How much to factor difficulty into question selection
        - exclude_ids: List of question IDs to exclude (already answered)
        
        Returns:
        - Tuple of (selected question, reason for selection)
        """
        if not available_questions:
            return None, "No questions available"
        
        # Filter out excluded questions
        if exclude_ids:
            available_questions = [
                q for q in available_questions 
                if q.get('id') not in exclude_ids
            ]
            
        if not available_questions:
            return None, "No questions available after filtering"
        
        # Identify weak skills
        weak_skills = {
            skill: mastery
            for skill, mastery in skill_masteries.items()
            if mastery < threshold
        }
        
        # Strategy 1: Target the weakest skill
        if weak_skills:
            target_skill = min(weak_skills.keys(), key=lambda k: weak_skills[k])
            
            # Find questions that target this skill
            matching_questions = [
                q for q in available_questions
                if q.get('skill') == target_skill
            ]
            
            if matching_questions:
                # Further refine by selecting appropriate difficulty
                mastery = weak_skills[target_skill]
                
                # Select difficulty based on mastery level
                if mastery < 0.3:
                    # For low mastery, prefer easier questions
                    preferred_difficulties = ["very_easy", "easy"]
                elif mastery < 0.6:
                    # For medium mastery, prefer medium difficulty
                    preferred_difficulties = ["easy", "medium"]
                else:
                    # For higher mastery (but still below threshold), prefer harder questions
                    preferred_difficulties = ["medium", "hard"]
                
                # Try to find questions with preferred difficulty
                preferred_questions = [
                    q for q in matching_questions
                    if q.get('difficulty') in preferred_difficulties
                ]
                
                # If we have preferred difficulty questions, choose from those
                if preferred_questions:
                    question = random.choice(preferred_questions)
                    return question, f"Targeting weak skill: {target_skill} (mastery: {mastery:.2f}) with {question.get('difficulty', 'medium')} difficulty"
                
                # Otherwise choose any question for the weak skill
                question = random.choice(matching_questions)
                return question, f"Targeting weak skill: {target_skill} (mastery: {mastery:.2f})"
        
        # Strategy 2: If no weak skills or no matching questions, choose based on balanced exploration
        # Group questions by skill
        skill_groups = {}
        for q in available_questions:
            skill = q.get('skill', 'unknown')
            if skill not in skill_groups:
                skill_groups[skill] = []
            skill_groups[skill].append(q)
        
        # If we have multiple skills, try to balance exposure to different skills
        if len(skill_groups) > 1:
            # Find least practiced skill (assuming practice is reflected in mastery)
            if skill_masteries:
                least_practiced = min(
                    [s for s in skill_groups.keys() if s in skill_masteries],
                    key=lambda s: skill_masteries.get(s, 0),
                    default=None
                )
                
                if least_practiced and least_practiced in skill_groups:
                    question = random.choice(skill_groups[least_practiced])
                    mastery = skill_masteries.get(least_practiced, 0)
                    return question, f"Balancing skill exposure: {least_practiced} (mastery: {mastery:.2f})"
        
        # Strategy 3: Random selection as fallback
        question = random.choice(available_questions)
        return question, "Random selection (all skills above threshold or no skill match)"
