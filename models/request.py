from bson.objectid import ObjectId 
from models import Requests
from datetime import datetime, timedelta
from pymongo import DESCENDING

class Requestdb:
    def __init__(self) -> None:
        self.collection = Requests
    
    def create_request(self, request):
        return self.collection.insert_one(request.__dict__).inserted_id
    
    def get_all(self):
        return self.collection.find().sort("created_at", DESCENDING)
    
    def get_by_request_id(self, request_id):
        return self.collection.find_one({"request_id": request_id})

    def get_by_isMember(self, uid):
        return self.collection.find({'$or': [{'sender': uid}, {'receipient': uid}]}).sort("created_at", DESCENDING)
        
    def get_by_isMember_limited(self, uid):
        return self.collection.find({'$or': [{'sender': uid}, {'receipient': uid}]}).sort("created_at", DESCENDING).limit(3)
    
    def get_by_sender(self, uid): # Remove
        return self.collection.find({"sender":uid}).sort("created_at", DESCENDING)
    
    def get_by_sender_limited(self, uid): # Remove
        return self.collection.find({"sender":uid}).sort("created_at", DESCENDING).limit(3)
    
    def get_by_reciepient(self, uid): # Remove
        return self.collection.find({"receipient":uid}).sort("created_at", DESCENDING)
    
    def get_by_receipient_limited(self, uid): # Remove
        return self.collection.find({"receipient":uid}).sort("created_at", DESCENDING).limit(3)
    
    def update_request_dtls(self, request_id, details):
        return self.collection.update_one({"request_id": request_id},{"$set": details}).modified_count>0
    
    def delete_request(self, request_id):
        return self.collection.updated_one({"request_id": request_id}, {"$set": {"deleted_at": datetime.now()}}).modified_count>0

class Request:
    def __init__(self, request_id, title, type, sender, receipient, purpose, request_details, created_at=None, status=None) -> None:
        self.request_id = request_id
        self.title = title
        self.type = type
        self.sender = sender
        self.receipient = receipient
        self.status = status or "pending"
        self.created_at = created_at or datetime.now()
        self.request_details = request_details
        self.purpose = purpose