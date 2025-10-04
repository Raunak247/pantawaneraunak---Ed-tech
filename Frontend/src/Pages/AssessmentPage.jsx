// FILE: src/components/AssessmentPage.js
import React, { useState, useEffect } from 'react';
import { Award } from 'lucide-react';
import api from '../services/api';
import './AssessmentPage.css';

export function AssessmentPage({ user, selectedSubject, setCurrentPage, setAssessmentId }) {
  const [assessmentIdLocal, setAssessmentIdLocal] = useState(null);
  const [currentQuestion, setCurrentQuestion] = useState(null);
  const [selectedAnswer, setSelectedAnswer] = useState('');
  const [loading, setLoading] = useState(false);
  const [feedback, setFeedback] = useState(null);
  const [questionIndex, setQuestionIndex] = useState(0);
  const [totalQuestions, setTotalQuestions] = useState(0);
  const [isComplete, setIsComplete] = useState(false);

  useEffect(() => { startAssessment(); }, []);

  const startAssessment = async () => {
    setLoading(true);
    try {
      const result = await api.startAssessment({
        user_id: user.user_id,
        subject: selectedSubject.id,
        question_count: 10
      });
      setAssessmentIdLocal(result.assessment_id);
      setAssessmentId(result.assessment_id);
      setCurrentQuestion(result.question);
      setQuestionIndex(result.current_question_index);
      setTotalQuestions(result.total_questions);
    } catch (err) { console.error(err); }
    finally { setLoading(false); }
  };

  const handleSubmitAnswer = async () => {
    if (!selectedAnswer) return;
    setLoading(true);
    try {
      const result = await api.submitAssessmentAnswer({
        assessment_id: assessmentIdLocal,
        question_id: currentQuestion.id,
        answer: selectedAnswer
      });
      setFeedback({ is_correct: result.is_correct, correct_answer: result.correct_answer });
      setTimeout(() => {
        if (result.is_complete) setIsComplete(true);
        else {
          setCurrentQuestion(result.next_question);
          setQuestionIndex(result.current_question_index);
          setSelectedAnswer('');
          setFeedback(null);
        }
      }, 2000);
    } catch (err) { console.error(err); }
    finally { setLoading(false); }
  };

  const viewResults = () => setCurrentPage('results');

  if (loading && !currentQuestion) return <div className="container loading-text">Loading assessment...</div>;
  if (isComplete) {
    return (
      <div className="container completion-container">
        <Award className="completion-icon" />
        <h2>Assessment Complete!</h2>
        <p>Great job! You've completed all questions.</p>
        <button onClick={viewResults} className="cta-button">View Results</button>
      </div>
    );
  }

  return (
    <div className="assessment-page">
      <div className="assessment-container">
        <div className="assessment-progress">
          <div className="progress-info">
            <span>Question {questionIndex + 1} of {totalQuestions}</span>
            <span>Skill: {currentQuestion?.skill}</span>
          </div>
          <div className="progress-bar-container">
            <div className="progress-bar" style={{ width: `${((questionIndex + 1) / totalQuestions) * 100}%` }} />
          </div>
        </div>

        <h3 className="question-text">{currentQuestion?.text}</h3>

        {feedback && (
          <div className={`feedback-box ${feedback.is_correct ? 'correct' : 'incorrect'}`}>
            <p>{feedback.is_correct ? '✓ Correct!' : '✗ Incorrect'}</p>
            {!feedback.is_correct && <p className="correct-answer">Correct answer: {feedback.correct_answer}</p>}
          </div>
        )}

        <div className="options-container">
          {currentQuestion?.options.map((option, index) => (
            <button
              key={index}
              onClick={() => !feedback && setSelectedAnswer(option)}
              disabled={!!feedback}
              className={`option-button ${selectedAnswer === option ? 'selected' : ''}`}
            >
              {option}
            </button>
          ))}
        </div>

        <button
          onClick={handleSubmitAnswer}
          disabled={!selectedAnswer || loading || !!feedback}
          className="submit-button"
        >
          {loading ? 'Submitting...' : 'Submit Answer'}
        </button>
      </div>
    </div>
  );
}
