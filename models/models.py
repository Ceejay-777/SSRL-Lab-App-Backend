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
            
        _id = firstname + "SSRL"
        
        for index in range(max):
            _id = _id + random.choice(digits)
            
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


class AllowedExtension:    
    def images(filename):
        ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'svg'} 
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
    
    def files(filename):
        ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docs','docx', "txt"} 
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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


