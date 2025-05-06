from app.extensions import mongo_client

db = mongo_client['LAB_APP_DB']

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
Sessions = db["Session"]
Reports = db["Reports"]


