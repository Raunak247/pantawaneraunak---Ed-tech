from typing import Optional, Dict, List, Any
import logging
import json
import os
import sys
import firebase_admin
from firebase_admin import firestore, credentials

# Add parent directory to path for importing Firebase module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

# Import our Firebase manager
try:
    from firebase import firebase_manager
except ImportError:
    # If Firebase module is not found, we'll use direct initialization
    pass

from src.config import settings

logger = logging.getLogger(__name__)


class InMemoryDatabase:
    def __init__(self):
        self.collections: Dict[str, List[Dict[str, Any]]] = {
            "questions": [],
            "sessions": [],
            "attempts": [],
            "user_skills": []
        }
        self.id_counters: Dict[str, int] = {
            "questions": 1,
            "sessions": 1,
            "attempts": 1,
            "user_skills": 1
        }
        self._load_fallback_questions()
    
    def _load_fallback_questions(self):
        """Load fallback questions from sample_questions.json if available"""
        try:
            # First look in the workspace root directory
            sample_paths = [
                settings.fallback_questions_path,
                'sample_questions.json',
                '../sample_questions.json',  # Try one directory up
                os.path.join(os.path.dirname(__file__), '../../sample_questions.json')  # From src dir
            ]
            
            for path in sample_paths:
                if path and os.path.exists(path):
                    with open(path, 'r') as f:
                        questions_data = json.load(f)
                        questions_list = []
                        
                        # Convert dict to list with IDs
                        for q_id, q_data in questions_data.items():
                            # Make sure each question has an ID field
                            if "id" not in q_data:
                                q_data["id"] = q_id
                            questions_list.append(q_data)
                        
                        self.collections["questions"] = questions_list
                        logger.info(f"Loaded {len(questions_list)} fallback questions from {path}")
                        return
                        
        except Exception as e:
            logger.warning(f"Failed to load fallback questions: {e}")
            # Continue with empty questions collection
    
    def get_collection(self, name: str):
        if name not in self.collections:
            self.collections[name] = []
            self.id_counters[name] = 1
        return InMemoryCollection(name, self.collections, self.id_counters)


class InMemoryCollection:
    def __init__(self, name: str, collections: Dict, id_counters: Dict):
        self.name = name
        self.collections = collections
        self.id_counters = id_counters
    
    async def insert_one(self, document: Dict[str, Any]):
        if "_id" not in document:
            document["_id"] = str(self.id_counters[self.name])
            self.id_counters[self.name] += 1
        self.collections[self.name].append(document.copy())
        return type('InsertResult', (), {'inserted_id': document["_id"]})()
    
    async def insert_many(self, documents: List[Dict[str, Any]]):
        inserted_ids = []
        for doc in documents:
            if "_id" not in doc:
                doc["_id"] = str(self.id_counters[self.name])
                self.id_counters[self.name] += 1
            self.collections[self.name].append(doc.copy())
            inserted_ids.append(doc["_id"])
        return type('InsertManyResult', (), {'inserted_ids': inserted_ids})()
    
    async def find_one(self, filter_dict: Dict[str, Any]):
        for doc in self.collections[self.name]:
            if self._match_filter(doc, filter_dict):
                return doc.copy()
        return None
    
    def find(self, filter_dict: Optional[Dict[str, Any]] = None):
        filter_dict = filter_dict or {}
        return InMemoryCursor(self.collections[self.name], filter_dict)
    
    async def update_one(self, filter_dict: Dict[str, Any], update: Dict[str, Any]):
        for i, doc in enumerate(self.collections[self.name]):
            if self._match_filter(doc, filter_dict):
                if "$set" in update:
                    doc.update(update["$set"])
                if "$inc" in update:
                    for key, value in update["$inc"].items():
                        doc[key] = doc.get(key, 0) + value
                return type('UpdateResult', (), {'modified_count': 1})()
        return type('UpdateResult', (), {'modified_count': 0})()
    
    async def delete_many(self, filter_dict: Dict[str, Any]):
        original_count = len(self.collections[self.name])
        self.collections[self.name] = [
            doc for doc in self.collections[self.name]
            if not self._match_filter(doc, filter_dict)
        ]
        deleted_count = original_count - len(self.collections[self.name])
        return type('DeleteResult', (), {'deleted_count': deleted_count})()
    
    async def count_documents(self, filter_dict: Dict[str, Any]):
        count = sum(1 for doc in self.collections[self.name] if self._match_filter(doc, filter_dict))
        return count
    
    def _match_filter(self, doc: Dict[str, Any], filter_dict: Dict[str, Any]) -> bool:
        if not filter_dict:
            return True
        for key, value in filter_dict.items():
            if key not in doc or doc[key] != value:
                return False
        return True


class InMemoryCursor:
    def __init__(self, data: List[Dict[str, Any]], filter_dict: Dict[str, Any]):
        self.data = [doc.copy() for doc in data if self._match_filter(doc, filter_dict)]
        self.index = 0
    
    def _match_filter(self, doc: Dict[str, Any], filter_dict: Dict[str, Any]) -> bool:
        if not filter_dict:
            return True
        for key, value in filter_dict.items():
            if key not in doc or doc[key] != value:
                return False
        return True
    
    async def to_list(self, length: Optional[int] = None):
        if length is None:
            return self.data
        return self.data[:length]
    
    def sort(self, key: str, direction: int = 1):
        reverse = direction == -1
        self.data.sort(key=lambda x: x.get(key, ""), reverse=reverse)
        return self


class FirebaseCollection:
    def __init__(self, collection_ref):
        self.collection_ref = collection_ref
    
    async def insert_one(self, document: Dict[str, Any]):
        if "_id" in document:
            doc_id = document.pop("_id")
            doc_ref = self.collection_ref.document(doc_id)
        else:
            doc_ref = self.collection_ref.document()
            doc_id = doc_ref.id
        
        await doc_ref.set(document)
        return type('InsertResult', (), {'inserted_id': doc_id})()
    
    async def insert_many(self, documents: List[Dict[str, Any]]):
        batch = self.collection_ref.firestore.batch()
        inserted_ids = []
        
        for doc in documents:
            if "_id" in doc:
                doc_id = doc.pop("_id")
                doc_ref = self.collection_ref.document(doc_id)
            else:
                doc_ref = self.collection_ref.document()
                doc_id = doc_ref.id
                
            batch.set(doc_ref, doc)
            inserted_ids.append(doc_id)
        
        await batch.commit()
        return type('InsertManyResult', (), {'inserted_ids': inserted_ids})()
    
    async def find_one(self, filter_dict: Dict[str, Any]):
        query = self.collection_ref
        for key, value in filter_dict.items():
            query = query.where(key, "==", value)
        
        docs = await query.limit(1).get()
        for doc in docs:
            result = doc.to_dict()
            result["_id"] = doc.id
            return result
        
        return None
    
    def find(self, filter_dict: Optional[Dict[str, Any]] = None):
        filter_dict = filter_dict or {}
        query = self.collection_ref
        
        for key, value in filter_dict.items():
            query = query.where(key, "==", value)
            
        return FirebaseCursor(query)
    
    async def update_one(self, filter_dict: Dict[str, Any], update: Dict[str, Any]):
        # First, find the document to update
        query = self.collection_ref
        for key, value in filter_dict.items():
            query = query.where(key, "==", value)
            
        docs = await query.limit(1).get()
        modified_count = 0
        
        for doc in docs:
            update_data = {}
            
            if "$set" in update:
                update_data.update(update["$set"])
                
            if "$inc" in update:
                current_data = doc.to_dict()
                for key, value in update["$inc"].items():
                    update_data[key] = current_data.get(key, 0) + value
            
            await doc.reference.update(update_data)
            modified_count = 1
            break
            
        return type('UpdateResult', (), {'modified_count': modified_count})()
    
    async def delete_many(self, filter_dict: Dict[str, Any]):
        query = self.collection_ref
        for key, value in filter_dict.items():
            query = query.where(key, "==", value)
            
        docs = await query.get()
        batch = self.collection_ref.firestore.batch()
        deleted_count = 0
        
        for doc in docs:
            batch.delete(doc.reference)
            deleted_count += 1
            
        await batch.commit()
        return type('DeleteResult', (), {'deleted_count': deleted_count})()
    
    async def count_documents(self, filter_dict: Dict[str, Any]):
        query = self.collection_ref
        for key, value in filter_dict.items():
            query = query.where(key, "==", value)
            
        docs = await query.get()
        return len(docs)


class FirebaseCursor:
    def __init__(self, query):
        self.query = query
        self.sort_field = None
        self.sort_direction = None
        
    def sort(self, key: str, direction: int = 1):
        direction_str = "ASCENDING" if direction == 1 else "DESCENDING"
        self.query = self.query.order_by(key, direction=direction_str)
        return self
        
    async def to_list(self, length: Optional[int] = None):
        if length is not None:
            self.query = self.query.limit(length)
            
        docs = await self.query.get()
        result = []
        
        for doc in docs:
            data = doc.to_dict()
            data["_id"] = doc.id
            result.append(data)
            
        return result


class DatabaseManager:
    def __init__(self):
        self.client = None
        self.db = None
        self.in_memory_db = InMemoryDatabase()
        self.use_in_memory = settings.use_in_memory
        self.firebase_app = None
        
    async def connect(self):
        if settings.firebase_credentials_path and not self.use_in_memory:
            try:
                # Use Firebase manager if available, otherwise initialize directly
                try:
                    # Use our Firebase manager module if available
                    self.firebase_app = firebase_manager.app
                    self.db = firebase_manager.db
                    logger.info("Using Firebase manager for Firestore connection")
                except (NameError, AttributeError):
                    # Fallback to direct initialization if Firebase manager is not available
                    if not self.firebase_app and not firebase_admin._apps:
                        cred_path = settings.firebase_credentials_path
                        if os.path.exists(cred_path):
                            cred = credentials.Certificate(cred_path)
                            self.firebase_app = firebase_admin.initialize_app(cred, {
                                'projectId': settings.firebase_project_id
                            })
                        else:
                            raise FileNotFoundError(f"Firebase credentials file not found: {cred_path}")
                    elif firebase_admin._apps:
                        self.firebase_app = firebase_admin.get_app()
                    
                    # Get Firestore client
                    self.db = firestore.client()
                
                self.use_in_memory = False
                logger.info("Successfully connected to Firebase Firestore")
                
                # Check if questions collection exists and has data
                try:
                    questions_ref = self.db.collection('questions')
                    questions = await FirebaseCollection(questions_ref).find().to_list()
                    if len(questions) == 0:
                        logger.warning("Firebase questions collection is empty. Loading fallback questions...")
                        await self._load_fallback_questions_to_firebase()
                except Exception as e:
                    logger.warning(f"Error checking questions collection: {e}")
            except Exception as e:
                logger.warning(f"Failed to connect to Firebase: {e}. Using in-memory storage with fallback questions.")
                self.use_in_memory = True
        else:
            logger.info("Firebase credentials not provided. Using in-memory storage with fallback questions.")
            self.use_in_memory = True
    
    async def close(self):
        if self.firebase_app:
            firebase_admin.delete_app(self.firebase_app)
    
    def get_collection(self, name: str):
        if self.use_in_memory:
            return self.in_memory_db.get_collection(name)
        if self.db is not None:
            return FirebaseCollection(self.db.collection(name))
        return self.in_memory_db.get_collection(name)
    
    async def _load_fallback_questions_to_firebase(self):
        """Load fallback questions from sample_questions.json to Firebase if Firebase is empty"""
        try:
            sample_paths = [
                settings.fallback_questions_path,
                'sample_questions.json',
                '../sample_questions.json',  # Try one directory up
                os.path.join(os.path.dirname(__file__), '../../sample_questions.json')  # From src dir
            ]
            
            for path in sample_paths:
                if path and os.path.exists(path):
                    with open(path, 'r') as f:
                        questions_data = json.load(f)
                        questions_list = []
                        
                        # Convert dict to list with IDs
                        for q_id, q_data in questions_data.items():
                            # Make sure each question has an ID field
                            if "id" not in q_data:
                                q_data["id"] = q_id
                            questions_list.append(q_data)
                        
                        # Batch upload to Firebase
                        if questions_list and self.db:
                            questions_ref = self.db.collection('questions')
                            batch = self.db.batch()
                            count = 0
                            
                            for question in questions_list:
                                doc_ref = questions_ref.document(question["id"])
                                batch.set(doc_ref, question)
                                count += 1
                                
                                # Commit every 500 documents (Firestore batch limit)
                                if count % 500 == 0:
                                    await batch.commit()
                                    batch = self.db.batch()
                            
                            # Commit any remaining documents
                            if count % 500 != 0:
                                await batch.commit()
                                
                            logger.info(f"Uploaded {count} fallback questions to Firebase from {path}")
                            return
        except Exception as e:
            logger.warning(f"Failed to load fallback questions to Firebase: {e}")
    
    def is_using_memory(self) -> bool:
        return self.use_in_memory


db_manager = DatabaseManager()
