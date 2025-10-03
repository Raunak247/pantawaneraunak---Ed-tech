import os
from dotenv import load_dotenv

# Load the .env file
load_dotenv()

# Print environment variables
print(f"USE_IN_MEMORY: {os.getenv('USE_IN_MEMORY')}")
print(f"FIREBASE_CREDENTIALS_PATH: {os.getenv('FIREBASE_CREDENTIALS_PATH')}")
print(f"FIREBASE_PROJECT_ID: {os.getenv('FIREBASE_PROJECT_ID')}")