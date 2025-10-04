// FILE: src/components/DashboardPage.js
import React, { useState, useEffect } from 'react';
import { BarChart3, Award, Clock } from 'lucide-react';
import api from '../services/api';
import './DashboardPage.css';

export function DashboardPage({ user }) {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchStats = async () => {
      try { const data = await api.getUserStats(user.user_id); setStats(data); }
      catch (err) { console.error(err); }
      finally { setLoading(false); }
    };
    fetchStats();
  }, [user]);

  if (loading) return <div className="container loading-text">Loading dashboard...</div>;

  return (
    <div className="container dashboard-page">
      <div className="dashboard-header"><h2>Your Dashboard</h2></div>
      <div className="stats-grid">
        <div className="stat-card">
          <BarChart3 style={{ color: '#2563eb' }} />
          <h3>Assessments</h3>
          <div className="stat-value">{stats?.assessment_stats.completed}</div>
          <div className="stat-detail">{stats?.assessment_stats.completion_rate.toFixed(1)}% completion rate</div>
        </div>
        <div className="stat-card">
          <Award style={{ color: '#9333ea' }} />
          <h3>Average Score</h3>
          <div className="stat-value">{stats?.assessment_stats.average_score.toFixed(1)}%</div>
        </div>
        <div className="stat-card">
          <Clock style={{ color: '#16a34a' }} />
          <h3>Time Spent</h3>
          <div className="stat-value">{stats?.learning_stats.total_time_spent_minutes}</div>
          <div className="stat-detail">minutes</div>
        </div>
      </div>

      {stats?.by_subject?.length > 0 && (
        <div className="progress-section">
          <h3>Progress by Subject</h3>
          <div className="progress-list">
            {stats.by_subject.map(subject => (
              <div key={subject.name} className="progress-item">
                <div className="progress-header">
                  <span>{subject.name}</span>
                  <span>Score: {subject.average_score.toFixed(1)}%</span>
                </div>
                <div className="progress-bar-full">
                  <div className="progress-bar-fill" style={{ width: `${subject.average_score}%` }} />
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
