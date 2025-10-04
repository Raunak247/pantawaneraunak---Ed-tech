// API Configuration
const API_BASE_URL = 'http://localhost:8000';

// API Service
const api = {
  // Health check
  healthCheck: async () => {
    const response = await fetch(`${API_BASE_URL}/health`);
    return response.json();
  },

  // Subjects
  getAllSubjects: async () => {
    const response = await fetch(`${API_BASE_URL}/api/subjects/`);
    return response.json();
  },

  getSubjectDetails: async (subjectId) => {
    const response = await fetch(`${API_BASE_URL}/api/subjects/${subjectId}`);
    return response.json();
  },

  // Users
  register: async (userData) => {
    const response = await fetch(`${API_BASE_URL}/api/users/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(userData)
    });
    return response.json();
  },

  login: async (credentials) => {
    const response = await fetch(`${API_BASE_URL}/api/users/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(credentials)
    });
    return response.json();
  },

  getUserProfile: async (userId) => {
    const response = await fetch(`${API_BASE_URL}/api/users/${userId}`);
    return response.json();
  },

  getUserStats: async (userId) => {
    const response = await fetch(`${API_BASE_URL}/api/users/${userId}/stats`);
    return response.json();
  },

  // Assessment
  startAssessment: async (data) => {
    const response = await fetch(`${API_BASE_URL}/api/assessment/start`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    return response.json();
  },

  submitAssessmentAnswer: async (data) => {
    const response = await fetch(`${API_BASE_URL}/api/assessment/answer`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    return response.json();
  },

  getAssessmentResults: async (assessmentId) => {
    const response = await fetch(`${API_BASE_URL}/api/assessment/${assessmentId}/results`);
    return response.json();
  },

  // Learning
  getLearningPath: async (userId, subject) => {
    const response = await fetch(`${API_BASE_URL}/api/learning/path/${userId}/${subject}`);
    return response.json();
  },

  updateProgress: async (data) => {
    const response = await fetch(`${API_BASE_URL}/api/learning/progress/update`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    return response.json();
  },

  getNextQuestion: async (userId, subject) => {
    const response = await fetch(`${API_BASE_URL}/api/learning/next-question/${userId}/${subject}`);
    return response.json();
  },

  submitAnswer: async (data) => {
    const response = await fetch(`${API_BASE_URL}/api/learning/submit-answer`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    return response.json();
  }
};

export default api;