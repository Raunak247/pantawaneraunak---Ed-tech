"""
Firebase Configuration Module

This module handles Firebase initialization and configuration.
Place your Firebase credentials in the credentials directory and update the path below.

In production, use environment variables instead of file paths for security.
"""

import os
import firebase_admin
from firebase_admin import credentials, firestore
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
load_dotenv()

class FirebaseManager:
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(FirebaseManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._initialized = True
        self._app = None
        self._db = None
        
    def initialize(self, use_emulator=False):
        """Initialize Firebase with credentials"""
        if self._app:
            return
            
        # Check if we're using in-memory mode
        if os.getenv('USE_IN_MEMORY', '').lower() == 'true':
            # In memory mode, don't initialize Firebase
            return None
        
        # Get credential path from environment variables or use default
        cred_path = os.getenv('FIREBASE_CREDENTIALS_PATH', 'firebase/credentials/firebase-credentials.json')
        
        # Check if credentials file exists
        if not Path(cred_path).exists():
            raise FileNotFoundError(f"Firebase credentials file not found at {cred_path}")
        
        # Initialize Firebase app
        cred = credentials.Certificate(cred_path)
        self._app = firebase_admin.initialize_app(cred)
        
        # Initialize Firestore
        self._db = firestore.client()
        
        # Use emulator if specified
        if use_emulator:
            emulator_host = os.getenv('FIRESTORE_EMULATOR_HOST', 'localhost:8080')
            self._db.collection('_').document('_')  # Force client initialization
            os.environ['FIRESTORE_EMULATOR_HOST'] = emulator_host
            
        return self._db
    
    @property
    def db(self):
        """Get Firestore database instance"""
        if os.getenv('USE_IN_MEMORY', '').lower() == 'true':
            return None
        
        if not self._db:
            self.initialize()
        return self._db
    
    @property
    def app(self):
        """Get Firebase app instance"""
        if os.getenv('USE_IN_MEMORY', '').lower() == 'true':
            return None
            
        if not self._app:
            self.initialize()
        return self._app


# Create singleton instance
firebase_manager = FirebaseManager()

# Expose db for easy importing
db = firebase_manager.db