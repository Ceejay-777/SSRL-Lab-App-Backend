from models import Todos
from datetime import datetime
from pymongo import DESCENDING
from bson.objectid import ObjectId 

class Todosdb:
    def __init__(self) -> None:
        self.collection = Todos
        
    def create_todo(self, dtls):
        print("Okay")
        return self.collection.insert_one(dtls.__dict__).inserted_id
    
    def add_todo(self, uid, todo):
        now = datetime.now().isoformat()
        modified = self.collection.update_one({"uid":uid}, {"$push": {"todo": {"todo": todo, "id": now, "completed": False}}}).modified_count>0 
        return [modified, now]
    
    def change_status(self, uid, todo_id, status):
        return self.collection.update_one({"uid": uid, "todo.id": todo_id}, {"$set": {"todo.$.completed": status}}).modified_count>0
    
    def edit_todo(self, uid, todo_id, todo):
        return self.collection.update_one({"uid": uid, "todo.id": todo_id}, {"$set": {"todo.$.todo": todo}}).modified_count>0

    def delete_todo(self, uid, todo_id):
        return self.collection.update_one({"uid":uid}, {"$pull": {"todo" : {"id": todo_id}}}).modified_count>0

    def get_todo_by_user_id(self, user_id):
        return self.collection.find_one({"uid":user_id})
    
class Todo:
    def __init__(self, uid, todo=None, created_at=None):
        self.uid = uid
        self.todo = todo or []
        self.created_at = created_at or datetime.now()