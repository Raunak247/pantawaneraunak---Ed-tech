// FILE: src/components/Footer.js
import React from 'react';
import './Footer.css';

export function Footer() {
    return (
        <footer className="footer">
            <div className="footer-container">
                <div className="footer-grid">
                    <div className="footer-section">
                        <h3>About AdaptLearn</h3>
                        <p>
                            Personalized learning powered by Bayesian Knowledge Tracing.
                            Adaptive assessments that grow with you.
                        </p>
                    </div>
                    <div className="footer-section">
                        <h3>Quick Links</h3>
                        <ul>
                            <li><a href="#">How It Works</a></li>
                            <li><a href="#">Support</a></li>
                            <li><a href="#">Privacy Policy</a></li>
                        </ul>
                    </div>
                    <div className="footer-section">
                        <h3>Contact</h3>
                        <p>
                            Email: support@adaptlearn.com<br />
                            Phone: +1 (555) 123-4567
                        </p>
                    </div>
                </div>
                <div className="footer-bottom">
                    <p>&copy; 2025 AdaptLearn. All rights reserved. Powered by BKT Technology.</p>
                </div>
            </div>
        </footer>
    );
}
