# Firebase Setup

This guide explains how to set up Firebase for the Adaptive Learning Backend.

## Prerequisites

- Firebase account (create one at [Firebase Console](https://console.firebase.google.com/))
- Firebase project with Firestore database enabled

## Getting Firebase Credentials

1. Go to your Firebase project in the [Firebase Console](https://console.firebase.google.com/)
2. Navigate to Project Settings > Service Accounts
3. Click "Generate new private key"
4. Save the JSON file as `firebase-credentials.json`

## Configuration

1. Place the `firebase-credentials.json` file in the `firebase/credentials/` directory
2. Update your `.env` file with the following variables:
   ```
   FIREBASE_CREDENTIALS_PATH=firebase/credentials/firebase-credentials.json
   FIREBASE_PROJECT_ID=your-project-id
   USE_IN_MEMORY=false  # Set to 'true' for development without Firebase
   ```

## Testing the Connection

To test your Firebase connection:

```bash
python -c "from firebase import firebase_manager; print(f'Connected to Firebase: {firebase_manager.db is not None}')"
```

## Data Structure

The application uses the following Firestore collections:

- `questions`: Assessment questions with skills and difficulties
- `users`: User profiles and authentication data
- `assessments`: Assessment session data
- `learning_paths`: Generated learning paths for users
- `user_skills`: User's skill mastery levels

## Uploading Sample Data

To upload sample data to your Firestore database:

```bash
python -m firebase.upload_data --data-dir data
```

## Local Development

For development without Firebase, set `USE_IN_MEMORY=true` in your `.env` file. The application will use the in-memory database with sample questions from `sample_questions.json`.