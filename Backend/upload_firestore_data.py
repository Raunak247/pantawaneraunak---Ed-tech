import os
import json
import uuid
import firebase_admin
from firebase_admin import credentials, firestore
from dotenv import load_dotenv
import argparse
from pathlib import Path
import time
from datetime import datetime

def load_firebase_credentials():
    """Load Firebase credentials from .env file"""
    load_dotenv()
    
    creds_path = os.environ.get("FIREBASE_CREDENTIALS_PATH")
    project_id = os.environ.get("FIREBASE_PROJECT_ID")
    
    if not creds_path or not os.path.exists(creds_path):
        print(f"Error: Firebase credentials not found at {creds_path}")
        print("Make sure you have set up your Firebase credentials properly.")
        return None, None
    
    if not project_id:
        print("Error: FIREBASE_PROJECT_ID not set in .env file")
        return None, None
        
    return creds_path, project_id

def initialize_firebase():
    """Initialize Firebase Admin SDK"""
    creds_path, project_id = load_firebase_credentials()
    
    if not creds_path or not project_id:
        return None
        
    try:
        # Initialize Firebase app
        cred = credentials.Certificate(creds_path)
        firebase_app = firebase_admin.initialize_app(cred, {
            'projectId': project_id
        })
        
        # Get Firestore client
        db = firestore.client()
        
        print(f"✅ Connected to Firebase Firestore project: {project_id}")
        return db
    except Exception as e:
        print(f"Error initializing Firebase: {e}")
        return None

def generate_sample_questions():
    """Generate sample questions for the adaptive learning system"""
    python_questions = [
        {
            "id": str(uuid.uuid4()),
            "text": "What is the output of print(2 + 2)?",
            "options": ["2", "4", "22", "Error"],
            "correct_answer": "4",
            "skill": "basic_python",
            "subject": "python",
            "difficulty": 1
        },
        {
            "id": str(uuid.uuid4()),
            "text": "Which of the following is a mutable data type in Python?",
            "options": ["string", "tuple", "list", "int"],
            "correct_answer": "list",
            "skill": "data_types",
            "subject": "python",
            "difficulty": 2
        },
        {
            "id": str(uuid.uuid4()),
            "text": "What does the 'len()' function do in Python?",
            "options": ["Returns the largest item in an iterable", 
                        "Returns the length of an object", 
                        "Returns a list of enumerated items", 
                        "Returns the smallest item in an iterable"],
            "correct_answer": "Returns the length of an object",
            "skill": "basic_python",
            "subject": "python",
            "difficulty": 1
        },
        {
            "id": str(uuid.uuid4()),
            "text": "How do you create a list in Python?",
            "options": ["list = (1, 2, 3)", "list = {1, 2, 3}", "list = [1, 2, 3]", "list = <1, 2, 3>"],
            "correct_answer": "list = [1, 2, 3]",
            "skill": "data_types",
            "subject": "python",
            "difficulty": 1
        },
        {
            "id": str(uuid.uuid4()),
            "text": "What is the correct way to define a function in Python?",
            "options": ["function myFunc():", "def myFunc[]:", "def myFunc():", "func myFunc():"],
            "correct_answer": "def myFunc():",
            "skill": "functions",
            "subject": "python",
            "difficulty": 2
        }
    ]
    
    math_questions = [
        {
            "id": str(uuid.uuid4()),
            "text": "What is the result of 5 + 7?",
            "options": ["10", "12", "57", "35"],
            "correct_answer": "12",
            "skill": "addition",
            "subject": "math",
            "difficulty": 1
        },
        {
            "id": str(uuid.uuid4()),
            "text": "What is 8 × 9?",
            "options": ["56", "63", "72", "81"],
            "correct_answer": "72",
            "skill": "multiplication",
            "subject": "math",
            "difficulty": 2
        },
        {
            "id": str(uuid.uuid4()),
            "text": "Solve for x: 3x + 5 = 20",
            "options": ["3", "5", "15", "45"],
            "correct_answer": "5",
            "skill": "algebra",
            "subject": "math",
            "difficulty": 3
        },
        {
            "id": str(uuid.uuid4()),
            "text": "What is the area of a rectangle with length 6 and width 4?",
            "options": ["10", "24", "20", "30"],
            "correct_answer": "24",
            "skill": "geometry",
            "subject": "math",
            "difficulty": 2
        },
        {
            "id": str(uuid.uuid4()),
            "text": "What is the square root of 81?",
            "options": ["8", "9", "18", "27"],
            "correct_answer": "9",
            "skill": "arithmetic",
            "subject": "math",
            "difficulty": 2
        }
    ]
    
    return python_questions + math_questions

def generate_sample_skills():
    """Generate sample skills data"""
    return {
        "basic_python": {
            "name": "Basic Python",
            "description": "Fundamental Python concepts like syntax and simple operations",
            "subject": "python",
            "prerequisites": []
        },
        "data_types": {
            "name": "Python Data Types",
            "description": "Understanding of Python's data types and their properties",
            "subject": "python",
            "prerequisites": ["basic_python"]
        },
        "functions": {
            "name": "Python Functions",
            "description": "Defining and working with functions in Python",
            "subject": "python",
            "prerequisites": ["basic_python"]
        },
        "addition": {
            "name": "Addition",
            "description": "Adding numbers together",
            "subject": "math",
            "prerequisites": []
        },
        "multiplication": {
            "name": "Multiplication",
            "description": "Multiplying numbers together",
            "subject": "math",
            "prerequisites": ["addition"]
        },
        "arithmetic": {
            "name": "Arithmetic Operations",
            "description": "Basic operations like addition, subtraction, multiplication, division",
            "subject": "math",
            "prerequisites": []
        },
        "algebra": {
            "name": "Basic Algebra",
            "description": "Solving simple equations with variables",
            "subject": "math",
            "prerequisites": ["arithmetic"]
        },
        "geometry": {
            "name": "Basic Geometry",
            "description": "Calculating areas and perimeters of shapes",
            "subject": "math",
            "prerequisites": ["arithmetic"]
        }
    }

def upload_data_to_firestore(db, collection_name, data, batch_size=500):
    """
    Upload data to Firestore collection
    
    Args:
        db: Firestore client
        collection_name: Name of the collection to add data to
        data: List of dictionaries or dictionary of dictionaries to add
        batch_size: Maximum batch size (Firestore allows max 500 operations per batch)
    """
    print(f"\nUploading {len(data)} items to '{collection_name}' collection...")
    
    # Create a batch
    batch = db.batch()
    count = 0
    total_uploaded = 0
    
    # Handle both list of items and dictionary of items
    items = data.items() if isinstance(data, dict) else enumerate(data)
    
    for key, item in items:
        # For dictionaries, use the key as document ID
        # For lists, use the item's ID if available, otherwise create one
        if isinstance(data, dict):
            doc_ref = db.collection(collection_name).document(key)
        else:
            doc_id = item.get('id', str(uuid.uuid4()))
            doc_ref = db.collection(collection_name).document(doc_id)
            
        # Add timestamp
        if isinstance(item, dict):
            item['created_at'] = firestore.SERVER_TIMESTAMP
            
        # Add to batch
        batch.set(doc_ref, item)
        count += 1
        total_uploaded += 1
        
        # If we've reached batch_size, commit the batch and create a new one
        if count >= batch_size:
            batch.commit()
            print(f"  Uploaded {total_uploaded} items so far...")
            batch = db.batch()
            count = 0
            time.sleep(1)  # Short pause to prevent rate limiting
    
    # Commit any remaining items
    if count > 0:
        batch.commit()
    
    print(f"✅ Successfully uploaded {total_uploaded} items to '{collection_name}'")

def load_json_data(file_path):
    """Load data from a JSON file"""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading JSON file {file_path}: {e}")
        return None

def clear_collection(db, collection_name):
    """Delete all documents in a collection"""
    print(f"\nClearing '{collection_name}' collection...")
    
    try:
        docs = db.collection(collection_name).limit(500).stream()
        deleted = 0
        
        for doc in docs:
            doc.reference.delete()
            deleted += 1
            
        print(f"✅ Deleted {deleted} documents from '{collection_name}'")
    except Exception as e:
        print(f"Error clearing collection: {e}")

def import_from_sql(connection_string, query, collection_name, id_column=None):
    """
    Import data from an SQL database to Firestore
    
    Args:
        connection_string: SQL connection string
        query: SQL query to get the data
        collection_name: Firestore collection to upload to
        id_column: Column to use as document ID (optional)
    """
    try:
        import sqlalchemy
        from sqlalchemy import create_engine, text
    except ImportError:
        print("Error: SQLAlchemy is not installed. Please install it with:")
        print("pip install sqlalchemy pymysql psycopg2-binary")
        return None
        
    print(f"\nImporting data from SQL database to '{collection_name}' collection...")
    
    try:
        # Create engine and connect to database
        engine = create_engine(connection_string)
        with engine.connect() as conn:
            result = conn.execute(text(query))
            columns = result.keys()
            
            # Convert result to list of dictionaries
            records = []
            for row in result:
                record = {}
                for i, column in enumerate(columns):
                    record[column] = row[i]
                    
                # Use specified column as ID if provided
                if id_column and id_column in record:
                    record['id'] = str(record[id_column])
                    
                records.append(record)
                
            print(f"✅ Successfully retrieved {len(records)} records from the database")
            return records
    except Exception as e:
        print(f"Error importing from SQL: {e}")
        return None

def import_from_mongodb(connection_string, database, collection, filter_query=None):
    """
    Import data from MongoDB to Firestore
    
    Args:
        connection_string: MongoDB connection string
        database: MongoDB database name
        collection: MongoDB collection name
        filter_query: MongoDB filter query (optional)
    """
    try:
        from pymongo import MongoClient
    except ImportError:
        print("Error: pymongo is not installed. Please install it with:")
        print("pip install pymongo")
        return None
        
    print(f"\nImporting data from MongoDB '{database}.{collection}' to Firestore...")
    
    try:
        # Connect to MongoDB
        client = MongoClient(connection_string)
        db = client[database]
        coll = db[collection]
        
        # Get the documents
        filter_query = filter_query or {}
        documents = list(coll.find(filter_query))
        
        # Convert ObjectId to string for each document
        for doc in documents:
            if '_id' in doc:
                doc['id'] = str(doc['_id'])
                del doc['_id']
        
        print(f"✅ Successfully retrieved {len(documents)} documents from MongoDB")
        return documents
    except Exception as e:
        print(f"Error importing from MongoDB: {e}")
        return None

def main():
    parser = argparse.ArgumentParser(description="Upload data to Firebase Firestore")
    parser.add_argument("--clear", action="store_true", help="Clear collections before uploading")
    parser.add_argument("--json", type=str, help="Path to JSON file with data to upload")
    parser.add_argument("--collection", type=str, help="Collection name to upload data to")
    
    # Add SQL import arguments
    parser.add_argument("--sql", action="store_true", help="Import from SQL database")
    parser.add_argument("--conn", type=str, help="SQL connection string")
    parser.add_argument("--query", type=str, help="SQL query to get data")
    parser.add_argument("--id-column", type=str, help="SQL column to use as document ID")
    
    # Add MongoDB import arguments
    parser.add_argument("--mongo", action="store_true", help="Import from MongoDB")
    parser.add_argument("--mongo-conn", type=str, help="MongoDB connection string")
    parser.add_argument("--mongo-db", type=str, help="MongoDB database name")
    parser.add_argument("--mongo-coll", type=str, help="MongoDB collection name")
    
    args = parser.parse_args()
    
    # Initialize Firebase
    db = initialize_firebase()
    if not db:
        print("Exiting due to Firebase initialization error")
        return
    
    # Determine the collection name
    collection_name = args.collection if args.collection else "questions"
    
    # Handle SQL import
    if args.sql and args.conn and args.query:
        data = import_from_sql(args.conn, args.query, collection_name, args.id_column)
        if data:
            if args.clear:
                clear_collection(db, collection_name)
            upload_data_to_firestore(db, collection_name, data)
        return
    
    # Handle MongoDB import
    if args.mongo and args.mongo_conn and args.mongo_db and args.mongo_coll:
        data = import_from_mongodb(args.mongo_conn, args.mongo_db, args.mongo_coll)
        if data:
            if args.clear:
                clear_collection(db, collection_name)
            upload_data_to_firestore(db, collection_name, data)
        return
    
    # Handle JSON import
    if args.json:
        data = load_json_data(args.json)
        if data:
            if args.clear:
                clear_collection(db, collection_name)
            upload_data_to_firestore(db, collection_name, data)
        return
    
    # Otherwise, upload sample data
    print("\nPreparing to upload sample data to Firebase Firestore...")
    
    # Generate sample data
    questions = generate_sample_questions()
    skills = generate_sample_skills()
    
    # Clear collections if requested
    if args.clear:
        clear_collection(db, "questions")
        clear_collection(db, "skills")
    
    # Upload data
    upload_data_to_firestore(db, "questions", questions)
    upload_data_to_firestore(db, "skills", skills)
    
    print("\n✅ Data upload complete!")
    print("\nYour Firebase Firestore database now contains:")
    print(f"  - {len(questions)} questions")
    print(f"  - {len(skills)} skills")
    print("\nYou can now run your adaptive learning application!")

if __name__ == "__main__":
    main()