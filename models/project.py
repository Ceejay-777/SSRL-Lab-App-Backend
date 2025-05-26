from models import Projects
from pymongo import DESCENDING
from datetime import datetime
from bson.objectid import ObjectId
class Projectdb:
    def __init__(self) -> None:
        self.collection = Projects
        
    def create_project(self, project):
        return self.collection.insert_one(project.__dict__).inserted_id
        
    def get_all(self):
        return self.collection.find({'deleted_at': {'$exists': False}}).sort("created_at", DESCENDING)
    
    def get_all_projects(self):
        return self.collection.find()
    
    def get_all_limited(self):
        return self.collection.find({'deleted_at': {'$exists': False}}).sort("created_at", DESCENDING).limit(4)
    
    def get_by_isMember_limited(self, uid):
        return self.collection.find({'$or': [
               {'leads.id': uid,},
               {'team_members.id': uid}
           ], 'deleted_at': {'$exists': False}}).sort('created_at', DESCENDING).limit(4)
    
    def get_by_isMember(self, uid):
        return self.collection.find({'$or': [
               {'leads.id': uid},
               {'team_members.id': uid}
           ], 'deleted_at': {'$exists': False}}).sort('created_at', DESCENDING)
    
    def existing_project_name(self, name):
        return self.collection.find_one({"name": name})
        
    def get_by_project_id(self, project_id):
        return self.collection.find_one({"project_id": project_id, 'deleted_at': {'$exists': False}})
    
    def submit_doc(self, project_id, doc):
        return self.collection.update_one({'project_id': project_id}, {'$push': {'submissions.docs': doc}}).modified_count > 0
    
    def submit_link(self, project_id, link):
        return self.collection.update_one({'project_id': project_id}, {'$push': {'submissions.links': link}}).modified_count > 0
    
    def get_by_stack_limited(self, stack):
        return self.collection.find({"stack" : stack}).sort("created_at", DESCENDING).limit(4)
    
    def get_by_stack(self, stack):
        return self.collection.find({"stack" : stack, 'deleted_at': {'$exists': False}}).sort("created_at", DESCENDING)
    
    def update_project_details(self, project_id, details):
        return self.collection.update_one({"project_id": project_id}, {"$set": details}).modified_count>0
    
    def mark_project(self, project_id, status):
        return self.collection.update_one({"project_id":project_id},{"$set":{"status":status}}).modified_count>0
    
    def delete_project(self, project_id):
        return self.collection.update_one({"project_id":project_id}, {"$set":{"deleted_at": datetime.now()}}).modified_count>0
    
    def send_feedback(self, project_id, sender, feedback):
        return self.collection.update_one({"project_id":project_id}, {"$push": {"feedback":{'feedback': feedback, 'sender': sender, 'created_at': datetime.now()}}}).modified_count>0
    
    def update_dtls(self, project_id, dtls):
        return self.collection.update_one({"project_id": project_id},{"$set": dtls}).modified_count>0
    
    def unset_field(self, project_id, field):
        return self.collection.update_one({"project_id": project_id},{"$unset": {field: 1}}).modified_count>0

class Project:
    def __init__(self, project_id, name, description, objectives, leads, team_members, stack, created_by, deadline, created_at=None, status=None, submissions=None) -> None:
        self.project_id = project_id
        self.name = name
        self.description = description
        self.objectives = objectives
        self.team_members = team_members
        self.leads = leads
        self.stack = stack
        self.created_by = created_by
        self.deadline = deadline
        self.status = status if  status else 'uncompleted'
        self.submissions = submissions if submissions else  {"docs": [], "links": []} 
        self.created_at = created_at if created_at else datetime.now()
        