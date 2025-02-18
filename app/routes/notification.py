from flask import Blueprint, request, jsonify
from db.models import Userdb, generate, updatePwd, Reportdb, Requestdb, Projectdb, Todosdb, Notificationsdb, Notification, AllowedExtension, User, Request
from flask_bcrypt import Bcrypt, check_password_hash, generate_password_hash
from funcs import convert_to_json_serializable
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_jwt
from flask_mail import Message
from app.extensions import mail
from datetime import datetime, timedelta
from funcs import *
import json
from werkzeug.utils import secure_filename

notification_bp = Blueprint('notification', __name__)

User_db = Userdb()
Request_db = Requestdb()
Report_db = Reportdb()
Project_db = Projectdb()
Todos_db = Todosdb()
Notifications_db = Notificationsdb()


@notification_bp.get("/notification/get_all")
@jwt_required()
def get_all_notifications():
    try:
        uid = get_jwt_identity()
        
        all_notifications = convert_to_json_serializable(list(Notifications_db.get_by_isMember(uid)))
        total = len(all_notifications)
        print(total)
        unread = Notifications_db.get_unread_count(uid)
        return jsonify({"notifications": all_notifications, "total": total, "unread": unread, "status": "success"})
    except Exception as e:
        return jsonify({"message": f'Something went wrong: {e}', 'status': "error"}), 500
    
@notification_bp.post("/notification/mark_as_read/<id>")
@jwt_required()
def mark_as_read(id):
    try:
        uid = get_jwt_identity()
        marked = Notifications_db.mark_as_read(id)
        
        # if not marked:
        #     return jsonify({"message": "Notification not found", "status": "error"}), 404
        
        return jsonify({"message": "Notification marked as read", "status": "success"}), 200
    
    except Exception as e:
        return jsonify({"message": f'Something went wrong: {e}', 'status': "error"}), 500
    
@notification_bp.post("/notification/mark_all_as_read")
@jwt_required()
def mark_all_as_read():
    try:
        uid = get_jwt_identity()
        marked = Notifications_db.mark_all_as_read(uid)
        
        if not marked:
            return jsonify({"message": "Somethig went wrong, try again", "status": "error"}), 404
        
        return jsonify({"message": "All notifications marked as read", "status": "success"}), 200
    except Exception as e:
        return jsonify({"message": f'Something went wrong: {e}', 'status': "error"}), 500

@notification_bp.delete("/notification/delete/<id>")
@jwt_required()
def delete_notification(id):
    try:
        deleted = Notifications_db.delete_notification(id)
        
        if not deleted:
            return jsonify({"message": "Notification not found", "status": "error"}), 404
        
        return jsonify({"message": "Notification deleted", "status": "success"})    
    except Exception as e:
        return jsonify({"message": f'Something went wrong: {e}', 'status': "error"}), 500

# @notification_bp.delete("/notification/delete_all")
# @jwt_required()
# def delete_all_notifications():
#     try:
#         uid = get_jwt_identity()
#         Notifications_db.delete_all_notifications(uid)
#         return jsonify({"message": "All notifications deleted", "status": "success"})
#     except Exception as e:
#         return jsonify({"message": f'Something went wrong: {e}', 'status': "error"}), 500

# @notification_bp.get("/notification/get_unread_count")
# @jwt_required()
# def get_unread_count():
#     try:
#         uid = get_jwt_identity()
#         unread_count = Notifications_db.get_unread_count(uid)
#         return jsonify({"unread_count": unread_count, "status": "success"})
#     except Exception as e:
#         return jsonify({"message":