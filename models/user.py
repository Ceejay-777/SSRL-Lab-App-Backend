from models import Users, User
from datetime import datetime
from bson import ObjectId

class Userdb:
    def __init__(self) -> None:
        self.collection =  Users

    def create_user(self, user):
        return self.collection.insert_one(user.__dict__).inserted_id
        
    def get_user_by_role(self, role):
        return self.collection.find({"role": role, "deleted_at": {'exists': False}})
    
    def get_user_fullname(self, uid):
        user = self.collection.find_one({"uid" : uid})
        return user["fullname"]
    
    def get_user_by_role_one(self, role):
        return self.collection.find_one({"role": role})
    
    def get_user_by_uid(self, user_uid):
        return self.collection.find_one({"uid": user_uid, "deleted_at": {'$exists': False}})
    
    def get_user_by_oid(self, user_id):
        return self.collection.find_one({"_id": ObjectId(user_id)})
    
    def update_dtl(self, user_id, dtls):
        return self.collection.update_one({"uid":user_id},{"$set": dtls}).modified_count>0
    
    def delete_user(self, id, dtls):
        return self.collection.update_one({"uid":id}, {"$set": dtls}).modified_count>0
    
    def get_all_users(self):
        return self.collection.find().sort("uid")
    
    def get_all_users_limited(self):
        return self.collection.find().limit(4)
    
    def get_lead(self, stack):
        return self.collection.find_one({"role":"Lead", "stack":stack})
    
    def get_users_by_stack(self, stack):
        return self.collection.find({"stack":stack}).sort("uid")
    
    def get_users_by_stack_limited(self, stack):
        return self.collection.find({"stack":stack}).limit(4)
    
    def update_user(self, uid, details):
        try:
            result = self.collection.update_one({"uid": uid}, {"$set": details})
            
            if result.matched_count == 0:
                return {"success": False, "error": "No user found with the given UID '{uid}'"}
            if result.modified_count == 0:
                return {"success": False, "error": "No changes were made to the user profile"}
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}
        
class User:
    def __init__(self, firstname, surname, hashed_pwd, uid, stack, niche, role, phone_num, email, mentor_id, avatar, task_id, bio, location, bday, datetime_created, suspended=None, created_at=None) -> None:
        self.firstname = firstname, 
        self.surname = surname
        self.hashed_pwd = hashed_pwd
        self.uid = uid
        self.stack = stack
        self.niche = niche
        self.role = role
        self.phone_num = phone_num
        self.email = email
        self.mentor_id = mentor_id
        self.avatar = avatar
        self.task_id = task_id   
        self.datetime_created = datetime_created
        self.bio = bio
        self.location = location
        self.bday = bday
        self.suspended = suspended
        self.created_at = created_at if created_at else datetime.now()