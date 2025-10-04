// FILE: src/components/SubjectsPage.js
import React, { useState, useEffect } from 'react';
import { BookOpen } from 'lucide-react';
import api from '../services/api';
import './SubjectsPage.css';

export function SubjectsPage({ user, setCurrentPage, setSelectedSubject }) {
    const [subjects, setSubjects] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchSubjects = async () => {
            try {
                const data = await api.getAllSubjects();
                setSubjects(data.subjects || []);
            } catch (err) {
                console.error('Failed to fetch subjects:', err);
            } finally {
                setLoading(false);
            }
        };
        fetchSubjects();
    }, []);

    const handleSubjectClick = (subject) => {
        setSelectedSubject(subject);
        setCurrentPage('assessment');
    };

    if (loading) {
        return <div className="container loading-text">Loading subjects...</div>;
    }

    return (
        <div className="container subjects-page">
            <div className="subjects-header">
                <h2>Choose Your Subject</h2>
            </div>

            <div className="subjects-grid">
                {subjects.map((subject) => (
                    <div
                        key={subject.id}
                        className="subject-card"
                        onClick={() => handleSubjectClick(subject)}
                    >
                        <BookOpen />
                        <h3>{subject.name}</h3>
                        <p>{subject.description}</p>
                        <div className="subject-stats">
                            <span>{subject.question_count} questions</span>
                            <span>{Object.keys(subject.skills).length} skills</span>
                        </div>
                        <button className="subject-button">Start Assessment</button>
                    </div>
                ))}
            </div>
        </div>
    );
}
