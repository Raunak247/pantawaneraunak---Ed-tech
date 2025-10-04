// FILE: src/components/Header.js
import React, { useState } from 'react';
import { Menu, X, Brain, BookOpen, BarChart3, User, LogOut, Home } from 'lucide-react';
import './Header.css';

export function Header({ user, onLogout, currentPage, setCurrentPage }) {
    const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

    return (
        <header className="header">
            <div className="header-container">
                <div className="header-content">
                    <div className="header-logo">
                        <Brain />
                        <h1>AdaptLearn</h1>
                    </div>

                    <nav className="header-nav desktop">
                        <button
                            onClick={() => setCurrentPage('home')}
                            className={`nav-button ${currentPage === 'home' ? 'active' : ''}`}
                        >
                            <Home />
                            <span>Home</span>
                        </button>

                        {user && (
                            <>
                                <button
                                    onClick={() => setCurrentPage('subjects')}
                                    className={`nav-button ${currentPage === 'subjects' ? 'active' : ''}`}
                                >
                                    <BookOpen />
                                    <span>Subjects</span>
                                </button>
                                <button
                                    onClick={() => setCurrentPage('dashboard')}
                                    className={`nav-button ${currentPage === 'dashboard' ? 'active' : ''}`}
                                >
                                    <BarChart3 />
                                    <span>Dashboard</span>
                                </button>
                                <button
                                    onClick={() => setCurrentPage('profile')}
                                    className={`nav-button ${currentPage === 'profile' ? 'active' : ''}`}
                                >
                                    <User />
                                    <span>{user.username}</span>
                                </button>
                                <button onClick={onLogout} className="logout-button">
                                    <LogOut />
                                    <span>Logout</span>
                                </button>
                            </>
                        )}
                    </nav>

                    <button
                        className="mobile-menu-button"
                        onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                    >
                        {mobileMenuOpen ? <X /> : <Menu />}
                    </button>
                </div>

                {mobileMenuOpen && (
                    <nav className="mobile-nav">
                        <button onClick={() => { setCurrentPage('home'); setMobileMenuOpen(false); }}>Home</button>
                        {user && (
                            <>
                                <button onClick={() => { setCurrentPage('subjects'); setMobileMenuOpen(false); }}>Subjects</button>
                                <button onClick={() => { setCurrentPage('dashboard'); setMobileMenuOpen(false); }}>Dashboard</button>
                                <button onClick={() => { setCurrentPage('profile'); setMobileMenuOpen(false); }}>Profile</button>
                                <button onClick={() => { onLogout(); setMobileMenuOpen(false); }} className="logout-button">Logout</button>
                            </>
                        )}
                    </nav>
                )}
            </div>
        </header>
    );
}
