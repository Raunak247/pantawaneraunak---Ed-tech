"""
This file contains helper functions for common Firestore operations
"""

from google.cloud.firestore_v1.base_query import FieldFilter
from firebase_admin import firestore
from . import firebase_manager

def get_collection(collection_name):
    """Get a reference to a Firestore collection"""
    return firebase_manager.db.collection(collection_name)

def query_by_field(collection_name, field, value, operator="=="):
    """
    Query documents in a collection by a field
    
    Args:
        collection_name (str): Name of the collection
        field (str): Field to query on
        value: Value to compare with
        operator (str): Comparison operator (==, >, <, >=, <=, !=, in, not-in, array-contains, array-contains-any)
    
    Returns:
        Query: Firestore query object
    """
    collection = get_collection(collection_name)
    return collection.where(filter=FieldFilter(field, operator, value))

def get_document(collection_name, document_id):
    """Get a document by ID"""
    return get_collection(collection_name).document(document_id).get()

def create_document(collection_name, document_data, document_id=None):
    """Create a new document in a collection"""
    collection = get_collection(collection_name)
    
    if document_id:
        return collection.document(document_id).set(document_data)
    else:
        return collection.add(document_data)

def update_document(collection_name, document_id, update_data):
    """Update a document by ID"""
    return get_collection(collection_name).document(document_id).update(update_data)

def delete_document(collection_name, document_id):
    """Delete a document by ID"""
    return get_collection(collection_name).document(document_id).delete()

def batch_write(operations):
    """
    Perform a batch write operation
    
    Args:
        operations (list): List of tuples in the format (operation_type, collection, doc_id, data)
            operation_type can be 'set', 'update', or 'delete'
    """
    batch = firebase_manager.db.batch()
    
    for op in operations:
        operation_type, collection_name, doc_id, data = op
        doc_ref = get_collection(collection_name).document(doc_id)
        
        if operation_type == 'set':
            batch.set(doc_ref, data)
        elif operation_type == 'update':
            batch.update(doc_ref, data)
        elif operation_type == 'delete':
            batch.delete(doc_ref)
    
    return batch.commit()

def transaction_example(callback_function):
    """
    Execute a function within a Firestore transaction
    
    Args:
        callback_function (callable): Function that takes a transaction object and performs operations
    """
    return firebase_manager.db.transaction(callback_function)