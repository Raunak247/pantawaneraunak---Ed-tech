"""
Firestore data upload utility

This script can be used to populate the Firestore database with initial data.
"""

import json
import argparse
import os
from pathlib import Path
from firebase_admin import firestore
from dotenv import load_dotenv

# Import firebase manager
from . import firebase_manager

def load_json_data(file_path):
    """Load data from a JSON file"""
    with open(file_path, 'r') as f:
        return json.load(f)

def upload_collection(db, collection_name, data):
    """Upload data to a Firestore collection"""
    collection_ref = db.collection(collection_name)
    batch = db.batch()
    count = 0
    
    for doc_id, doc_data in data.items():
        doc_ref = collection_ref.document(doc_id)
        batch.set(doc_ref, doc_data)
        count += 1
        
        # Firestore batches can contain up to 500 operations
        if count >= 500:
            batch.commit()
            batch = db.batch()
            count = 0
    
    if count > 0:
        batch.commit()
    
    return len(data)

def main():
    """Main function to upload data to Firestore"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Upload data to Firestore')
    parser.add_argument('--data-dir', type=str, default='data',
                        help='Directory containing JSON files to upload')
    parser.add_argument('--use-emulator', action='store_true',
                        help='Use Firestore emulator instead of production')
    args = parser.parse_args()
    
    # Initialize Firebase with emulator if specified
    db = firebase_manager.initialize(use_emulator=args.use_emulator)
    
    # Get all JSON files in the data directory
    data_dir = Path(args.data_dir)
    json_files = list(data_dir.glob('*.json'))
    
    if not json_files:
        print(f"No JSON files found in {data_dir}")
        return
    
    # Upload each file to a collection named after the file
    total_docs = 0
    for json_file in json_files:
        collection_name = json_file.stem
        data = load_json_data(json_file)
        doc_count = upload_collection(db, collection_name, data)
        total_docs += doc_count
        print(f"Uploaded {doc_count} documents to collection '{collection_name}'")
    
    print(f"Total: {total_docs} documents uploaded to {len(json_files)} collections")

if __name__ == "__main__":
    # Load environment variables
    load_dotenv()
    main()