from flask import Blueprint, request, jsonify
from db.models import Userdb, generate, updatePwd, Reportdb, Requestdb, Projectdb, Todosdb, Notificationsdb, Notification, AllowedExtension, User
from flask_bcrypt import Bcrypt, check_password_hash, generate_password_hash
from funcs import convert_to_json_serializable
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_jwt
from flask_mail import Message
from app.extensions import mail
from datetime import datetime, timedelta
from funcs import *
import json
from werkzeug.utils import secure_filename

personnel_bp = Blueprint('personnel', __name__)

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
            return jsonify({"message": "User not found", "status": "error"}), 404
        
        uid = user_profile["uid"]
        user_role =user_profile["role"]
        stack = user_profile["stack"]
        firstname = user_profile["firstname"]
        avatar = user_profile["avatar"]
        todos = list(Todos_db.get_todos_by_user_id_limited(uid))
        
        if user_role=="Admin":
            projects = list(Project_db.get_all_limited())
            reports = list(Report_db.get_all_limited())
        elif user_role == "Lead":
            projects = list(Project_db.get_by_stack_limited(stack))
        else:
            projects = list(Project_db.get_by_isMember_limited(uid))
            reports = list(Report_db.get_by_isMember_limited(uid))
        
        requests = list(Request_db.get_by_isMember_limited(uid))
        notifications = list(Notifications.get_by_isMember_limited(uid))
            
        response = convert_to_json_serializable({"firstname" : firstname, "avatar" : avatar, "user_role": user_role, "stack": stack, "reports" : reports, "requests" : requests, "projects" : projects, "todos" : todos, "notifications": notifications, "status" : "success"})
            
        return jsonify(response), 200
    
    except Exception as e:
        return jsonify({'message': f"Something went wrong: {e}", 'status': 'error'}), 500

@personnel_bp.get('/view/members')
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
        
        softlead = [lead for lead in leads if lead['stack'] == "Software"]
        hardlead = [lead for lead in leads if lead['stack'] == "Hardware"]
        softinterns = [intern for intern in interns if intern['stack'] == "Software"]
        hardinterns = [intern for intern in interns if intern['stack'] == "Hardware"]
        
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
        return jsonify({'message': f"Something went wrong: {e}", 'status': 'error'}), 500
    
@personnel_bp.get('/get_soft_members')
@jwt_required()
def get_soft_members():
    try:
        leads = list(User_db.get_user_by_role(role = "Lead"))
        interns = list(User_db.get_user_by_role(role="Intern"))
        
        softlead = [{"id": lead['uid'], "name": lead['fullname']} for lead in leads if lead['stack'] == "Software"]
        softinterns = [{"id": intern['uid'], "name": intern['fullname']} for intern in interns if intern['stack'] == "Software"]
        
        response = {
        "members": softlead + softinterns,
        "status" : "success"
        } 
        return jsonify(convert_to_json_serializable(response)), 200
    except Exception as e:
        return jsonify({'message': f"Something went wrong: {e}", 'status': 'error'}), 500
    
@personnel_bp.get('/get_hard_members') #Personnel tab 
@jwt_required()
def get_hard_members():
    try:
        leads = list(User_db.get_user_by_role(role = "Lead"))
        interns = list(User_db.get_user_by_role(role="Intern"))
        
        hardlead = [{"id": lead['uid'], "name": lead['fullname']} for lead in leads if lead['stack'] == "Hardware"]
        hardinterns = [{"id": intern['uid'], "name": intern['fullname']} for intern in interns if intern['stack'] == "Hardware"]
        
        response = {
        "members": hardlead + hardinterns,
        "status" : "success"
        } 
        return jsonify(convert_to_json_serializable(response)), 200
    except Exception as e:
        return jsonify({'message': f"Something went wrong: {e}", 'status': 'error'}), 500
    
@personnel_bp.get('/get_all_members') #Personnel tab 
@jwt_required()
def get_all_members():
    try:
        leads = list(User_db.get_user_by_role("Lead"))
        interns = list(User_db.get_user_by_role("Intern"))
        
        leads = [{"id": lead['uid'], "name": lead['fullname']} for lead in leads]
        interns = [{"id": intern['uid'], "name": intern['fullname']} for intern in interns]
        
        response = {
        "members": leads +interns,
        "status" : "success"
        } 
        return jsonify(convert_to_json_serializable(response)), 200
    except Exception as e:
        return jsonify({'message': f"Something went wrong: {e}", 'status': 'error'}), 500

@personnel_bp.get('/get_all_members_and_admins') 
@jwt_required()
def get_all_leads_and_admins():
    try:
        admins = list(User_db.get_user_by_role("Admin"))
        leads = list(User_db.get_user_by_role("Lead"))
        
        admins = [{"id": admin['uid'], "name": admin['fullname']} for admin in admins]
        leads = [{"id": lead['uid'], "name": lead['fullname']} for lead in leads]
        
        response = {
        "members": admins + leads,
        "status" : "success"
        } 
        return jsonify(convert_to_json_serializable(response)), 200
    except Exception as e:
        return jsonify({'message': f"Something went wrong: {e}", 'status': 'error'}), 500

@personnel_bp.get('/personnel/get/<requested_uid>') 
def show_user_profile(requested_uid):
    try:
        requested_profile = User_db.get_user_by_uid(requested_uid)
        if not requested_profile:
            return jsonify({'message': 'Personnel not found', 'status': 'error'})
        
        response = {"requested_profile" : requested_profile, "status" : "success" }
        return jsonify(convert_to_json_serializable(response)), 200
    except Exception as e:  
        return jsonify({"message": f"Something went wrong: {e}", "status": "error"}), 500
    
@personnel_bp.post('/personnel/admin_create_user')
@jwt_required()
@admin_and_lead_role_required
def create_user():
    try:
        data = json.loads(request.form.get('info'))
        print(data)
        
        firstname =data.get("firstname")
        surname =data.get("lastname")
        stack =data.get("stack")
        niche =data.get("niche")
        role =data.get("role")
        phone_num =data.get("phone_num")
        email =data.get("email")
        mentor_id = "NIL"
        task_id = "NIL"
        bio =data.get("bio", "NIL")
        location = "NIL"
        bday =data.get("bday", "NIL")
        now = datetime.now().strftime
        month = now("%B")
        year =  now("%Y")
        datetime_created = "{0}, {1}".format(month, year)
        fullname = "{0} {1}".format(surname, firstname)
        pwd = generate.password()
        hashed_pwd = generate_password_hash(pwd)
        uid = generate.user_id(firstname)
        avatar_url = 'NIL'
        
        avatar = request.files.get("avatar", None)
        avatar_msg = ''
        if avatar :
            if not allowed_file(avatar.filename):
                return {'message': 'Invalid avatar file type', 'status': 'error'}, 400
            
            if len(avatar.read()) > 500 * 1024:
                return {'message': 'File size should not exceed 500KB', 'status': 'error'}, 400
            
            avatar.seek(0)
            
            try:
                upload_result = upload_func(avatar, 'SSRL_Lab_App/interns/profile_image')
                
                if not upload_result:
                    avatar_msg = "Avatar upload failed"
                    
                avatar_msg = ''
                avatar_url = {"secure_url": upload_result['secure_url'], "public_id": upload_result['public_id']}
                
            except Exception as e:
                return {'message': f'avatar upload failed: {str(e)}', 'status': 'error'}, 500
        
        
        user = User(firstname, surname, fullname, hashed_pwd, uid, stack, niche, role, phone_num, email, mentor_id, avatar_url, task_id, bio, location, bday, datetime_created)
        
        user_id= User_db.create_user(user)
        if not user_id:
            return jsonify({"message": "Unable to create user at the moment. Please try again", "status" : "danger"}), 500
        
        response = convert_to_json_serializable({"message" : f"user {uid} created successfully. {avatar_msg}", "user_id" : str(user_id), "status" : "success"})
        return jsonify(response)
        
    #     try:
    #         msg = Message('SSRL Login credentials', sender = 'covenantcrackslord03@gmail.com', recipients = [email])
    #         msg.body = f"Welcome to SSRL🤗 \nCheck out your login credentials below\n\nUnique I.D: {uid} \nPassword: {pwd}  \n\n\nFrom SSRL Team"
            
    #         mail.send(msg)
        
    #         response = convert_to_json_serializable({"message" : f"user {uid} created successfully", "user_id" : str(user_id), "status" : "success"})
            
    #         return jsonify(response), 200 # Show the created user's profile -> Fetch /show/profile/<requested_id>
    #     except Exception as e:
    #         print(e)
        
    except Exception as e:
        print(e)
        return jsonify({"message": f"Unable to create user at the moment! Please confirm that the inputed email is correct or check your internet connection. {e}", "status" : "danger"}), 500
    
@personnel_bp.get('/personnel/me')
@jwt_required()
def view_profile_me():
    try:
        uid = get_jwt_identity()
        user_profile = User_db.get_user_by_uid(uid)
        if not user_profile:
            return jsonify({'message': 'Profile not found', 'status': 'error'}), 404
        
        response = {"user_profile" : user_profile, "status" : "success"}
        return jsonify(convert_to_json_serializable(response)), 200 
    
    except Exception as e:
        return jsonify({'mes  sage': f"Something went wrong: {e}", 'status': 'error'}), 500

@personnel_bp.patch('/personnel/edit_profile') 
@jwt_required()
def user_edit_profile(): 
    try:
        uid = get_jwt_identity()
        data = json.loads(request.form.get('info'))
        avatar = request.files.get('avatar', 'NIL')
        avatar_msg = ''
        
        if avatar != 'NIL':  
            if not allowed_file(avatar.filename):
                return {'message': 'Invalid avatar file type', 'status': 'error'}, 400
            
            if len(avatar.read()) > 500 * 1024:
                return {'message': 'File size should not exceed 500KB', 'status': 'error'}, 400
            
            avatar.seek(0)
            
            try: 
                uploaded = upload_func(avatar, folder="smart_app/avatars")
                
                if not uploaded:
                    avatar_msg = "Could not upload image right now"
                else:
                    avatar = {'secure_url': uploaded["secure_url"], 'public_id': uploaded["public_id"]}
                    
            except Exception as e:
                print(e)
                
        data['avatar'] = avatar
        updated = User_db.update_user(uid, data)
    
        if not updated['success']:
            return jsonify({"message": f"{updated['error']}", "status" : "danger"}), 403
        
        return jsonify({"message": f"profile updated successfully {avatar_msg}", "status" : "success"}), 200
        
    except Exception as e:
        return jsonify({'message': f"Something went wrong: {e}", 'status': 'error'}), 500

@personnel_bp.patch('/personnel/admin_edit/<edit_id>')
@jwt_required()
@admin_and_lead_role_required
def admin_edit_profile(edit_id):
    try:
        data = json.loads(request.form.get('info'))
        
        firstname =data.get("firstname")
        surname =data.get("surname")
        avatar = request.files.get("avatar", 'NIL')
        print(avatar)
        data["fullname"] = "{0} {1}".format(surname, firstname)
        avatar_msg = ''
        
        edit_profile = User_db.get_user_by_uid(edit_id)
        if not edit_profile:
            return jsonify({"message": "User not found", "status": "error"}), 404
        
        if avatar != 'NIL':
            if not allowed_file(avatar.filename):
                return {'message': 'Invalid avatar file type', 'status': 'error'}, 400
            
            if len(avatar.read()) > 500 * 1024:
                return {'message': 'File size should not exceed 500KB', 'status': 'error'}, 400
            
            avatar.seek(0)
            
            try:
                upload_result = upload_func(avatar, 'SSRL_Lab_App/interns/profile_image')
                
                if not upload_result:
                    avatar_msg = "Avatar upload failed"
                else:
                    avatar_msg = ''
                    avatar = {"secure_url": upload_result['secure_url'], "public_id": upload_result['public_id']}
                    print(avatar)
                    
            except Exception as e:
                return {'message': f'avatar upload failed: {str(e)}', 'status': 'error'}, 500    
        
            data['avatar'] = avatar
            
        edited = User_db.update_user(edit_id, data)
        if not edited['success']:
            return jsonify({"message": f"Profile update unsuccessful: {edited['error']}", "status": "error"}), 500
        
        return jsonify({"message": f"Profile updated successfully. {avatar_msg}", "status": "success"}), 200
    
    except Exception as e:
        return jsonify({"message": f"Something went wrong: {e}", "status": "error"}), 500
    
     # try:
        #     msg = Message('SSRL Profile Updated', sender = 'covenantcrackslord03@gmail.com', recipients = [edit_profile["email"]])
        #     msg.body = f"Your profile has been updated\n Check out your new Id below below\n\nUnique I.D: {uid}\n\n\nFrom SSRL Team"
            
        #     mail.send(msg)
            
        #     updated = User_db.update_user_profile_by_oid(oid, dtls)
        #     if updated:
        #         flash("Profile updated successful!", "success")
        #         return redirect(url_for('show_user_profile', requested_id=edit_profile["_id"]))
        #     else:
        #         flash("profile update undsuccessful!", "danger")
        #         return redirect(url_for('view_members'))
        # except: 
        #     flash("Profile update unsuccessful! Please confirm that the inputed email address is correct and that you are connected to the internet.", "danger")
        #     return redirect(url_for('view_members'))
    
   
        
    # return jsonify({"message": "Something went wrong. Please try again", "status" : "danger"}), 500
            
@personnel_bp.patch('/add_lead/<intern_uid>') 
@jwt_required()
@admin_and_lead_role_required
def admin_add_lead(intern_uid):
    try:
        stack = User_db.get_user_by_uid(intern_uid)["stack"]
        dtls = {
            "role": "Lead"
        }
        updated = User_db.update_dtl(intern_uid, dtls)
        if updated:
            return jsonify({"message": f"You've successfully made {intern_uid} a {stack} Lead", "status" : "success"}), 200
        else:
            return jsonify({"message": "profile update unsuccessful","status" : "danger"}), 500
        
    except Exception as e:  
            return jsonify({"message": f"Something went wrong: {e}", "status": "error"}), 500
   
@personnel_bp.patch('/remove_lead/<intern_uid>') 
@jwt_required()
@admin_and_lead_role_required
def admin_remove_lead(intern_uid):
    try:
        stack = User_db.get_user_by_uid(intern_uid)["stack"]
        
        dtls = {
            "role": "Intern"
        }
        updated = User_db.update_dtl(intern_uid, dtls)
        if updated:
            return jsonify({"message": f"You've successfully removed {intern_uid} as {stack} lead", "status" : "success"}), 200
        else:
            return jsonify({"message": "profile update unsuccessful","status" : "danger"}), 500
    except Exception as e:  
        return jsonify({"message": f"Something went wrong: {e}", "status": "error"}), 500
    
@personnel_bp.patch('/add_admin/<intern_uid>') 
@jwt_required()
@admin_role_required
def admin_add_admin(intern_uid):
    try:
        dtls = {
            "role": "Admin"
        }
        updated = User_db.update_dtl(intern_uid, dtls)
        if updated:
            return jsonify({"message": f"You've successfully made {intern_uid} an Admin", "status" : "success"}), 200
        else:
            return jsonify({"message": "Profile update unsuccessful","status" : "danger"}), 500
    except Exception as e:  
        return jsonify({"message": f"Something went wrong: {e}", "status": "error"}), 500
        
@personnel_bp.patch('/remove_admin/<intern_uid>')
@jwt_required()
@admin_role_required
def admin_remove_admin(intern_uid):
    try:
        dtls = {
            "role": "Intern"
        }
        updated = User_db.update_dtl(intern_uid, dtls)
        if updated:
            return jsonify({"message": f"You've successfully removed {intern_uid} from an Admin", "status" : "success"}), 200
        else:
            return jsonify({"message": "Profile update unsuccessful","status" : "danger"}), 500
    except Exception as e:  
        return jsonify({"message": f"Something went wrong: {e}", "status": "error"}), 500

@personnel_bp.patch('/admin/delete_user/<requested_id>')
@jwt_required()
@admin_role_required
def admin_delete_user(requested_id):
    try:
        dtls = {"deleted": "True"}
        deleted = User_db.update_dtl(requested_id, dtls)
        
        if deleted:
            return jsonify({"message": f"User {requested_id} deleted successfully!", "status" : "success"}), 200
        else:
            return jsonify({"message": f"The request to delete {requested_id} was not successful!", "status" : "danger"}), 400
    except Exception as e:  
        return jsonify({"message": f"Something went wrong: {e}", "status": "error"}), 500
    
@personnel_bp.patch('/admin/suspend_user/<requested_id>')
@jwt_required()
@admin_role_required
def admin_suspend_user(requested_id):
    try:
        dtls = {"suspended": "True"}
        deleted = User_db.update_dtl(requested_id, dtls)

        if deleted:
            return jsonify({"message": f"User {requested_id} suspended successfully!", "status" : "success"}), 200
        else:
            return jsonify({"message": f"The request to suspend {requested_id} was not successful!", "status" : "danger"}), 400
    except Exception as e:  
        return jsonify({"message": f"Something went wrong: {e}", "status": "error"}), 500
    
@personnel_bp.patch('/admin/unsuspend_user/<requested_id>')
@jwt_required()
@admin_role_required
def admin_unsuspend_user(requested_id):
    try:
        dtls = {"suspended": "False"}
        deleted = User_db.update_dtl(requested_id, dtls)
        
        if deleted:
            return jsonify({"message": f"User {requested_id} unsuspended successfully!", "status" : "success"}), 200
        else:
            return jsonify({"message": f"The request to delunsuspend {requested_id} was not successful!", "status" : "danger"}), 400
    except Exception as e:  
        return jsonify({"message": f"Something went wrong: {e}", "status": "error"}), 500
