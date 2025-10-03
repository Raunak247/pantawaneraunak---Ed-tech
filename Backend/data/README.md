# Data Directory

This directory contains data files for initializing the database.

## Usage

Place JSON files here for uploading to Firestore using:

```bash
python -m firebase.upload_data --data-dir data
```

## Sample Files

- `questions.json`: Sample assessment questions
- `users.json`: Sample user data
- `subjects.json`: Subject definitions

## Creating Data Files

Each file should be named after the collection it represents and contain JSON objects with document IDs as keys.