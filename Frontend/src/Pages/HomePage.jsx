// FILE: src/components/HomePage.js
import React from 'react';
import { Brain, Award, TrendingUp } from 'lucide-react';
import './HomePage.css';
import api from '../services/api';
export function HomePage({ user, setCurrentPage }) {
  return (
    <div className="container home-page">
      <div className="home-header">
        <h1>Welcome to AdaptLearn</h1>
        <p>
          Personalized learning powered by Bayesian Knowledge Tracing. 
          Our adaptive platform adjusts to your skill level in real-time.
        </p>
      </div>

      <div className="features-grid">
        <div className="feature-card">
          <Brain style={{ color: '#2563eb' }} />
          <h3>Adaptive Learning</h3>
          <p>Questions adapt to your skill level using advanced BKT algorithms</p>
        </div>
        <div className="feature-card">
          <Award style={{ color: '#9333ea' }} />
          <h3>Skill Mastery</h3>
          <p>Track your progress across different skills and subjects</p>
        </div>
        <div className="feature-card">
          <TrendingUp style={{ color: '#16a34a' }} />
          <h3>Personalized Path</h3>
          <p>Get customized learning recommendations based on your performance</p>
        </div>
      </div>

      <div className="home-cta">
        {user ? (
          <button onClick={() => setCurrentPage('subjects')} className="cta-button">
            Start Learning
          </button>
        ) : (
          <p style={{ color: '#6b7280' }}>Please sign in to start learning</p>
        )}
      </div>
    </div>
  );
}
