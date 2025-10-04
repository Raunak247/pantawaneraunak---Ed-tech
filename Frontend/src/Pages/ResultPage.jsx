// FILE: src/components/ResultsPage.js
import React, { useState, useEffect } from 'react';
import { Award } from 'lucide-react';
import api from '../services/api';
import './ResultsPage.css';

export function ResultsPage({ user, assessmentId, setCurrentPage }) {
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchResults = async () => {
      try { const data = await api.getAssessmentResults(assessmentId); setResults(data); }
      catch (err) { console.error(err); }
      finally { setLoading(false); }
    };
    if (assessmentId) fetchResults();
  }, [assessmentId]);

  if (loading) return <div className="container loading-text">Loading results...</div>;
  if (!results) return <div className="container loading-text">No results available</div>;

  const getMasteryLevel = mastery => (mastery >= 0.75 ? 'high' : mastery >= 0.5 ? 'medium' : 'low');

  return (
    <div className="results-page">
      <div className="results-container">
        <div className="results-header">
          <Award className="results-icon" />
          <h2>Assessment Results</h2>
          <p>{results.subject}</p>
        </div>

        <div className="score-grid">
          <div className="score-card blue">
            <p>Score</p>
            <div className="score-value">{results.score.percentage}%</div>
            <p>{results.score.correct} / {results.score.total} correct</p>
          </div>
          <div className="score-card purple">
            <p>Skills Assessed</p>
            <div className="score-value">{Object.keys(results.skill_masteries).length}</div>
          </div>
          <div className="score-card green">
            <p>Average Mastery</p>
            <div className="score-value">{(Object.values(results.skill_masteries).reduce((a,b)=>a+b,0)/Object.keys(results.skill_masteries).length*100).toFixed(0)}%</div>
          </div>
        </div>

        <div className="mastery-section">
          <h3>Skill Masteries</h3>
          <div className="mastery-list">
            {Object.entries(results.skill_masteries).map(([skill, mastery]) => {
              const level = getMasteryLevel(mastery);
              return (
                <div key={skill} className="mastery-item">
                  <div className="mastery-header">
                    <span>{skill.replace(/_/g,' ').replace(/\b\w/g,l=>l.toUpperCase())}</span>
                    <span className={`mastery-score ${level}`}>{(mastery*100).toFixed(0)}%</span>
                  </div>
                  <div className={`mastery-bar-container`}>
                    <div className={`mastery-bar ${level}`} style={{ width: `${mastery*100}%` }} />
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {results.learning_path && (
          <div className="learning-path-section">
            <h3>Your Personalized Learning Path</h3>
            <p>{results.learning_path.recommendation_reason}</p>
          </div>
        )}

        <div className="results-actions">
          <button onClick={() => setCurrentPage('subjects')} className="primary-action">Take Another Assessment</button>
          <button onClick={() => setCurrentPage('dashboard')} className="secondary-action">View Dashboard</button>
        </div>
      </div>
    </div>
  );
}
