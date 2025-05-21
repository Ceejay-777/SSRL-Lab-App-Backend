from models import Reports
from datetime import datetime
from pymongo import DESCENDING

class Reportdb:
    def __init__(self) -> None:
        self.collection = Reports
    
    def create_report(self, request):
        return self.collection.insert_one(request.__dict__).inserted_id 
    
    def get_all(self):
        return self.collection.find({'deleted_at': {'$exists': False}}).sort("created_at", DESCENDING)
    
    def get_all_limited(self):
        return self.collection.find({'deleted_at': {'$exists': False}}).sort("created_at", DESCENDING).limit(3)
    
    def get_by_stack(self, stack):
        return self.collection.find({"stack": stack, 'deleted_at': {'$exists': False}}).sort("created_at", DESCENDING)
    
    def get_by_isMember(self, uid):
        return self.collection.find({'$or': [
               {'sender.id': uid},
               {'receiver': uid}
           ], 'deleted_at': {'$exists': False}}).sort("created_at", DESCENDING)
        
    def get_by_isMember_limited(self, uid):
        return self.collection.find({'$or': [
               {'sender.id': uid},
               {'receiver': uid}
           ], 'deleted_at': {'$exists': False}}).sort("created_at", DESCENDING).limit(3)
    
    def get_by_report_id(self, report_id):
        return self.collection.find_one({"report_id": report_id, 'deleted_at': {'$exists': False}})

    def update_report_dtls(self,report_id, dtls):
        return self.collection.update_one({"report_id":report_id},{"$set": dtls}).modified_count>0
    
    def give_feedback(self,report_id, dtls):
        return self.collection.update_one({"report_id":report_id},{"$push":{"feedback": dtls}}).modified_count>0
    
    def add_doc(self, report_id, doc):
        return self.collection.update_one({"report_id":report_id},{"$push":{"submissions.docs": doc}}).modified_count>0
    
    def add_link(self, report_id, link):
        return self.collection.update_one({"report_id":report_id},{"$push":{"submissions.links": link}}).modified_count>0
    
class Report:
    def __init__(self, report_id, title, stack, report_type, receiver, sender, report_details, submissions=None, feedback=None, created_at=None):
        self.report_id = report_id
        self.title = title 
        self.stack = stack 
        self.report_type = report_type
        self.submissions = submissions or {"docs": [], "links": []}
        self.feedback = feedback or []
        self.created_at = created_at or datetime.now()
        self.receiver = receiver
        self.sender = sender
        self.report_details = report_details