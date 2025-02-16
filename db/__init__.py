from pymongo import MongoClient

uri_local = "mongodb://localhost:27017"
client = MongoClient("mongodb+srv://smartsystemlaboratory:vu52ZVyLHpAkRrGk@cluster0.lk2pi.mongodb.net/")
db = client['LAB_APP_DB']
Users = db['Users']
Notifications = db['Notifications']
Todos = db['Todos']
Eqpts = db['Equipments']
lost_eqpts = db["Lost_eqpt"]
Requests = db["Requests"]
Reports = db["Reports"]
Projects = db["Projects"]
Inventory = db["Inventory"]
Attendance = db["Attendance"]
Attendance_v2 = db["Attendance_v2"]
Sessions = db["Session"]
Reports = db["Reports"]


