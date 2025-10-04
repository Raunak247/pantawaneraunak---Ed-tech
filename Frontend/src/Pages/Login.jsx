// FILE: src/components/AuthPage.js
import React, { useState } from 'react';
import { Brain } from 'lucide-react';
import api from '../services/api';
import './AuthPage.css';

export function AuthPage({ onLogin }) {
  const [isLogin, setIsLogin] = useState(true);
  const [formData, setFormData] = useState({ email: '', password: '', username: '', name: '' });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      if (isLogin) {
        const result = await api.login({ email: formData.email, password: formData.password });
        if (result.user) onLogin(result.user);
        else setError(result.detail || 'Login failed');
      } else {
        const result = await api.register(formData);
        if (result.user) onLogin(result.user);
        else setError(result.detail || 'Registration failed');
      }
    } catch (err) {
      setError('Network error. Check backend is running.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-container">
        <div className="auth-header">
          <Brain className="auth-icon" />
          <h2>{isLogin ? 'Welcome Back' : 'Join AdaptLearn'}</h2>
          <p>{isLogin ? 'Sign in to continue learning' : 'Start your learning journey'}</p>
        </div>

        {error && <div className="auth-error">{error}</div>}

        <form onSubmit={handleSubmit} className="auth-form">
          {!isLogin && (
            <>
              <input
                type="text"
                placeholder="Username"
                value={formData.username}
                onChange={(e) => setFormData({ ...formData, username: e.target.value })}
                className="auth-input"
                required
              />
              <input
                type="text"
                placeholder="Full Name"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                className="auth-input"
              />
            </>
          )}
          <input
            type="email"
            placeholder="Email"
            value={formData.email}
            onChange={(e) => setFormData({ ...formData, email: e.target.value })}
            className="auth-input"
            required
          />
          <input
            type="password"
            placeholder="Password"
            value={formData.password}
            onChange={(e) => setFormData({ ...formData, password: e.target.value })}
            className="auth-input"
            required
          />
          <button type="submit" disabled={loading} className="auth-submit">
            {loading ? 'Please wait...' : isLogin ? 'Sign In' : 'Sign Up'}
          </button>
        </form>

        <div className="auth-toggle">
          <button onClick={() => setIsLogin(!isLogin)}>
            {isLogin ? "Don't have an account? Sign up" : 'Already have an account? Sign in'}
          </button>
        </div>
      </div>
    </div>
  );
}
