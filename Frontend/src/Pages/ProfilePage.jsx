// FILE: src/components/ProfilePage.js
import React from 'react';
import { User } from 'lucide-react';
import './ProfilePage.css';
import api from '../services/api';

export function ProfilePage({ user }) {
  return (
    <div className="profile-page">
      <div className="profile-container">
        <div className="profile-header">
          <div className="profile-avatar"><User /></div>
          <h2>{user.name || user.username}</h2>
          <p>@{user.username}</p>
        </div>

        <div className="profile-details">
          <div className="profile-field"><label>Email</label><p>{user.email}</p></div>
          <div className="profile-field"><label>User ID</label><p className="small">{user.user_id}</p></div>
          <div className="profile-field"><label>Member Since</label><p>{new Date(user.created_at).toLocaleDateString()}</p></div>
        </div>
      </div>
    </div>
  );
}
