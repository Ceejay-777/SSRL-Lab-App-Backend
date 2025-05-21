from flask import Blueprint, request, jsonify
from models.models import generate, Notificationsdb, Notification
from flask_bcrypt import  generate_password_hash
from funcs import convert_to_json_serializable
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_mail import Message
from app.extensions import mail
from datetime import datetime
from funcs import *
import json
from models.user import User, Userdb
from models.project import Projectdb
from models.request import Requestdb
from models.report import Reportdb
from models.todo import Todosdb
from funcs import return_error

personnel_bp = Blueprint('personnel', __name__, url_prefix='/personnel')

User_db = Userdb()
Request_db = Requestdb()
Report_db = Reportdb()
Project_db = Projectdb()
Todos_db = Todosdb()
Notifications = Notificationsdb()

@personnel_bp.get('/home')
@jwt_required()
def home():
    try:
        uid = get_jwt_identity()
        
        user_profile = User_db.get_user_by_uid(uid)
        if not user_profile:
            return jsonify({"message": "User with uid '{uid}' not found", "status": "error"}), 404
        
        user_role = user_profile["role"]
        stack = user_profile["stack"]
        firstname = user_profile["firstname"]
        avatar = user_profile["avatar"]
        todos = list(Todos_db.get_todo_by_user_id_limited(uid))
        unread_notes = Notifications.get_unread_count(uid)
        
        if user_role=="Admin":
            projects = list(Project_db.get_all_limited())
            reports = list(Report_db.get_all_limited())
        elif user_role == "Lead":
            projects = list(Project_db.get_by_stack_limited(stack))
            reports = list(Report_db.get_by_isMember_limited(uid))
        else:
            projects = list(Project_db.get_by_isMember_limited(uid))
            reports = list(Report_db.get_by_isMember_limited(uid))
        
        requests = list(Request_db.get_by_isMember_limited(uid))
        notifications = list(Notifications.get_by_isMember_limited(uid))
            
        response = convert_to_json_serializable({"firstname" : firstname, "avatar" : avatar, "user_role": user_role, "stack": stack, "reports" : reports, "requests" : requests, "projects" : projects, "todos" : todos, "notifications": notifications, "unread": unread_notes, "status" : "success"})
            
        return jsonify(response), 200
    
    except Exception as e:
        return jsonify(return_error(e)), 500

@personnel_bp.get('/view_members')
@jwt_required()
def view_members():
    try:
        uid = get_jwt_identity()
        
        user = User_db.get_user_by_uid(uid)
        if not user:
            return jsonify({'message': 'User not found', 'status': 'error'}), 404
        
        admins = list(User_db.get_user_by_role(role = "Admin"))
        leads = list(User_db.get_user_by_role(role = "Lead"))
        interns = list(User_db.get_user_by_role(role="Intern"))
        
        softlead = [lead for lead in leads if lead['stack'] == "software"]
        hardlead = [lead for lead in leads if lead['stack'] == "hardware"]
        softinterns = [intern for intern in interns if intern['stack'] == "software"]
        hardinterns = [intern for intern in interns if intern['stack'] == "hardware"]
        
        response = {
        "admins" : admins,
        "softleads": softlead,
        "hardleads": hardlead,
        "softinterns": softinterns,
        "hardinterns": hardinterns,
        "status" : "success"
        } 
        return jsonify(convert_to_json_serializable(response)), 200
    
    except Exception as e:
        return jsonify(return_error(e)), 500
    
@personnel_bp.get('/get_members_identity/<role>')
@jwt_required()
def get_members_identity(role):
    try:
        admins = list(User_db.get_user_by_role(role = "Admin"))
        leads = list(User_db.get_user_by_role(role = "Lead"))
        interns = list(User_db.get_user_by_role(role="Intern"))
        
        admins_identity = [{"id": admin['uid'], "name": admin['fullname']} for admin in admins]
        softleads = [{"id": lead['uid'], "name": lead['fullname']} for lead in leads if lead['stack'] == "software"]
        softinterns = [{"id": intern['uid'], "name": intern['fullname']} for intern in interns if intern['stack'] == "software"]
        hardleads = [{"id": lead['uid'], "name": lead['fullname']} for lead in leads if lead['stack'] == "hardware"]
        hardinterns = [{"id": intern['uid'], "name": intern['fullname']} for intern in interns if intern['stack'] == "hardware"]
        
        if role == 'softmembers':
            response = {'members': softleads + softinterns, 'status': 'success'}
            
        elif role == 'hardmembers':
            response = {'members': hardleads + hardinterns, 'status': 'success'}
            
        elif role == 'allmembers':
            response = {'members': admins_identity + softleads + softinterns + hardleads + hardinterns, 'status': 'success'}
            
        elif role == 'admins':
            response = {'members': admins_identity, 'status': 'success'}
            
        elif role == 'leads':
            response = {'members': softleads + hardleads, 'status': 'success'}
            
        elif role == 'softleads':
            response = {'members': softleads, 'status': 'success'}
            
        elif role == 'hardleads':
            response = {'members': hardleads, 'status': 'success'}
            
        elif role == 'softinterns':
            response = {'members': softinterns, 'status': 'success'}
            
        elif role == 'hardinterns':
            response = {'members': hardinterns, 'status': 'success'}
            
        elif role == 'admins_and_all_members':
            response = {'members': admins_identity + softleads + softinterns + hardleads + hardinterns, 'status': 'success'}
            
        else:
            response = {'message': 'Invalid role', 'status': 'error'}
        
        return jsonify(convert_to_json_serializable(response)), 200
    
    except Exception as e:
        return jsonify(return_error(e)), 500

@personnel_bp.get('/get_profile/<requested_uid>') 
@jwt_required()
def get_member_profile(requested_uid):
    try:
        requested_profile = User_db.get_user_by_uid(requested_uid)
        if not requested_profile:
            return jsonify({'message': f"Personnel with uid '{requested_uid}' not found", 'status': 'error'})
        
        response = {"profile" : requested_profile, "status" : "success" }
        
        return jsonify(convert_to_json_serializable(response)), 200
    
    except Exception as e:  
        return jsonify(return_error(e)), 500
    
@personnel_bp.post('/admin_create_user')
@jwt_required()
@admin_and_lead_role_required
def create_user():
    try:
        data = json.loads(request.form.get('info'))
        print(data)
        
        firstname = data.get("firstname")
        surname = data.get("surname")
        pwd = generate.password()
        hashed_pwd = generate_password_hash(pwd)
        stack = data.get("stack")
        niche = data.get("niche")
        role = data.get("role")
        phone_num = data.get("phone_num")
        email = data.get("email")
        bio = data.get("bio", None)
        bday = data.get("bday", None)
        
        while True:
            uid = generate.user_id(firstname)
            
            if not User_db.get_user_by_uid(uid):
                break
            
        avatar_url = None
        avatar = request.files.get("avatar", None)
        avatar_msg = ''
        
        if avatar :
            if not allowed_file(avatar.filename):
                return {'message': 'Invalid avatar file type', 'status': 'error'}, 400
            
            if len(avatar.read()) > 500 * 1024:
                return {'message': 'Avatar size should not exceed 500KB', 'status': 'error'}, 400
            
            avatar.seek(0)
            
            try:
                upload_result = upload_file(avatar, 'SSRL_Lab_App/interns/profile_image')
                
                if not upload_result:
                    avatar_msg = "Avatar upload failed"
                    
                avatar_msg = ''
                avatar_url = {"secure_url": upload_result['secure_url'], "public_id": upload_result['public_id']}
                
            except Exception as e:
                return {'message': f'avatar upload failed: {str(e)}', 'status': 'error'}, 500
        
        user = User(surname=surname, hashed_pwd=hashed_pwd, uid=uid, stack=stack, niche=niche, role=role, phone_num=phone_num, email=email, avatar=avatar_url, bio=bio, bday=bday, firstname=firstname)
        
        user_id= User_db.create_user(user)
        if not user_id:
            return jsonify({"message": "Unable to create user at the moment. Please try again", "status" : "error"}), 500
        
        response = convert_to_json_serializable({"message" : f"user {uid} created successfully. {avatar_msg}", "user_id" : str(user_id), "status" : "success"})
        
        try:
            msg = Message('SSRL Login credentials', recipients = [email])
            msg.body = f"Welcome to SSRL🤗 \nCheck out your login credentials below\n\nUnique I.D: {uid} \nPassword: {pwd}  \n\n\nFrom SSRL Team"
            
            mail.send(msg)
        
            return jsonify(response), 200 
        
        except Exception as e:
            return (return_error(e)), 500
        
    except Exception as e:
        print(e)
        return jsonify({"message": f"Unable to create user at the moment! Please confirm that the inputed email is correct or check your internet connection. {e}", "status" : "error"}), 500
    
@personnel_bp.get('/me')
@jwt_required()
def view_my_profile():
    try:
        uid = get_jwt_identity()
        
        user_profile = User_db.get_user_by_uid(uid)
        if not user_profile:
            return jsonify({'message': 'Profile not found', 'status': 'error'}), 404
        
        response = {"user_profile" : user_profile, "status" : "success"}
        return jsonify(convert_to_json_serializable(response)), 200 
    
    except Exception as e:
        return jsonify(return_error(e)), 500

@personnel_bp.patch('/edit_profile') 
@jwt_required()
def edit_profile(): 
    try:
        uid = get_jwt_identity()
        data = json.loads(request.form.get('info'))
        avatar = request.files.get('avatar', None)
        
        user = User_db.get_user_by_uid(uid)    
        if not user:
            return jsonify({"message": f"User with uid '{uid}' not found", "status": "error"}), 404
            
        avatar_msg = ''
        previous_avatar = user.get('avatar')
        
        if avatar: 
            if not allowed_file(avatar.filename):
                return {'message': 'Invalid avatar file type', 'status': 'error'}, 400
            
            if len(avatar.read()) > 500 * 1024:
                return {'message': 'File size should not exceed 500KB', 'status': 'error'}, 400
            
            avatar.seek(0)
            
            try: 
                uploaded = upload_file(avatar, folder="SSRL_Lab_App/interns/profile_image")
                
                if not uploaded:
                    avatar_msg = "Could not upload image right now"
                    
                else:
                    avatar = {'secure_url': uploaded["secure_url"], 'public_id': uploaded["public_id"]}
                    if previous_avatar:
                        delete_file(previous_avatar.get('public_id'))
                    
            except Exception as e:
                avatar_msg = f"Could not upload image right now: {str(e)}"
                print(e)
                
        data['avatar'] = avatar
        updated = User_db.update_user(uid, data)
    
        if not updated['success']:
            return jsonify({"message": f"{updated['error']}", "status" : "error"}), 403
        
        return jsonify({"message": f"profile updated successfully {avatar_msg}", "status" : "success"}), 200
        
    except Exception as e:
        return jsonify(return_error(e)), 500

@personnel_bp.patch('/admin_edit_profile/<uid>')
@jwt_required()
@admin_and_lead_role_required
def admin_edit_profile(uid):
    try:
        data = json.loads(request.form.get('info'))
        
        avatar = request.files.get("avatar", None)
        avatar_msg = ''
        
        user = User_db.get_user_by_uid(uid)
        if not user:
            return jsonify({"message": f"User with uid '{uid}' not found", "status": "error"}), 404
        
        previous_avatar = user.get('avatar')
        
        if avatar:
            if not allowed_file(avatar.filename):
                return {'message': 'Invalid avatar file type', 'status': 'error'}, 400
            
            if len(avatar.read()) > 500 * 1024:
                return {'message': 'File size should not exceed 500KB', 'status': 'error'}, 400
            
            avatar.seek(0)
            
            try:
                uploaded = upload_file(avatar, 'SSRL_Lab_App/interns/profile_image')
                if not uploaded:
                    avatar_msg = "Avatar upload failed"
                    
                else:
                    avatar_msg = ''
                    avatar = {"secure_url": uploaded['secure_url'], "public_id": uploaded['public_id']}
                    
                    if previous_avatar:
                        delete_file(previous_avatar.get('public_id'))
                    
            except Exception as e:
                return {'message': f'avatar upload failed: {str(e)}', 'status': 'error'}, 500    
        
            data['avatar'] = avatar
            
        edited = User_db.update_user(uid, data)
        if not edited['success']:
            return jsonify({"message": f"Profile update unsuccessful: {edited['error']}", "status": "error"}), 500
        
        return jsonify({"message": f"Profile updated successfully. {avatar_msg}", "status": "success"}), 200
    
    except Exception as e:
        return jsonify(return_error(e)), 500
            
@personnel_bp.patch('/add_lead/<intern_uid>') 
@jwt_required()
@admin_and_lead_role_required
def admin_add_lead(intern_uid):
    try:
        user = User_db.get_user_by_uid(intern_uid)
        if not user:
            return jsonify({"message": f"User with uid '{intern_uid}' not found", "status": "error"}), 404
            
        stack = user["stack"]
        dtls = {"role": "Lead"}
        
        updated = User_db.update_dtl(intern_uid, dtls)
        if not updated:
            return jsonify({"message": f"Could not make {intern_uid} a {stack} lead", "status" : "error"}), 500
            
        return jsonify({"message": f"You've successfully made {intern_uid} a {stack} Lead", "status" : "success"}), 200

    except Exception as e:  
            return jsonify(return_error(e)), 500
   
@personnel_bp.patch('/remove_lead/<intern_uid>') 
@jwt_required()
@admin_and_lead_role_required
def admin_remove_lead(intern_uid):
    try:
        user = User_db.get_user_by_uid(intern_uid)
        if not user:
            return jsonify({"message": f"User with uid '{intern_uid}' not found", "status": "error"}), 404
            
        stack = user["stack"]
        dtls = {"role": "Intern"}
        
        updated = User_db.update_dtl(intern_uid, dtls)
        if not updated:
            return jsonify({"message": f"Could not remove {intern_uid} as {stack} lead", "status" : "error"}), 500
            
        return jsonify({"message": f"You've successfully removed {intern_uid} as {stack} Lead", "status" : "success"}), 200

    except Exception as e:  
            return jsonify(return_error(e)), 500
    
@personnel_bp.patch('/add_admin/<intern_uid>') 
@jwt_required()
@admin_role_required
def admin_add_admin(intern_uid):
    try:
        user = User_db.get_user_by_uid(intern_uid)
        if not user:
            return jsonify({"message": f"User with uid '{intern_uid}' not found", "status": "error"}), 404
        
        dtls = {"role": "Admin"}
        
        updated = User_db.update_dtl(intern_uid, dtls)
        if not updated:
            return jsonify({"message": f"Could not make {intern_uid} an Admin", "status" : "error"}), 500
        
        return jsonify({"message": f"You've successfully made {intern_uid} an Admin", "status" : "success"}), 200
            
    except Exception as e:  
        return jsonify(return_error(e)), 500
        
@personnel_bp.patch('/remove_admin/<intern_uid>') 
@jwt_required()
@admin_role_required
def admin_remove_admin(intern_uid):
    try:
        user = User_db.get_user_by_uid(intern_uid)
        if not user:
            return jsonify({"message": f"User with uid '{intern_uid}' not found", "status": "error"}), 404
        
        dtls = {"role": "Intern"}
        
        updated = User_db.update_dtl(intern_uid, dtls)
        if not updated:
            return jsonify({"message": f"Could not remove {intern_uid} as Admin", "status" : "error"}), 500
        
        return jsonify({"message": f"You've successfully removed {intern_uid} as Admin", "status" : "success"}), 200
            
    except Exception as e:  
        return jsonify(return_error(e)), 500

@personnel_bp.delete('/delete_user/<intern_uid>')
@jwt_required()
@admin_role_required
def admin_delete_user(intern_uid):
    try:
        user = User_db.get_user_by_uid(intern_uid)
        if not user:
            return jsonify({"message": f"User with uid '{intern_uid}' not found", "status": "error"}), 404
        
        dtls = {"deleted_at": datetime.now()}
        deleted = User_db.update_dtl(intern_uid, dtls)
        
        if not deleted:
            return jsonify({"message": f"Could not delete {intern_uid}!", "status" : "error"}), 400
            
        return jsonify({"message": f"User {intern_uid} deleted successfully!", "status" : "success"}), 200
    
    except Exception as e:  
        return jsonify(return_error(e)), 500
    
@personnel_bp.patch('/suspend_user/<intern_uid>')
@jwt_required()
@admin_role_required
def admin_suspend_user(intern_uid):
    try:
        user = User_db.get_user_by_uid(intern_uid)
        if not user:
            return jsonify({"message": f"User with uid '{intern_uid}' not found", "status": "error"}), 404
        
        dtls = {"suspended": True}
        suspended = User_db.update_dtl(intern_uid, dtls)

        if not suspended:
            return jsonify({"message": f"Could not suspend {intern_uid}!", "status" : "error"}), 400
        
        return jsonify({"message": f"User {intern_uid} suspended successfully!", "status" : "success"}), 200
    
    except Exception as e:  
        return jsonify(return_error(e)), 500
    
@personnel_bp.patch('/unsuspend_user/<intern_uid>')
@jwt_required()
@admin_role_required
def admin_unsuspend_user(intern_uid):
    try:
        user = User_db.get_user_by_uid(intern_uid)
        if not user:
            return jsonify({"message": f"User with uid '{intern_uid}' not found", "status": "error"}), 404
        
        dtls = {"suspended": False}
        suspended = User_db.update_dtl(intern_uid, dtls)

        if not suspended:
            return jsonify({"message": f"Could not unsuspend {intern_uid}!", "status" : "error"}), 400
        
        return jsonify({"message": f"User {intern_uid} unsuspended successfully!", "status" : "success"}), 200
    
    except Exception as e:  
        return jsonify(return_error(e)), 500
