from bson.objectid import ObjectId 
from properties import *
import os
import string, random
from datetime import datetime, timedelta
from db import *
from pymongo import DESCENDING, ASCENDING

class Userdb:
    def __init__(self) -> None:
        self.collection =  Users

    def create_user(self, usr):
        return self.collection.insert_one(usr.__dict__).inserted_id
        
    def get_user_by_role(self, role):
        return self.collection.find({"role": role, "deleted": "False"})
    
    def get_user_fullname(self, uid):
        user = self.collection.find_one({"uid" : uid})
        return user["fullname"]
    
    def get_user_by_role_one(self, role):
        return self.collection.find_one({"role": role})
    
    def get_user_by_uid(self, user_uid):
        return self.collection.find_one({"uid": user_uid})
    
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
    
    # def update_user(self, user_id, dtls):
    #     return self.collection.update_one({"uid":user_id},{"$set":dtls}).modified_count>0
    
    def update_user(self, user_id, dtls):
        try:
            result = self.collection.update_one({"uid": user_id}, {"$set": dtls})
            
            if result.matched_count == 0:
                return {"success": False, "error": "No user found with the given UID"}
            if result.modified_count == 0:
                return {"success": False, "error": "No changes were made to the document"}
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
class Notificationsdb:
    def __init__(self):
        self.collection = Notifications
        
    def send_notification(self, dtls):
        print("Notification Created")
        return self.collection.insert_one(dtls.__dict__).inserted_id
    
    def get_by_isMember(self, uid):
        return self.collection.find({'receivers' : uid})
    
    def get_by_isMember_limited(self, uid):
        return self.collection.find({'receivers' : uid}).limit(3)
    
    # Get all notifications for a particular user
    
    
class Todosdb:
    def __init__(self) -> None:
        self.collection = Todos
        
    def create_todo(self, dtls):
        print("Okay")
        return self.collection.insert_one(dtls.__dict__).inserted_id
    
    def add_todo(self, uid, todo):
        # print("Okay")
        return self.collection.update_one({"uid":uid},{"$push": {"todo": {"todo": todo, "created_at": datetime.now(), "completed": False}}}).modified_count>0
    
    def change_status(self, uid, status):
        return self.collection.update_one({"uid": uid}, {"$set": {"todo.completed": status}}).modified_count>0

    def delete_todo(self, uid):
        return self.collection.update_one({"uid":uid}, {"$set": {"softdeletd_at" : datetime.now()}}).modified_count>0
    
    def get_todos_by_user_id(self, user_id):
        return self.collection.find({"uid":user_id})
    
    def get_todos_by_user_id_limited(self, user_id):
        return self.collection.find({"uid":user_id}).lomit(4)
    
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

class Projectdb:
    def __init__(self) -> None:
        self.collection = Projects
        
    def get_all(self):
        return self.collection.find({'softdeleted_at': None}).sort("date_created", DESCENDING)
    
    def get_all_limited(self):
        return self.collection.find({'softdeleted_at': None}).sort("date_created", DESCENDING).limit(4)
    
    def get_by_isMember_limited(self, uid):
        return self.collection.find({'$or': [
               {'leads': uid,},
               {'team_members': uid}
           ], 'softdeleted_at': None}).sort('date_created', DESCENDING).limit(4)
    
    def get_by_isMember(self, uid):
        return self.collection.find({'$or': [
               {'leads': uid},
               {'team_members': uid}
           ], 'softdeleted_at': None}).sort('date_created', DESCENDING)
    
    def insert_new(self, request):
        existing_project = self.collection.find_one({"name": request.name})
        if not existing_project:
            return self.collection.insert_one(request.__dict__).inserted_id
        
    def existing_project_name(self, name):
        return self.collection.find_one({"name": name})
    
    def project_exists(self, project_id):
        try:
            project = self.collection.find_one({'_id': ObjectId(project_id)})
            return project is not None
        except:
            return False
        
    def get_project_name(self, project_id):
        project = self.collection.find_one({'_id': ObjectId(project_id)})
        return project['name']
    
    def get_project_members(self, project_id):
        project = self.collection.find_one({'_id': ObjectId(project_id)})
        return project['leads'] + project['team_members']
    
    def get_project_leads(self, project_id):
        project = self.collection.find_one({'_id': ObjectId(project_id)})
        return project['leads']
    
    def get_project_team_members(self, project_id):
        project = self.collection.find_one({'_id': ObjectId(project_id)})
        return project['team_members']
    
    def get_project_submissions(self, project_id):
        project = self.collection.find_one({'_id': ObjectId(project_id)})
        return project['submissions']
    
    def get_by_project_id(self, _id):
        return self.collection.find_one({"_id":ObjectId(_id)})
    
    def submit_doc(self, project_id, doc):
        return self.collection.update_one({'_id': ObjectId(project_id)}, {'$push': {'submissions.docs': doc}}).modified_count > 0
    
    def submit_link(self, project_id, link):
        return self.collection.update_one({'_id': ObjectId(project_id)}, {'$push': {'submissions.links': link}}).modified_count > 0
        
    def get_by_sender(self, uid): # Remove
        return self.collection.find({"sender": "uid"}).sort("date_time", -1)
    
    def get_by_sender_limited(self, _id, uid): # Remove
        return self.collection.find({"sender":{"_id":_id, "uid":uid}}).sort("date_time", -1).limit(4)
    
    def get_by_stack_limited(self, stack):
        return self.collection.find({"stack" : stack}).sort("date_time", -1).limit(4)
    
    def get_by_stack(self, stack, uid):
        return self.collection.find({"$or" : [
            {"stack" : stack}, 
            {"uid": uid},
        ], 'softdeleted_at': None}).sort("date_time", -1)
    
    def get_by_recipient_dtls(self, category, recipient, name):
        return self.collection.find({"recipient_dtls":{"category":category, "recipient": recipient, "name":name}}).sort("date_time", -1)
    
    def get_by_recipient_dtls_limited(self, category, recipient, name):
        return self.collection.find({"recipient_dtls":{"category":category, "recipient": recipient, "name":name}}).sort("date_time", -1).limit(4)
    
    def update_project_dtls(self, project_id, dtls):
        return self.collection.update_one({"_id":ObjectId(project_id)},{"$set":dtls}).modified_count>0
    
    def submit_project(self, project_id, dtls, no_submissions): #Remove
        return self.collection.update_one({"_id":ObjectId(project_id)},{"$set":{"submissions":dtls, "no_submissions":no_submissions}}).modified_count>0
    
    def mark_project(self, project_id, status):
        marked = self.collection.update_one({"_id":ObjectId(project_id)},{"$set":{"status":status}}).modified_count>0
        print(marked)
        return marked
    
    def delete_project(self, project_id, name):
        return self.collection.update_one({"_id":ObjectId(project_id)}, {"$set":{"softdeleted_at": datetime.now()}}).modified_count>0
    
    def send_feedback(self, project_id, sender, feedback):
        return self.collection.update_one({"_id":ObjectId(project_id)}, {"$push": {"feedback":{'feedback': feedback, 'sender': sender, 'created_at': datetime.now()}}}).modified_count>0
    
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
     

class Attendancedb_v2:
    def __init__(self) -> None:
        self.collection = Attendance_v2
    
    def sign_in(self, dtls):
        return self.collection.insert_one(dtls).inserted_id
    
    def sign_out(self, attendance_id, time_out, status):
        return self.collection.update_one({"_id":ObjectId(attendance_id)},{"$set":{"time_out": time_out, "status": status}}).modified_count>0
    
    def get_attendance(self, user_id):
        return self.collection.find({"user_id": user_id}).sort("date_time", -1).limit(3)
     
    def get_user_attendance_by_date(self, user_uid, date):
        return self.collection.find({"user_uid": user_uid, "date":date})
    
    def get_marked_in_users(self, date):
        return self.collection.find({"date": date, "status": "in"}).sort("date_time", -1)
    
class Sessionsdb:
    def __init__(self) -> None:
        self.collection = Sessions
        
    def create_session(self, session):
        return self.collection.insert_one(session.__dict__).inserted_id
    
    def get_session(self, session_id):
        return self.collection.find_one({"_id": ObjectId(session_id)})
    
    def expire_sessions(self):
        eight_hours_ago = datetime.now() - timedelta(hours=8)
        self.collection.update_many({"last_accessed": {"$lt": eight_hours_ago}}, {"$set": {"expired": "true"}})
    
    def cleanup(self): # Possibly add an expired condition
        nine_hours_ago = datetime.now() - timedelta(hours=9)
        self.collection.delete_many({"last_accessed": {"$lt": nine_hours_ago}})
        
    # def update_session(self, session_id, user_data):
    #     return self.collection.update_one({"_id": ObjectId(session_id)}, {"$set": {"user_data": user_data}}).modified_count>0
    
    def update_session(self, session_id, user_data):
        try:
            result = self.collection.update_one(
                {"_id": ObjectId(session_id)},
                {"$set": {"user_data": user_data}}
            )
            return result.matched_count > 0  
        except Exception as e:
            print(f"Error updating session: {e}")
            return False
    
    def delete_session(self, session_id):
        self.collection.delete_one({"session_id": session_id})    
    
    
class generate:   
    def password():
        password_length = int(12)
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
    
class User:
    def __init__(self, firstname, surname, fullname, hashed_pwd, uid, stack, niche, role, phone_num, email, mentor_id, avatar, task_id, bio, location, bday, datetime_created, suspended="False", deleted="False") -> None:
        self.firstname = firstname
        self.surname = surname
        self.fullname = fullname
        self. hashed_pwd = hashed_pwd
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
        self.deleted = deleted
        
class Notification:
    def __init__(self, title, receivers, type, message, status="unread", sentAt=None) -> None:
        self.title = title
        self.receivers = receivers
        self.type = type
        self.message = message
        self.status = status
        self.sentAt = sentAt or datetime.now()

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
        
class Project:
    def __init__(self, name, description, objectives, leads, team_members, team_avatars, stack, createdBy, status, submissions, date_created, deadline) -> None:
        self.name = name
        self.description = description
        self.objectives = objectives
        self.team_members = team_members
        self.leads = leads
        self.team_avatars = team_avatars
        self.stack = stack
        self.createdBy = createdBy
        self.status = status
        self.submissions = submissions
        self.date_created = date_created
        self.deadline = deadline
        
class Session:
    def __init__(self, user_data={}, created_at=datetime.now(), last_accessed=datetime.now(), expired="false"):
        self.user_data = user_data
        self.created_at = created_at
        self.last_accessed = last_accessed
        self.expired = expired
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


