from bson.objectid import ObjectId 
from properties import *
import os
import string, random
from datetime import datetime, timedelta
from models import *
from pymongo import DESCENDING, ASCENDING

class Notificationsdb:
    def __init__(self):
        self.collection = Notifications
        
    def send_notification(self, dtls):
        print("Notification Created")
        return self.collection.insert_one(dtls.__dict__).inserted_id
    
    def get_by_isMember(self, uid):
        return self.collection.find({'receivers' : uid}).sort("sentAt", DESCENDING)
    
    def get_by_isMember_limited(self, uid):
        return self.collection.find({'receivers' : uid}).sort("sentAt", DESCENDING).limit(3)
    
    def mark_as_read(self, note_id):
        return self.collection.update_one({"_id": ObjectId(note_id)}, {"$set": {"status": "read"}}).modified_count>0
    
    def mark_all_as_read(self, uid):
        return self.collection.update_many({'receivers' : uid}, {"$set": {"status": "read"}}).modified_count>0
    
    def get_unread_count(self, uid):
        return self.collection.count_documents({"receivers": uid, "status": "unread"})
    
    def delete_notification(self, note_id):
        return self.collection.delete_one({"_id": ObjectId(note_id)}).deleted_count>0
    
class Todosdb:
    def __init__(self) -> None:
        self.collection = Todos
        
    def create_todo(self, dtls):
        print("Okay")
        return self.collection.insert_one(dtls.__dict__).inserted_id
    
    def add_todo(self, uid, todo):
        now = datetime.now().isoformat()
        modified = self.collection.update_one({"uid":uid},{"$push": {"todo": {"todo": todo, "id": now, "completed": False}}}).modified_count>0 
        return [modified, now]
    
    def change_status(self, uid, todo_id, status):
        return self.collection.update_one({"uid": uid, "todo.id": todo_id}, {"$set": {"todo.$.completed": status}}).modified_count>0
    
    def edit_todo(self, uid, todo_id, todo):
        return self.collection.update_one({"uid": uid, "todo.id": todo_id}, {"$set": {"todo.$.todo": todo}}).modified_count>0

    def delete_todo(self, uid, todo_id):
        return self.collection.update_one({"uid":uid}, {"$pull": {"todo" : {"id": todo_id}}}).modified_count>0

    def get_todo_by_user_id(self, user_id):
        return self.collection.find_one({"uid":user_id})
    
    # def get_todos_by_user_id_limited(self, user_id):
    #     return sorted(self.collection.find_one({"uid":user_id}, {"_id": 0, "todo": 1}).get('todo', []), key=lambda x: x["id"], reverse=True)[0:4]
    
    def get_todos_by_user_id_limited(self, user_id):
        doc = self.collection.find_one({"uid": user_id}, {"_id": 0, "todo": 1})
        
        if not doc or "todo" not in doc:
            return []

        return sorted(
            doc.get("todo", []), 
            key=lambda x: datetime.fromisoformat(x["id"]), 
            reverse=True
        )[:4]
    
class Eqptdb:
    def __init__(self) -> None:
        self.collection = Eqpts
    
    def new_input(self, dtls):
        return self.collection.insert_one(dtls.__dict__).inserted_id
    
    def update_eqpt_dtls(self,eqpt_id, dtls):
        return self.collection.update_one({"_id":ObjectId(eqpt_id)},{"$set":dtls.__dict__}).modified_count>0

    def delete_existing_eqpt(self, eqpt_id):
        return self.collection.delete_one({"_id":ObjectId(eqpt_id)}).deleted_count>0
    
    def get_eqpt_by_id(self, eqpt_id):
        return self.collection.find_one({"_id":ObjectId(eqpt_id)})
    
    def get_eqpt_by_name(self, eqpt_name):
        return self.collection.find_one({'$text':{'$search':eqpt_name}})
    
    def get_all_eqpt(self):
        return self.collection.find().sort("name")
    
    def get_all_available_eqpt(self):
        return self.collection.find({"status":"available"}).sort("name")
    
    
class lost_eqptdb:
    def __init__(self) -> None:
        self.collection = lost_eqpts
        
    def new_input(self, dtls):
        return self.collection.insert_one(dtls.__dict__).inserted_id

    def get_all(self):
        return self.collection.find().sort("date_time")
    
    def get_eqpt_by_id(self, eqpt_id):
        return self.collection.find_one({"_id":ObjectId(eqpt_id)})
    
    def update_eqpt_dtls(self,eqpt_id, dtls):
        return self.collection.update_one({"_id":ObjectId(eqpt_id)},{"$set":dtls.__dict__}).modified_count>0
    
    def delete_lost_eqpt(self, eqpt_id):
        return self.collection.delete_one({"_id":ObjectId(eqpt_id)}).deleted_count>0
    
    
class Requestdb:
    def __init__(self) -> None:
        self.collection = Requests
    
    def insert_new(self, request):
        return self.collection.insert_one(request.__dict__).inserted_id
    
    def get_all(self):
        return self.collection.find().sort("date_time", -1)
    
    # def get_all(self):
    #     return self.collection.find().sort("date_time", -1)
    
    def get_by_request_id(self, _id):
        return self.collection.find_one({"_id":ObjectId(_id)})

    def get_by_isMember(self, uid):
        return self.collection.find({'$or': [
               {'sender': uid},
               {'receipient': uid}
           ]}).sort("date_time", -1)
        
    def get_by_isMember_limited(self, uid):
        return self.collection.find({'$or': [
               {'sender': uid},
               {'receipient': uid}
           ]}).sort("date_time", -1).limit(3)
    
    def get_by_sender(self, uid): # Remove
        return self.collection.find({"sender":uid}).sort("date_time", -1)
    
    def get_by_sender_limited(self, uid): # Remove
        return self.collection.find({"sender":uid}).sort("date_time", -1).limit(3)
    
    def get_by_reciepient(self, uid): # Remove
        return self.collection.find({"receipient":uid}).sort("date_time", -1)
    
    def get_by_receipient_limited(self, uid): # Remove
        return self.collection.find({"receipient":uid}).sort("date_time", -1).limit(3)
    
    def update_request_dtls(self,request_id, dtls):
        return self.collection.update_one({"_id":ObjectId(request_id)},{"$set":dtls.__dict__}).modified_count>0
    
    def delete_request(self, request_id):
        return self.collection.updated_one({"_id":ObjectId(request_id)}, {"$set": {"softdeleted_at": datetime.now()}}).modified_count>0
    
    def approve_request(self,request_id):
        return self.collection.update_one({"_id":ObjectId(request_id)},{"$set":{"status":"Approved"}}).modified_count>0
    
    def decline_request(self,request_id):
        return self.collection.update_one({"_id":ObjectId(request_id)},{"$set":{"status":"Declined"}}).modified_count>0
    
    def update_many_reqs(self):
        return self.collection.update_many({}, {"$set": {"avatar": "NIL"}})
    
class Reportdb:
    def __init__(self) -> None:
        self.collection = Reports
    
    def insert_new(self, request):
        return self.collection.insert_one(request.__dict__).inserted_id 
    
    def get_all(self):
        return self.collection.find({'softdeleted_at': None}).sort("created_at", DESCENDING)
    
    def get_all_limited(self):
        return self.collection.find({'softdeleted_at': None}).sort("created_at", DESCENDING).limit(3)
    
    def get_by_stack(self, stack):
        return self.collection.find({"stack": stack, 'softdeleted_at': None}).sort("created_at", DESCENDING)
    
    def get_by_isMember(self, uid):
        return self.collection.find({'$or': [
               {'sender': uid},
               {'receiver': uid}
           ], 'softdeleted_at': None}).sort("created_at", DESCENDING)
        
    def get_by_isMember_limited(self, uid):
        return self.collection.find({'$or': [
               {'sender': uid},
               {'receiver': uid}
           ], 'softdeleted_at': None}).sort("created_at", DESCENDING).limit(3)
    
    def get_by_report_id(self, _id):
        return self.collection.find_one({"_id":ObjectId(_id)})

    def get_by_sender(self, _id, uid):
        return self.collection.find({"sender":{"_id":_id, "uid":uid}}).sort("date_time", -1)
    
    def get_by_sender_limited(self, _id, uid):
        return self.collection.find({"sender":{"_id":_id, "uid":uid}}).sort("date_time", -1).limit(3)
    
    def get_by_recipient(self, position):
        return self.collection.find({"recipient":position}).sort("date_time", -1)
    
    def get_by_recipient_limited(self, position):
        return self.collection.find({"recipient":position}).sort("date_time", -1).limit(3)
    
    def update_report_dtls(self,report_id, dtls):
        return self.collection.update_one({"_id":ObjectId(report_id)},{"$set":dtls.__dict__}).modified_count>0
    
    def give_feedback(self,report_id, dtls):
        return self.collection.update_one({"_id":ObjectId(report_id)},{"$push":{"feedback": dtls}}).modified_count>0
    
    def add_doc(self, report_id, doc):
        return self.collection.update_one({"_id":ObjectId(report_id)},{"$push":{"submissions.docs": doc}}).modified_count>0
    
    def add_link(self, report_id, link):
        return self.collection.update_one({"_id":ObjectId(report_id)},{"$push":{"submissions.links": link}}).modified_count>0
    
    def mark_completed(self,report_id):
        return self.collection.update_one({"_id":ObjectId(report_id)},{"$set":{"status":"Completed"}}).modified_count>0
    
    def mark_incomplete(self,report_id):
        return self.collection.update_one({"_id":ObjectId(report_id)},{"$set":{"status":"Incomplete"}}).modified_count>0
    
    def delete_report(self, report_id):
        return self.collection.update_one({"_id":ObjectId(report_id)}, {"$set": {"softdeleted_at": datetime.now()}}).modified_count>0

class Inventorydb:
    def __init__(self) -> None:
        self.collection = Inventory
    
    def insert_new(self, dtls):
        return self.collection.insert_one(dtls.__dict__).inserted_id
    
    def get_all(self):
        return self.collection.find().sort("date_inserted")
    
class Attendancedb:
    def __init__(self) -> None:
        self.collection = Attendance
    
    def sign_in(self, dtls):
        return self.collection.insert_one(dtls).inserted_id
    
    def sign_out(self, attendance_id, time_out, status):
        return self.collection.update_one({"_id":ObjectId(attendance_id)},{"$set":{"time_out": time_out, "status": status}}).modified_count>0
    
    def get_attendance(self, user_id):
        return self.collection.find({"user_id": user_id}).sort("date_time", -1).limit(3)
    
class generate:   
    def password():
        password_length = int(6)
        characters = string.ascii_letters + string.digits
        password = ""   
        for index in range(password_length):
            password = password + random.choice(characters)
            
        return password

    def user_id(firstname):
        max = int(3)
        digits = string.digits
        #while 1:
            
        _id = firstname + "SSRL"
        
        for index in range(max):
            _id = _id + random.choice(digits)
            
            # if Users.find_one({"pwd":_id}) == "None": 
            #     break
            
        return _id 
    
    def file_id():
        max = int(16)
        digits = string.digits
        file_id = ""
        
        for index in range(max):
            file_id = file_id + random.choice(digits)
            
            # if Users.find_one({"pwd":_id}) == "None": 
            #     break
            
        return file_id 
    
    def OTP():
        length = int(6)
        characters = string.digits
        otp = ""     
        for index in range(length):
            otp = otp + random.choice(characters)
            
        return otp
    
class Notification:
    def __init__(self, title, receivers, type, message, status="unread", created_at=None) -> None:
        self.title = title
        self.receivers = receivers
        self.type = type
        self.message = message
        self.status = status
        self.created_at = created_at or datetime.now()

class Eqpt:
    def __init__(self, name, quantity, description, date_of_arrival, type, status, datetime_inputed, date_inserted) -> None:
        self.name = name
        self.quantity = quantity
        self.description = description
        self.date_of_arrival = date_of_arrival
        self.type = type
        self.status = status
        self.datetime_inputed = datetime_inputed
        self.date_inserted = date_inserted
        
class existEqpt:
    def __init__(self, quantity, datetime_inputed, status) -> None:
        self.quantity = quantity
        self.datetime_inputed = datetime_inputed
        self.status = status

class lostEqpt:
    def __init__(self, eqpt_id, name, type, quantity, personnel_id, status, date_reported, date_edited) -> None:
        self.eqpt_id = eqpt_id
        self.name = name
        self.type = type
        self.quantity = quantity
        self.personnel_id = personnel_id
        self.status = status
        self.date_reported = date_reported
        self.date_edited = date_edited
        
class updateAdmin:
    def __init__(self, firstname, surname, fullname, uid, stack, niche, role, filename, phone_num, email, bio, location, bday) -> None:
        self.firstname = firstname
        self.surname = surname
        self.fullname = fullname
        self.uid = uid
        self.stack = stack
        self.niche = niche
        self.role = role
        self.phone_num = phone_num
        self.email = email
        self.avatar = filename 
        self.bio = bio
        self.location = location
        self.bday = bday
        
class Request:
    def __init__(self, title, type, sender, avatar, receipient, request_dtls, created_at=None, status="Pending") -> None:
        self.title = title
        self.type = type
        self.sender = sender
        self.avatar = avatar
        self.receipient = receipient
        self.status = status
        self.created_at = created_at or datetime.now()
        self.request_dtls = request_dtls
class Report:
    def __init__(self, title, stack, report_type, receiver, sender, avatar, submissions=None, feedback=None, created_at=None):
        self.title = title 
        self.stack = stack 
        self.report_type = report_type
        self.submissions = submissions or {"docs": [], "links": []}
        self.feedback = feedback or []
        self.created_at = created_at or datetime.now()
        self.receiver = receiver
        self.sender = sender
        self.avatar = avatar
class ActivityReport(Report):
    def __init__(self, title, stack, duration, report_type,  receiver, sender, avatar, next,  completed, ongoing):
        super().__init__(title, stack, report_type, receiver, sender, avatar)
        
        self.duration = duration
        self.completed = completed
        self.ongoing = ongoing
        self.next = next
    
class Todo:
    def __init__(self, uid, todo=None, created_at=None):
        
        self.uid = uid
        self.todo = todo or []
        self.created_at = created_at or datetime.now()
class ProjectReport(Report):
    def __init__(self, title, stack, report_type, receiver, sender, avatar, summary):
        super().__init__(title, stack, report_type, receiver, sender, avatar)
        
        self.summary = summary
         
class AllowedExtension:    
    def images(filename):
        ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'svg'} 
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
    
    def files(filename):
        ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docs','docx', "txt"} 
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

class Available:
    def __init__(self, _quantity, _status) -> None:
        self.status = _status
        self.quantity = _quantity
    
class updateEmail:
    def __init__(self, new_email) -> None:
        self.email = new_email
        
class updatePwd:
    def __init__(self, hashed_pwd) -> None:
        self.hashed_pwd = hashed_pwd
        
def formatAttendance(dtls):
    user_dtls = []
    for dtl in dtls:
        user_dtl = {}
        user_dtl["user_uid"] = dtl["user_uid"]
        user_dtl["date"] = dtl["date"]
        user_dtl["time_in"] = dtl["time_in"]
        user_dtls.append(user_dtl)
        
    return user_dtls

def sortFunc(e):
  return e["date_time"]



if "__name__"=="__main__":
    eqpt_db = Eqptdb()
    
    dtls = Eqpt("REISTOR", "1", "RESISTOR", "22/2222", "KDBEH", "ACTIVE", "", "")
    
    eqpt_id = eqpt_db.new_input(dtls)
    print(eqpt_id)


