from flask import Blueprint, request, jsonify
from models.models import generate, updatePwd, Reportdb, Todosdb, Notificationsdb, Notification, AllowedExtension
from flask_bcrypt import Bcrypt, check_password_hash, generate_password_hash
from funcs import convert_to_json_serializable
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_jwt
from flask_mail import Message
from app.extensions import mail
from datetime import datetime, timedelta
from funcs import *
import json
from werkzeug.utils import secure_filename
from models.user import Userdb
from models.project import Project, Projectdb
from models.request import Request, Requestdb
from funcs import return_error, get_la_code

request_bp = Blueprint('request', __name__, url_prefix='/request')

User_db = Userdb()
Request_db = Requestdb()
Report_db = Reportdb()
Project_db = Projectdb()
Todos_db = Todosdb()
Notifications = Notificationsdb()

@request_bp.post('/create_request')
@jwt_required()
def create_request():
    try:
        uid = get_jwt_identity()
        user = User_db.get_user_by_uid(uid)
        name =  user.get('surname') + " " + user.get('firstname')
        
        avatar = user.get('avatar', None)
        if avatar:
            avatar = avatar['secure_url']
       
        data = request.json
        print(data)
        title = data.get("title")
        type = data.get("type")
        request_details = data.get("request_details")
        receipient = data.get("receipient")
        purpose = data.get("purpose")
        
        sender = {'id': uid, 'name': name, 'avatar': avatar}
        
        while True:
            request_id = get_la_code('rqt')
            if not Request_db.get_by_request_id(request_id):
                break
        
        new_request = Request(title=title, type=type, sender=sender, receipient=receipient, request_details=request_details, purpose=purpose, request_id=request_id)
        
        created = Request_db.create_request(new_request)
        if not created:
            return jsonify({"message" : "Request unable to be submitted. Please try again!", "status" : "error"}), 500
        
        rec_not_title = "You received a new Request"
        rec_not_receivers = receipient
        rec_not_type = "Request"
        rec_not_message = f"You just received a new request from {name}. Check it out in your requests tab!"
        notification = Notification(rec_not_title, rec_not_receivers, rec_not_type, rec_not_message)
            
        Notifications.send_notification(notification)
        
        return jsonify({"message" : "Request submitted successfully!", "status" : "success"}), 200
    
    except Exception as e:
        return jsonify({"message": f'Something went wrong: {e}', 'status': "error"}), 500
    
@request_bp.get('/request/get_all')
@jwt_required()
def get_all_requests():
    try:
        uid = get_jwt_identity()
        role = get_jwt().get('user_role')
        
        if role == 'Admin':
            requests = list(Request_db.get_all())
        else:
            requests = list(Request_db.get_by_isMember(uid))
            
        requests = convert_to_json_serializable(requests)
            
        return jsonify({'requests': requests, 'status': 'success'})
        
    except Exception as e:
        return jsonify({"message": f'Something went wrong: {e}', 'status': "error"}), 500
    

@request_bp.get('/request/get_request/<request_id>')
@jwt_required()
def view_request(request_id):
    try:
        request = Request_db.get_by_request_id(request_id)
        if not request:
            return jsonify({"message": "Request not found", "status": "error"}), 404
        
        response = convert_to_json_serializable({"request":request, "status" : "success"})
        return jsonify(response), 200
    
    except Exception as e:
        return jsonify({"message": f'Something went wrong: {e}', 'status': "error"}), 500
    
@request_bp.post('/request/approve/<request_id>')
@jwt_required()
def approve_request(request_id):
    try:
        uid = get_jwt_identity()
        approved = Request_db.approve_request(request_id)
        title = Request_db.get_by_request_id(request_id)['title']
        
        not_title = "Request Approved"
        not_receivers = [uid]
        not_type = "Request"
        not_message = f"Your request '{title}' has been approved. Check it out in your requests tab!"
        not_status = "unread"
        not_sentAt = datetime.now()
        notification = Notification(not_title, not_receivers, not_type, not_message, not_status, not_sentAt)

        if approved: 
            Notifications.send_notification(notification)
            return jsonify({"message" : 'Request approved', "status" : "success"}), 200                                                  
        else:
            return jsonify({"message" : 'An error occurred! Try again', "status" : "danger"}), 500
        
    except Exception as e:
        return jsonify({"message": f'Something went wrong: {e}', 'status': "error"}), 500
    
@request_bp.post('/request/decline/<request_id>')
@jwt_required()
def decline_request(request_id):
    try:
        uid = get_jwt_identity()
        declined = Request_db.decline_request(request_id)
        title = Request_db.get_by_request_id(request_id)['title']
        
        not_title = "Request Declined"
        not_receivers = [uid]
        not_type = "Request"
        not_message = f"Your request '{title}' has been declined. Check it out in your requests tab!"
        not_status = "unread"
        not_sentAt = datetime.now()
        notification = Notification(not_title, not_receivers, not_type, not_message, not_status, not_sentAt)

        Notifications.send_notification(notification)
        return jsonify({"message" : 'Request declined', "status" : "success"})                                                   
    except Exception as e:
        return jsonify({"message": f'Something went wrong: {e}', 'status': "error"}), 500

@request_bp.get('/request/delete/<request_id>') 
def delete_request(request_id):
    try:
        deleted = Request_db.delete_request(request_id)
        
        if deleted:
            return jsonify({"message" : 'Request deleted successfully!', "status" : "success"}), 200     
        else:
            return jsonify({"message" : 'The request was unsuccessful!', "status" : "danger"}), 500  
    except Exception as e:
        return jsonify({"message": f'Something went wrong: {e}', 'status': "error"}), 500