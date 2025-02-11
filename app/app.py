from flask import Flask, session, render_template, redirect, url_for, request, flash, send_file, jsonify
from flask_bcrypt import Bcrypt, check_password_hash, generate_password_hash
from flask_mail import Mail, Message
from flask_cors import CORS, cross_origin
from db.models import *
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename
from io import BytesIO
import os 
from properties import *
from cloudinary.uploader import upload
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_jwt
import json
from flask_mail import Message
from main import app
from app.extensions import mail

import urllib.request
from auth import authenticate_user_for_attendance, decrypt
from funcs import *

User_db = Userdb()
Notifications = Notificationsdb()
Eqpt_db = Eqptdb()
lost_eqpt_db = lost_eqptdb()
Inventory_db = Inventorydb()
Request_db = Requestdb()
Report_db = Reportdb()
Project_db = Projectdb()
Todos_db = Todosdb()
Attendance_db  = Attendancedb()
Attendance_db_v2  = Attendancedb_v2()
Sessions_db = Sessionsdb()

    
@app.before_request
def clean_up_sessions():
    Sessions_db.expire_sessions()
    Sessions_db.cleanup()
    
@app.get('/session/new/<old_session_id>') # Work on creating new session only if old session has expired
def get_new_session_id(old_session_id):
    session = Session()
    new_session_id = Sessions_db.create_session(session)
    
    if not new_session_id:
        return jsonify({"message": "Something went wrong, pls try logging in again", "status": "error"}), 500
    
    new_session_db = Sessions_db.get_session(new_session_id)
    new_session = {"session_id": new_session_id, "expired": new_session_db["expired"]}
    
    if old_session_id == 'new':
        response = convert_to_json_serializable({"new_session": new_session, "old_session": {}, "status": "success"})
        return jsonify(response), 200
    
    old_session_db = Sessions_db.get_session(old_session_id)
    
    if not old_session_db:
        old_session = {}
        response = convert_to_json_serializable({"new_session": new_session, "old_session": {}, "status": "success"})
        return jsonify(response), 200
    
    old_session = {"session_id": old_session_id, "expired": old_session_db["expired"]}
    
    response = convert_to_json_serializable({"new_session": new_session, "old_session": old_session, "status": "success"})
        
    return jsonify(response), 200

@app.get('/session/update')
def update_session():
    session_id = request.headers.get("Session_ID")
    if (not session_id):
        return jsonify({"status": "error", "message": "Invaid session id. Try logging in again."}), 401
    
    print(session_id)
    user_data = {"user_id": "444446"}
    session = Sessions_db.update_session(session_id, user_data)
    print(session)
    
    if not session:
        return jsonify({"status": "error", "message": "Something went wrong. Try logging in again."}), 500
    
    return jsonify({"status": "success"})

@app.get('/test')
@jwt_required()
def test():
    res = {"message" : "Test success"}
    return jsonify(res), 200

# @app.post('/login')
# def login():
#     user_uid = request.json.get("user_uid")
#     pwd = request.json.get("pwd")
#     user_profile = User_db.get_user_by_uid(user_uid)
    
#     if not user_profile:
#         return {"message": "Invalid login ID", "status" : "danger"}, 401
    
#     if user_profile["deleted"] == "True":
#         return jsonify({"message": "Could not find user with the inputted credentials.", "status": "error"}), 404
    
#     if user_profile["suspended"] == "True":
#         return jsonify({"message": "This account has been suspended. Please contact the admin or your stack lead.", "status": "error"}), 401
    
#     authenticated = check_password_hash(user_profile["hashed_pwd"], pwd)
#     if not authenticated:
#         return {"message": "Invalid password","status" : "danger"}, 401
        
#     user_profile = convert_to_json_serializable(user_profile)
    
#     extra_claims = {
#         "user_id": user_profile['_id'],
#         "user_role":  user_profile['role'],
#         "stack":  user_profile['stack']
#         }
    
#     access_token = create_access_token(identity=user_uid, additional_claims=extra_claims)
    
#     response = {
#         "message": f"Welcome! {user_profile['fullname']}",
#         "status" : "success",
#         "user_profile": user_profile,
#         "access_token": access_token
#     }
#     return response, 200
        
# @app.get('/logout')
# @cross_origin(supports_credentials=True)
# def logout():
#     session_id = request.headers.get("Session_ID")
#     user_data = check_session(session_id)
    
#     if user_data == False:
#         return jsonify({"message": "Something went wrong. Please try logging in again 1.", "status": "error"}), 401 
    
#     if "user_id" in user_data:
#         updated_session = Sessions_db.update_session(user_data={})
#         return jsonify({"message": "Logged out successfully", "status": "success"}), 200 # Return to login
#     else:
#         return jsonify({"message": "You are not logged in!", "status": "danger"}), 400

# @app.get('/forgot/password')
# @cross_origin(supports_credentials=True)
# def forgot_password():
#     session["confirmed"]="false" # To forgot password page
#     return jsonify({"status" : "success"})
    
# @app.post('/confirm/credentials')
# def confirm_credentials():
#     status = session.get("confirmed")
    
#     if not status:
#         uid = request.json.get("uid")
#         email = request.json.get("email")
#         user = User_db.get_user_by_uid(uid)
        
#         if user:
#             if user["email"]==email:
#                 otp = generate.OTP()
#                 try:
#                     msg = Message('SSRL password recovery', sender = 'covenantcrackslord03@gmail.com', recipients = [email])
#                     msg.body = f"Enter the OTP below into the required field \nThe OTP will expire in 24 hours\n\nOTP: {otp}  \n\n\nFrom SSRL Team"
                    
#                     mail.send(msg)
                    
#                     session["uid"]=uid
#                     session["otp"]=otp
#                     print(session["otp"])
                    
#                     response = {
#                         "message": "Check your email for the OTP",
#                         "otp": otp, #To confirm OTP page
#                         "status" : "success"
#                     }
#                     return jsonify(response), 200
#                 except Exception as exp:
#                     response = {
#                         "message": "Unable to recover your account at the moment! Please confirm that the input email is correct or check your internet connection.",
#                         "status": "danger",
#                         "error": str(exp)
#                     }
#                     return jsonify(response), 500
#             else:
#                 response = {
#                 "message": "Please confirm that the email is correct!",
#                 "status": "danger"
#             }
#             return jsonify(response), 403
#         else:
#             response = {
#                     "message": "Please confirm that your username is correct!",
#                     "status": "danger"
#                 }
#             return jsonify(response), 403
#     elif status == "true":
#         response = {
#             "message": "Already confirmed.",
#             "status": "info"
#         }
#         return jsonify(response), 400 # Back to login
    
# @app.post('/confirm/otp')
# def confirm_otp():
#     print(session.permanent)
#     status = session.get("confirmed")
    
#     if not status: 
#         print(str(session))
#         input_otp = request.json.get("otp")
#         otp = session.get("otp")
#         print(otp)
#         if input_otp == otp:
#             session.pop("otp", None)
#             session["confirmed"] = "true"
#             return jsonify({"message": "OTP confirmed. Proceed to change password.", "status" : "success"}), 200 # To change password
#         else:
#             return jsonify({"message": "Invalid OTP!", "status" : "danger"}), 401
#     elif status == "true":
#         return jsonify({"message": "Already confirmed." , "status" : "info"}), 401 # Back to login

# @app.post('/change/password')
# def change_password():
#     new_pwd = request.json.get("new_pwd")
    
#     # confirm_pwd = request.form.get("confirm_pwd") 
#     # if new_pwd == confirm_pwd: # Confirm in the frontend
    
#     try: 
#         uid = session.get("uid", None) 
#         hashed_pwd = generate_password_hash(new_pwd)
#         dtls = updatePwd(hashed_pwd)
#         updated = User_db.update_user_profile(uid, dtls)
            
#         if updated:
#             user_profile = User_db.get_user_by_uid(uid)
#             session["user_uid"] = uid
#             session["user_id"] = str(user_profile["_id"])
#             session["user_role"] = user_profile["role"]
#             session["stack"] = user_profile["stack"]
#             session.pop("uid", None)
#             fullname = user_profile['fullname']
#             response = {
#             "user_profile" : convert_to_json_serializable(user_profile),
#             "message": f"Password changed successfully! Welcome back {fullname}",
#             "status" : "success"
#             }
#             return jsonify(response), 200 # To homepage
#         else:
#             return jsonify({"message": "Unable to change your password! Try again", "status" : "danger"}), 500
#     except Exception as e:
#         print(e)
#         return jsonify({"message": f"Something went wrong! Please, try again", "status" : "danger"}), 500

# @app.get('/home')
# @jwt_required()
# def home():
#     try:
#         uid = get_jwt_identity()
        
#         user_profile = User_db.get_user_by_uid(uid)
#         if not user_profile:
#             return jsonify({"message": "User not found", "status": "error"}), 404
        
#         uid = user_profile["uid"]
#         user_role =user_profile["role"]
#         stack = user_profile["stack"]
#         firstname = user_profile["firstname"]
#         avatar = user_profile["avatar"]
#         todos = list(Todos_db.get_todos_by_user_id_limited(uid))
#         # all_todos = list(Todos_db.get_todos_by_user_id(user_id))
        
#         reports = list(Report_db.get_by_isMember_limited(uid))
#         requests = list(Request_db.get_by_isMember_limited(uid))
#         notifications = list(Notifications.get_by_isMember_limited(uid))
            
#         if user_role=="Admin":
#             projects = list(Project_db.get_all_limited())
#         elif user_role == "Lead":
#             projects = list(Project_db.get_by_stack_limited(stack))
#         else: projects = list(Project_db.get_by_isMember_limited(uid))
            
#         response = convert_to_json_serializable({"firstname" : firstname, "avatar" : avatar, "user_role": user_role, "stack": stack, "reports" : reports, "requests" : requests, "projects" : projects, "todos" : todos, "notifications": notifications, "status" : "success"})
            
#         return jsonify(response), 200
    
#     except Exception as e:
#         return jsonify({'message': f"Something went wrong: {e}", 'status': 'error'}), 500

# @app.get('/view/members') #Personnel tab 
# @jwt_required()
# def view_members():
#     try:
#         uid = get_jwt_identity()
#         user = User_db.get_user_by_uid(uid)
#         if not user:
#             return jsonify({'message': 'User not found', 'status': 'error'}), 404
        
        
#         admins = list(User_db.get_user_by_role(role = "Admin"))
#         leads = list(User_db.get_user_by_role(role = "Lead"))
#         interns = list(User_db.get_user_by_role(role="Intern"))
        
#         softlead = [lead for lead in leads if lead['stack'] == "Software"]
#         hardlead = [lead for lead in leads if lead['stack'] == "Hardware"]
#         softinterns = [intern for intern in interns if intern['stack'] == "Software"]
#         hardinterns = [intern for intern in interns if intern['stack'] == "Hardware"]
        
#         response = {
#         "admins" : admins,
#         "softleads": softlead,
#         "hardleads": hardlead,
#         "softinterns": softinterns,
#         "hardinterns": hardinterns,
#         "status" : "success"
#         } 
#         return jsonify(convert_to_json_serializable(response)), 200
#     except Exception as e:
#         return jsonify({'message': f"Something went wrong: {e}", 'status': 'error'}), 500
    
# @app.get('/get_soft_members') #Personnel tab 
# @jwt_required()
# def get_soft_members():
#     try:
#         leads = list(User_db.get_user_by_role(role = "Lead"))
#         interns = list(User_db.get_user_by_role(role="Intern"))
        
#         softlead = [{"id": lead['uid'], "name": lead['fullname']} for lead in leads if lead['stack'] == "Software"]
#         softinterns = [{"id": intern['uid'], "name": intern['fullname']} for intern in interns if intern['stack'] == "Software"]
        
#         response = {
#         "members": softlead + softinterns,
#         "status" : "success"
#         } 
#         return jsonify(convert_to_json_serializable(response)), 200
#     except Exception as e:
#         return jsonify({'message': f"Something went wrong: {e}", 'status': 'error'}), 500
    
# @app.get('/get_hard_members') #Personnel tab 
# @jwt_required()
# def get_hard_members():
#     try:
#         leads = list(User_db.get_user_by_role(role = "Lead"))
#         interns = list(User_db.get_user_by_role(role="Intern"))
        
#         hardlead = [{"id": lead['uid'], "name": lead['fullname']} for lead in leads if lead['stack'] == "Hardware"]
#         hardinterns = [{"id": intern['uid'], "name": intern['fullname']} for intern in interns if intern['stack'] == "Hardware"]
        
#         response = {
#         "members": hardlead + hardinterns,
#         "status" : "success"
#         } 
#         return jsonify(convert_to_json_serializable(response)), 200
#     except Exception as e:
#         return jsonify({'message': f"Something went wrong: {e}", 'status': 'error'}), 500

# @app.get('/personnel/get/<requested_uid>') #user ID created by database
# def show_user_profile(requested_uid):
#     try:
#         requested_profile = User_db.get_user_by_uid(requested_uid)
        
#         response = {"requested_profile" : requested_profile, "status" : "success" }
#         return jsonify(convert_to_json_serializable(response)), 200
#     except Exception as e:  
#         return jsonify({"message": f"Something went wrong: {e}", "status": "error"}), 500
    
# @app.post('/personnel/admin_create_user')
# @jwt_required()
# @admin_and_lead_role_required
# def create_user():
#     try:
#         data = json.loads(request.form.get('info'))
#         print(data)
#         firstname =data.get("firstname")
#         surname =data.get("lastname")
#         stack =data.get("stack")
#         niche =data.get("niche")
#         role =data.get("role")
#         phone_num =data.get("phone_num")
#         email =data.get("email")
#         mentor_id = "NIL"
#         task_id = "NIL"
#         bio =data.get("bio", "NIL")
#         location = "NIL"
#         bday =data.get("bday", "NIL")
#         now = datetime.now().strftime
#         month = now("%B")
#         year =  now("%Y")
#         datetime_created = "{0}, {1}".format(month, year)
#         fullname = "{0} {1}".format(surname, firstname)
#         pwd = generate.password()
#         hashed_pwd = generate_password_hash(pwd)
#         uid = generate.user_id(firstname)
#         avatar_url = 'NIL'
        
#         avatar = request.files.get("avatar", None)
#         avatar_msg = ''
#         if avatar :
#             if not allowed_file(avatar.filename):
#                 return {'message': 'Invalid avatar file type', 'status': 'error'}, 400
            
#             if len(avatar.read()) > 500 * 1024:
#                 return {'message': 'File size should not exceed 500KB', 'status': 'error'}, 400
            
#             avatar.seek(0)
            
#             try:
#                 upload_result = upload_func(avatar, 'SSRL_Lab_App/interns/profile_image')
                
#                 if not upload_result:
#                     avatar_msg = "Avatar upload failed"
                    
#                 avatar_msg = ''
#                 avatar_url = {"secure_url": upload_result['secure_url'], "public_id": upload_result['public_id']}
                
#             except Exception as e:
#                 return {'message': f'avatar upload failed: {str(e)}', 'status': 'error'}, 500
        
        
#         user = User(firstname, surname, fullname, hashed_pwd, uid, stack, niche, role, phone_num, email, mentor_id, avatar_url, task_id, bio, location, bday, datetime_created)
        
#         user_id= User_db.create_user(user)
#         if not user_id:
#             return jsonify({"message": "Unable to create user at the moment. Please try again", "status" : "danger"}), 500
        
#         try:
#             msg = Message('SSRL Login credentials', sender = 'covenantcrackslord03@gmail.com', recipients = [email])
#             msg.body = f"Welcome to SSRL🤗 \nCheck out your login credentials below\n\nUnique I.D: {uid} \nPassword: {pwd}  \n\n\nFrom SSRL Team"
            
#             mail.send(msg)
        
#             response = convert_to_json_serializable({"message" : f"user {uid} created successfully", "user_id" : str(user_id), "status" : "success"})
            
#             return jsonify(response), 200 # Show the created user's profile -> Fetch /show/profile/<requested_id>
#         except Exception as e:
#             print(e)
        
#         response = convert_to_json_serializable({"message" : f"user {uid} created successfully. {avatar_msg}", "user_id" : str(user_id), "status" : "success"})
#         return jsonify(response)
        
#     except Exception as e:
#         print(e)
#         return jsonify({"message": f"Unable to create user at the moment! Please confirm that the inputed email is correct or check your internet connection. {e}", "status" : "danger"}), 500
    
# @app.get('/view/profile/me')
# def view_profile_me():
#     session_id = request.headers.get("Session_ID")
#     user_data = check_session(session_id)
    
#     if user_data == False:
#         return jsonify({"message": "Something went wrong. Please try logging in again 1.", "status": "error"}), 401 
    
#     if "user_id" in user_data:
#         user_id = user_data["user_id"]
#         user_profile = User_db.get_user_by_oid(user_id)
#         response = {"user_profile" : user_profile, "status" : "success"}
#         return jsonify(convert_to_json_serializable(response)), 200 
#     else:
#         return jsonify({"message": "You are not logged in", "status" : "info"}), 403 #To login page

# @app.patch('/user/edit/profile') #Send defaultvalues with request body
# def user_edit_profile(): 
#     if "user_id" in session:
#         user_id = session["user_id"]
        
#         if 'avatar' not in request.files: avatar = None
#         else: avatar = request.files['avatar']
        
#         phone_num = request.json.get("phone_num")
#         bio = request.json.get("bio")
#         location = request.json.get("location")
#         bday = request.json.get("bday")
#         email = request.json.get("email")
#         if avatar and AllowedExtension.images(secure_filename(avatar.filename)):
#             try: 
#                 uploaded = upload(avatar, folder="smart_app/avatars", resource_type="image")
#                 app.logger.info(uploaded)
#                 if "secure_url" in uploaded:
#                     filename = uploaded["secure_url"]
#                     dtls = {filename, phone_num, bio, location, bday, email}
                    
#                     updated = User_db.update_user_profile_by_oid(user_id, dtls)
                
#                     if updated:
#                         return jsonify({"message": "profile updated successfully", "status" : "success"}), 200
#                     else:
#                         return jsonify({"message": "profile updated unsuccessful", "status" : "danger"}), 403
#                 else:
#                     return jsonify({"message": "profile updated unsuccessful", "status" : "danger"}), 403
#             except:
#                 return jsonify({"message": "image upload error!", "status" : "danger"}), 500
#         else:
#             user_profile = User_db.get_user_by_oid(user_id)
#             filename = user_profile["avatar"]
#             dtls = {filename, phone_num, bio, location, bday, email}
            
#             updated = User_db.update_user_profile_by_oid(user_id, dtls)
            
#             if updated:
#                 return jsonify({"message": "profile updated successfully", "status" : "success"}), 200
#             else:
#                 return jsonify({"message": "profile updated unsuccessful", "status" : "danger"}), 403
#     else:
#         return jsonify({"message": "You are not logged in", "status" : "info"}), 403 #To login page

# @app.patch('/personnel/admin_edit/<edit_id>')
# @jwt_required()
# @admin_and_lead_role_required
# def admin_edit_profile(edit_id):
#     try:
#         data = json.loads(request.form.get('info'))
#         print(data)
        
#         firstname =data.get("firstname")
#         surname =data.get("surname")
#         avatar = request.files.get("avatar")
#         print(avatar)
#         data["fullname"] = "{0} {1}".format(surname, firstname)
#         avatar_msg = ''
        
#         edit_profile = User_db.get_user_by_uid(edit_id)
#         if not edit_profile:
#             return jsonify({"message": "User not found", "status": "error"}), 404
        
#         if avatar:
#             if not allowed_file(avatar.filename):
#                 return {'message': 'Invalid avatar file type', 'status': 'error'}, 400
            
#             if len(avatar.read()) > 500 * 1024:
#                 return {'message': 'File size should not exceed 500KB', 'status': 'error'}, 400
            
#             avatar.seek(0)
            
#             try:
#                 upload_result = upload_func(avatar, 'SSRL_Lab_App/interns/profile_image')
                
#                 if not upload_result:
#                     avatar_msg = "Avatar upload failed"
                    
#                 avatar_msg = ''
#                 avatar_url = {"secure_url": upload_result['secure_url'], "public_id": upload_result['public_id']}
#                 print(avatar_url)
#                 data['avatar'] = avatar_url
                
#             except Exception as e:
#                 return {'message': f'avatar upload failed: {str(e)}', 'status': 'error'}, 500    
        
#         edited = User_db.update_user(edit_id, data)
#         if not edited['success']:
#             return jsonify({"message": f"Profile update unsuccessful: {edited['error']}", "status": "error"}), 500
        
#         return jsonify({"message": f"Profile updated successfully. {avatar_msg}", "status": "success"}), 200
    
#     except Exception as e:
#         return jsonify({"message": f"Something went wrong: {e}", "status": "error"}), 500
    
#      # try:
#         #     msg = Message('SSRL Profile Updated', sender = 'covenantcrackslord03@gmail.com', recipients = [edit_profile["email"]])
#         #     msg.body = f"Your profile has been updated\n Check out your new Id below below\n\nUnique I.D: {uid}\n\n\nFrom SSRL Team"
            
#         #     mail.send(msg)
            
#         #     updated = User_db.update_user_profile_by_oid(oid, dtls)
#         #     if updated:
#         #         flash("Profile updated successful!", "success")
#         #         return redirect(url_for('show_user_profile', requested_id=edit_profile["_id"]))
#         #     else:
#         #         flash("profile update undsuccessful!", "danger")
#         #         return redirect(url_for('view_members'))
#         # except: 
#         #     flash("Profile update unsuccessful! Please confirm that the inputed email address is correct and that you are connected to the internet.", "danger")
#         #     return redirect(url_for('view_members'))
    
   
        
#     # return jsonify({"message": "Something went wrong. Please try again", "status" : "danger"}), 500
            
# @app.patch('/add_lead/<intern_uid>') 
# @jwt_required()
# @admin_and_lead_role_required
# def admin_add_lead(intern_uid):
#     try:
#         stack = User_db.get_user_by_uid(intern_uid)["stack"]
#         dtls = {
#             "role": "Lead"
#         }
#         updated = User_db.update_dtl(intern_uid, dtls)
#         if updated:
#             return jsonify({"message": f"You've successfully made {intern_uid} a {stack} Lead", "status" : "success"}), 200
#         else:
#             return jsonify({"message": "profile update unsuccessful","status" : "danger"}), 500
        
#     except Exception as e:  
#             return jsonify({"message": f"Something went wrong: {e}", "status": "error"}), 500
   
# @app.patch('/remove_lead/<intern_uid>') 
# @jwt_required()
# @admin_and_lead_role_required
# def admin_remove_lead(intern_uid):
#     try:
#         stack = User_db.get_user_by_uid(intern_uid)["stack"]
        
#         dtls = {
#             "role": "Intern"
#         }
#         updated = User_db.update_dtl(intern_uid, dtls)
#         if updated:
#             return jsonify({"message": f"You've successfully removed {intern_uid} as {stack} lead", "status" : "success"}), 200
#         else:
#             return jsonify({"message": "profile update unsuccessful","status" : "danger"}), 500
#     except Exception as e:  
#         return jsonify({"message": f"Something went wrong: {e}", "status": "error"}), 500
    
# @app.patch('/add_admin/<intern_uid>') 
# @jwt_required()
# @admin_role_required
# def admin_add_admin(intern_uid):
#     try:
#         dtls = {
#             "role": "Admin"
#         }
#         updated = User_db.update_dtl(intern_uid, dtls)
#         if updated:
#             return jsonify({"message": f"You've successfully made {intern_uid} an Admin", "status" : "success"}), 200
#         else:
#             return jsonify({"message": "Profile update unsuccessful","status" : "danger"}), 500
#     except Exception as e:  
#         return jsonify({"message": f"Something went wrong: {e}", "status": "error"}), 500
        
# @app.patch('/remove_admin/<intern_uid>')
# @jwt_required()
# @admin_role_required
# def admin_remove_admin(intern_uid):
#     try:
#         dtls = {
#             "role": "Intern"
#         }
#         updated = User_db.update_dtl(intern_uid, dtls)
#         if updated:
#             return jsonify({"message": f"You've successfully removed {intern_uid} from an Admin", "status" : "success"}), 200
#         else:
#             return jsonify({"message": "Profile update unsuccessful","status" : "danger"}), 500
#     except Exception as e:  
#         return jsonify({"message": f"Something went wrong: {e}", "status": "error"}), 500

# @app.patch('/admin/delete_user/<requested_id>')
# @jwt_required()
# @admin_role_required
# def admin_delete_user(requested_id):
#     try:
#         dtls = {"deleted": "True"}
#         deleted = User_db.update_dtl(requested_id, dtls)
        
#         if deleted:
#             return jsonify({"message": f"User {requested_id} deleted successfully!", "status" : "success"}), 200
#         else:
#             return jsonify({"message": f"The request to delete {requested_id} was not successful!", "status" : "danger"}), 400
#     except Exception as e:  
#         return jsonify({"message": f"Something went wrong: {e}", "status": "error"}), 500
    
# @app.patch('/admin/suspend_user/<requested_id>')
# @jwt_required()
# @admin_role_required
# def admin_suspend_user(requested_id):
#     try:
#         dtls = {"suspended": "True"}
#         deleted = User_db.update_dtl(requested_id, dtls)

#         if deleted:
#             return jsonify({"message": f"User {requested_id} suspended successfully!", "status" : "success"}), 200
#         else:
#             return jsonify({"message": f"The request to suspend {requested_id} was not successful!", "status" : "danger"}), 400
#     except Exception as e:  
#         return jsonify({"message": f"Something went wrong: {e}", "status": "error"}), 500
    
# @app.patch('/admin/unsuspend_user/<requested_id>')
# @jwt_required()
# @admin_role_required
# def admin_unsuspend_user(requested_id):
#     try:
#         dtls = {"suspended": "False"}
#         deleted = User_db.update_dtl(requested_id, dtls)
        
#         if deleted:
#             return jsonify({"message": f"User {requested_id} unsuspended successfully!", "status" : "success"}), 200
#         else:
#             return jsonify({"message": f"The request to delunsuspend {requested_id} was not successful!", "status" : "danger"}), 400
#     except Exception as e:  
#         return jsonify({"message": f"Something went wrong: {e}", "status": "error"}), 500
    
@app.get('/view/equipments')
def view_all_eqpt():
    if "user_id" in session:
        user_id = session["user_id"]
        user_role = session["user_role"]
        stack = session["stack"]
        user_profile = User_db.get_user_by_oid(user_id)
        
        if user_role=="Admin" or (user_role =="Lead" and stack =="Hardware"):
            equipments = list(Eqpt_db.get_all_eqpt())
            interns = User_db.get_all_users(), 
            lost_eqpts = lost_eqpt_db.get_all()
            availables = Eqpt_db.get_all_available_eqpt()
            inventory = list(Inventory_db.get_all())
            
            return jsonify({equipments:equipments, lost_eqpts:lost_eqpts, interns:interns, availables:availables, inventory:inventory, "status" : "success"})

        else:
            return jsonify({"message": "Unauthorized actiom. Please contact the admin.", "status" : "info"}), 401   
    else:
        # flash  ('you are not logged in!', "danger")
        # return redirect(url_for('login'))
        return jsonify({"message": "You are not logged in", "status" : "info"}), 403 #To login page

@app.get('/view/equipments/<eqpt_id>')        
def view_eqpt_dtls(eqpt_id):
    
    if "user_uid" in session:
        user_id = session["user_id"]
        user_role = session["user_role"]
        stack = session["stack"]
        user_profile = User_db.get_user_by_oid(user_id)
        
        if user_role=="Admin" or (user_role =="Lead" and stack =="Hardware"):
            eqpt_dtls = Eqpt_db.get_eqpt_by_id(eqpt_id)
            
            # return render_template('pages/view_equipment.html', user_profile=user_profile, eqpt_dtls=eqpt_dtls)
            return jsonify({ eqpt_dtls:eqpt_dtls, "status" : "success"})
        else:
            # flash('permission not granted', "danger")
            # return redirect(url_for('login'))   
            return jsonify({"message" : 'permission not granted', "status" : "info"})         
    else:
        # flash  ('you are not logged in!', "danger")
        # return redirect(url_for('login'))
        return jsonify({"message" : 'You are not logged in!', "status" : "info"})
    
@app.post('/equipment/new')
def eqpt_new_input():
   
    if "user_id" in session:
        user_role = session["user_role"]
        stack = session["stack"]
    
        if user_role=="Admin" or (user_role =="Lead" and stack == "Hardware"):
         
            Name = request.form.get("name")
            quantity = request.form.get("quantity")
            description = request.form.get("description")
            date_of_arrival = request.form.get("arrival")
            type = request.form.get("type")
            status = "available"
            now = datetime.now().strftime
            month = now("%B")
            date = now("%d")
            year = now("%Y")
            datetime_inputed = "{0} {1}, {2}".format(month, date, year)
            date_inserted = now("%x")
        
            dtls = Eqpt(Name, quantity, description, date_of_arrival, type, status, datetime_inputed, date_inserted)
            
            eqpt_id = Eqpt_db.new_input(dtls)
            if eqpt_id:
                name = {
                    "name": Name,
                    "id": eqpt_id
                }
                dtls = Eqpt(Name, quantity, description, date_of_arrival, type, status, datetime_inputed, date_inserted)
                Inventory_db.insert_new(dtls)
            
                # flash (f"Equipment {name} inputed successfully!", "success")
                # return redirect(url_for('view_eqpt_dtls', eqpt_id=eqpt_id))
                return jsonify({"message" : f"Equipment {name} inputed successfully!", eqpt_id : eqpt_id, "status" : "success"}) #What is eqpt_id needed for?
            else:
                # flash('An error occured!try again', 'danger')
                # return redirect(url_for('view_all_eqpt'))
                return jsonify({"message" : 'An error occured! Try again', "status" : "danger"})
        else:
            # flash('permission not granted', "danger")
            # return redirect(url_for('login')) 
            return jsonify({"message" : 'permission not granted', "status" : "info"})           
    else:
        # flash  ('you are not logged in!', "danger")
        # return redirect(url_for('login'))
        return jsonify({"message" : 'You are not logged in!', "status" : "info"})        
    
@app.post('/equipment/existing/input')
def eqpt_existing_input():
    
    if "user_id" in session:
        user_role = session["user_role"]
        stack = session["stack"]
        
        if user_role=="Admin" or (user_role =="Lead" and stack == "Hardware"):
         
            eqpt_id = request.form.get("eqpt_id")
            added_quantity = request.form.get("quantity")
            eqpt = Eqpt_db.get_eqpt_by_id(eqpt_id)
            name = {
                "name": eqpt["name"],
                "id" : eqpt_id
                
            }
            existing_quantity = eqpt["quantity"]
            quantity = int(added_quantity) + int(existing_quantity)
            description = eqpt["description"]
            date_of_arrival = request.form.get("arrival")
            type = eqpt["type"]
            status = "available"
            now = datetime.now().strftime
            month = now("%B")
            date = now("%d")
            year = now("%Y")
            datetime_inputed = "{0} {1}, {2}".format(month, date, year)
            date_inserted = now("%x")
        
            dtls = existEqpt(quantity, datetime_inputed, status)
            
            updated = Eqpt_db.update_eqpt_dtls(eqpt_id, dtls)
            
            if updated:
                dtls = Eqpt(name, added_quantity, description, date_of_arrival, type, status, datetime_inputed, date_inserted)
                Inventory_db.insert_new(dtls)
                # flash (f"Equipment inputed successfully!", "success")
                # return redirect(url_for('view_eqpt_dtls', eqpt_id=eqpt_id))
                return jsonify({"message" : f"Equipment inputed successfully!", eqpt_id : eqpt_id, "status" : "success"}) #What is eqpt_id needed for?

            else:
                # flash('An error occured!try again', 'danger')
                # return redirect(url_for('view_all_eqpt'))
                return jsonify({"message" : 'An error occured! Try again', "status" : "danger"})
        else:
            # flash('permission not granted', "danger")
            # return redirect(url_for('login'))  
            return jsonify({"message" : 'permission not granted', "status" : "info"})                             
    else:
        # flash  ('you are not logged in!', "danger")
        # return redirect(url_for('login'))
        return jsonify({"message" : 'You are not logged in!', "status" : "info"})                
    
@app.post('/equipment/update/<eqpt_id>')
def update_eqpt_dtls(eqpt_id):
    
    if "user_id" in session:
        user_role = session["user_role"]
        stack = session["stack"]
        
        if user_role=="Admin" or (user_role =="Lead" and stack =="Hardware"):
            name = request.form.get("name")
            quantity = request.form.get("quantity")
            description = request.form.get("description")
            date_of_arrival = request.form.get("arrival")
            type = request.form.get("type")
            status = request.form.get("status")
            datetime_inputed = request.form.get("date_inputed")
            now = datetime.now()
            month = now("%B")
            date = now("%d")
            year = now("%Y")
            date_updated = "{0} {1}, {2}".format(month, date, year)

            dtls = Eqpt(name, quantity, description, date_of_arrival, type, status, datetime_inputed, date_updated)
            
            updated = Eqpt_db.update_eqpt_dtls(eqpt_id, dtls)
            if updated:
                # flash(f"{name} details updated successfully!", "success")
                # return redirect(url_for('view_eqpt_dtls'), eqpt_id)
                return jsonify({"message" : f"{name} details successfully!", eqpt_id : eqpt_id, "status" : "success"}) #What is eqpt_id needed for?
                
            else:
                # flash("The request was unsuccessful!", "danger")
                # return redirect(url_for('view_eqpt_dtls'), eqpt_id)
                return jsonify({"message" : "The request was unsuccessful!", "status" : "danger"})                                   
        else:
            # flash('permission not granted', "danger")
            # return redirect(url_for('login'))  
            return jsonify({"message" : 'permission not granted', "status" : "info"})                                                   
    else:
        # flash  ('you are not logged in!', "danger")
        # return redirect(url_for('login')) 
         return jsonify({"message" : 'You are not logged in!', "status" : "info"})        
    
@app.get('/delete/equipment/<eqpt_id>')
def delete_eqpt(eqpt_id):
    
    if "user_id" in session:
        user_role = session["user_role"]
        stack = session["stack"]
        
        if user_role=="Admin" or (user_role =="Lead" and stack =="Hardware"):
            
            deleted = Eqpt_db.delete_existing_eqpt(eqpt_id)
            
            if deleted:
                # flash ("Equipment deleted successfully!", "success")
                # return redirect(url_for('view_all_eqpt'))
                return jsonify({"message" : "Equipment deleted successfully!", "status" : "success"})
            else:
                # flash("The request was unsuccessful!", "danger")
                # return redirect(url_for('view_eqpt_dtls'), eqpt_id)
                return jsonify({"message" : "The request was unsuccessful!", "status" : "danger"})      
        else:
            # flash('permission not granted', "danger")
            # return redirect(url_for('login'))  
            return jsonify({"message" : 'permission not granted', "status" : "info"})                                                   
    else:
        # flash  ('you are not logged in!', "danger")
        # return redirect(url_for('login')) 
         return jsonify({"message" : 'You are not logged in!', "status" : "info"})  
    
@app.post('/lost/equiment')
def lost_eqpt():
    
    if "user_id" in session:
        user_role = session["user_role"]
        stack = session["stack"]
        
        if user_role=="Admin" or (user_role =="Lead" and stack == "Hardware"):
            eqpt_id = request.form.get("id")
            eqpt = Eqpt_db.get_eqpt_by_id(eqpt_id)
            name = eqpt["name"]
            type = eqpt["type"]
            old_quant = int(eqpt["quantity"])
            quantity = request.form.get("quantity")
            personnel_id = request.form.get("person_resp")
            status = request.form.get("status")
            now = datetime.now().strftime
            month = now("%B")
            date = now("%d")
            year = now("%Y")
            date_reported = "{0} {1}, {2}".format(month, date, year)
            date_edited = ""
            
            dtls = lostEqpt(eqpt_id, name, type, quantity, personnel_id, status, date_reported, date_edited)
            lost_id = lost_eqpt_db.new_input(dtls)
            
            curr_quantity1 = old_quant - int(quantity)
            if curr_quantity1 > 1 :
                availability = "available"
                curr_quantity = curr_quantity1
            else:
                availability = "unavailable"
                curr_quantity = "0"
                
           
            _quantity = curr_quantity
            _status = availability

            dtls = Available(_quantity, _status)
            
            Eqpt_db.update_eqpt_dtls(eqpt_id, dtls)
            
            # flash (f"Equipment {name} recorded {status} successfully!", "success")
            # return redirect(url_for('view_lost_eqpt_dtls', eqpt_id=lost_id))
            return jsonify({"message" : f"Equipment {name} recorded {status} successfully!", eqpt_id : lost_id, "status" : "success"})
        else:
            # flash('permission not granted', "danger")
            # return redirect(url_for('login'))  
            return jsonify({"message" : 'permission not granted', "status" : "info"})                                                   
    else:
        # flash  ('you are not logged in!', "danger")
        # return redirect(url_for('login')) 
         return jsonify({"message" : 'You are not logged in!', "status" : "info"})   
    
@app.get('/view/lost/equipment/<eqpt_id>')        
def view_lost_eqpt_dtls(eqpt_id):
    
    if "user_id" in session:
        user_id = session["user_id"]
        user_role = session["user_role"]
        stack = session["stack"]
        user_profile = User_db.get_user_by_oid(user_id)
        
        if user_role=="Admin" or (user_role =="Lead" and stack =="Hardware"):
            eqpt_dtls = lost_eqpt_db.get_eqpt_by_id(eqpt_id)
            interns = User_db.get_all_users()
            
            # return render_template('pages/lost_equipment.html', user_profile=user_profile, eqpt_dtls=eqpt_dtls, interns=interns)
            return jsonify({user_profile:user_profile, eqpt_dtls:eqpt_dtls, interns:interns, "status" : "success"})
        else:
            # flash('permission not granted', "danger")
            # return redirect(url_for('login'))  
            return jsonify({"message" : 'permission not granted', "status" : "info"})                                                   
    else:
        # flash  ('you are not logged in!', "danger")
        # return redirect(url_for('login')) 
         return jsonify({"message" : 'You are not logged in!', "status" : "info"}) 
    
@app.post('/edit/lost/equiment/<eqpt_id>')
def edit_lost_eqpt(eqpt_id):
    
    if "user_id" in session:
        user_role = session["user_role"]
        stack = session["stack"]
        
        if user_role=="Admin" or (user_role =="Lead" and stack == "Hardware"):
            name = request.form.get("name")
            type = request.form.get("type")
            quantity = request.form.get("quantity")
            personnel_id = request.form.get("person_resp")
            status = request.form.get("status")
            date_reported = request.form.get("date_reported")
            now = datetime.now().strftime
            month = now("%B")
            date = now("%d")
            year = now("%Y")
            date_edited = "{0} {1}, {2}".format(month, date, year)
            
            dtls = lostEqpt(eqpt_id, name, type, quantity, personnel_id, status, date_reported, date_edited)
            updated = lost_eqpt_db.update_eqpt_dtls(eqpt_id, dtls)

            if updated:
                # flash ("Report details edited successfully!", "success")
                # return redirect(url_for('view_lost_eqpt_dtls', eqpt_id))
                return jsonify({"message" : "Report details edited successfully!", "status" : "success"}) 
            else:
                # flash ("Report details edit unsuccessfully!", "danger")
                # return redirect(url_for('view_lost_eqpt_dtls', eqpt_id))
                return jsonify({"message" : "Report details edited unsuccessfully!", "status" : "danger"})
        else:
            # flash('permission not granted', "danger")
            # return redirect(url_for('login'))  
            return jsonify({"message" : 'permission not granted', "status" : "info"})                                                   
    else:
        # flash  ('you are not logged in!', "danger")
        # return redirect(url_for('login')) 
         return jsonify({"message" : 'You are not logged in!', "status" : "info"})   

    
@app.get('/delete/lost/equipment/<eqpt_id>')
def delete_lost_eqpt(eqpt_id):

    if "user_id" in session:
        user_role = session["user_role"]
        stack = session["stack"]
        
        if user_role=="Admin" or (user_role =="Lead" and stack =="Hardware"):
            
            deleted = lost_eqpt_db.delete_lost_eqpt(eqpt_id)
            
            if deleted:
                # flash ("Equipment deleted successfully!", "success")
                # return redirect(url_for('view_all_eqpt'))
                return jsonify({"message" : "Equipment deleted successfully!", "status" : "success"})             
            else:
                # flash ('The request was unsuccessful!', "danger")
                # return redirect(url_for('view_eqpt_dtls', eqpt_id=eqpt_id))
                return jsonify({"message" : 'The request was unsuccessful!', "status" : "danger"})             
        else:
            # flash('permission not granted', "danger")
            # return redirect(url_for('login'))  
            return jsonify({"message" : 'permission not granted', "status" : "info"})                                                   
    else:
        # flash  ('you are not logged in!', "danger")
        # return redirect(url_for('login')) 
         return jsonify({"message" : 'You are not logged in!', "status" : "info"}) 
            
@app.post('/update/email')
def update_email():
    if "user_id" in session:
        id = session["user_id"]
        
        pwd = request.form.get("pwd")
        new_email = request.form.get("new_email")
        confirm_email = request.form.get("confirm_email")
        user_profile = User_db.get_user_by_oid(id)
        
        authenticated = check_password_hash(user_profile["hashed_pwd"], pwd)
        
        if authenticated:
            if new_email == confirm_email:
                dtls = updateEmail(new_email)
                updated = User_db.update_user_profile_by_oid(id, dtls)
                
                if updated:
                    return jsonify({"message" : "Email address updated successfully!", "status" : "success"})                    
                else:
                    return jsonify({"message" :"Unable to update your email address! Try again", "status" : "danger"})                    
            else:
                return jsonify({"message" :"Unmatching email address! Unable to update email address", "status" : "danger"})                    
        else:
            return jsonify({"message" : "Invalid password", "status" : "danger"})                    
    else:
         return jsonify({"message" : 'You are not logged in!', "status" : "info"}) 

@app.post('/update/password')
def update_password():
    if "user_id" in session:
        id = session["user_id"]
        
        old_pwd = request.form.get("old_pwd")
        new_pwd = request.form.get("new_pwd")
        confirm_pwd = request.form.get("confirm_pwd")
        
        user_profile = User_db.get_user_by_oid(id)
        
        authenticated = check_password_hash(user_profile["hashed_pwd"], old_pwd)
        
        if authenticated:
            if new_pwd == confirm_pwd:
                hashed_pwd = generate_password_hash(new_pwd)
                dtls = updatePwd(hashed_pwd)
                updated = User_db.update_user_profile_by_oid(id, dtls)
                
                if updated:
                    # flash("Password updated successfully!", "success")
                    # return redirect(url_for('view_profile_me'))
                    return jsonify({"message" : "Password updated successfully!", "status" : "success"})
                else:
                    # flash("Unable to change your password! Try again", "danger")
                    # return redirect(url_for('view_profile_me')) 
                    return jsonify({"message" :"Unable to change your password! Try again", "status" : "danger"})                    
            else:
                # flash("Unmatching password input! Unable to update your password", "danger")
                # return redirect(url_for('view_profile_me'))
                return jsonify({"message" :"Unmatching password input! Unable to update your password", "status" : "danger"})                    
        else:
            # flash("Invalid password", "danger")
            # return redirect(url_for('view_profile_me'))
            return jsonify({"message" : "Invalid password", "status" : "danger"})                    
    else:
        # flash  ('you are not logged in!', "danger")
        # return redirect(url_for('login')) 
         return jsonify({"message" : 'You are not logged in!', "status" : "info"}) 
 

@app.get('/submissions/forms/request')
def get_request_form():
    
    if "user_id" in session:
        user_id = session["user_id"]
        
        eqpts = Eqpt_db.get_all_eqpt()
        user_profile = User_db.get_user_by_oid(user_id)
        # return render_template('forms/request_form.html', eqpts=eqpts, user_profile=user_profile)
        return jsonify({eqpts:eqpts, user_profile:user_profile, "status" : "success"})
    else:
        # flash  ('you are not logged in!', "danger")
        # return redirect(url_for('login')) 
         return jsonify({"message" : 'You are not logged in!', "status" : "info"}) 
    
    
@app.get('/all/submissions')
def all_submissions():
    
    if "user_id" in session:
        role = session["user_role"]
        _id = session["user_id"]
        uid = session["user_uid"]
        stack = session["stack"]
        user_profile = User_db.get_user_by_oid(_id)
        eqpts = Eqpt_db.get_all_available_eqpt()
        
        if role == "Intern":
            reports =list(Report_db.get_by_sender(_id, uid))
            requests = list(Request_db.get_by_sender(_id, uid))
            projects = []
            
            project_all = list(Project_db.get_by_recipient_dtls(category="all", recipient=stack, name="All stack members"))
            for project in project_all:
                projects.append(project)
                
            project_one = list(Project_db.get_by_recipient_dtls(category="one", recipient=_id, name=uid))
            for project in project_one:
                projects.append(project)
                
            projects.sort(reverse=True, key=sortFunc)
            
            for x in reports:
                    date_time = x["date_time"].strftime("%j")
                    diff = int(datetime.now().strftime("%j")) - int(date_time)
                    
                    if diff == 0:
                        date_time_H = x["date_time"].strftime("%H")
                        diff_H = int(datetime.now().strftime("%H")) - int(date_time_H)
                        if diff_H == 0:
                            date_time_M = x["date_time"].strftime("%M")
                            diff_M = int(datetime.now().strftime("%M")) - int(date_time_M)
                            if diff_M == 0:
                                x["date_submitted"] = "now"
                            else:
                                x["date_submitted"] = f"{diff_M} minutes ago"
                        elif diff_H > 0:
                            x["date_submitted"] = f"{diff_H} hours ago"
                            
                    elif diff==1:
                        x["date_submitted"] = "yesterday"
                            
            for x in requests:
                date_time = x["date_time"].strftime("%j")
                diff = int(datetime.now().strftime("%j")) - int(date_time)
                
                if diff == 0:
                    date_time_H = x["date_time"].strftime("%H")
                    diff_H = int(datetime.now().strftime("%H")) - int(date_time_H)
                    if diff_H == 0:
                        date_time_M = x["date_time"].strftime("%M")
                        diff_M = int(datetime.now().strftime("%M")) - int(date_time_M)
                        if diff_M == 0:
                            x["date_submitted"] = "now"
                        else:
                            x["date_submitted"] = f"{diff_M} minutes ago"
                    elif diff_H > 0:
                        x["date_submitted"] = f"{diff_H} hours ago"
                        
                elif diff==1:
                    x["date_submitted"] = "yesterday"
                    
            for x in projects:
                    date_time = x["date_time"].strftime("%j")
                    diff = int(datetime.now().strftime("%j")) - int(date_time)
                    
                    if diff == 0:
                        date_time_H = x["date_time"].strftime("%H")
                        diff_H = int(datetime.now().strftime("%H")) - int(date_time_H)
                        if diff_H == 0:
                            date_time_M = x["date_time"].strftime("%M")
                            diff_M = int(datetime.now().strftime("%M")) - int(date_time_M)
                            if diff_M == 0:
                                x["date_created"] = "now"
                            else:
                                x["date_created"] = f"{diff_M} minutes ago"
                        elif diff_H > 0:
                            x["date_creatted"] = f"{diff_H} hours ago"
                            
                    elif diff==1:
                        x["date_created"] = "yesterday"

            
            # return render_template('pages/my_submissions.html', reports=reports, requests=requests, projects=projects, user_profile=user_profile, eqpts=eqpts)
            return jsonify({reports:reports, requests:requests, projects:projects, user_profile:user_profile, eqpts:eqpts, "status" : "success"})
        
        elif role == "Lead":
            if stack == "Software":
                reports =list(Report_db.get_by_sender(_id, uid))
                requests = list(Request_db.get_by_sender(_id, uid))
                projects = list(Project_db.get_by_recipient_dtls(category="one", recipient=_id, name=uid))
                
                for x in reports:
                    date_time = x["date_time"].strftime("%j")
                    diff = int(datetime.now().strftime("%j")) - int(date_time)
                    
                    if diff == 0:
                        date_time_H = x["date_time"].strftime("%H")
                        diff_H = int(datetime.now().strftime("%H")) - int(date_time_H)
                        if diff_H == 0:
                            date_time_M = x["date_time"].strftime("%M")
                            diff_M = int(datetime.now().strftime("%M")) - int(date_time_M)
                            if diff_M == 0:
                                x["date_submitted"] = "now"
                            else:
                                x["date_submitted"] = f"{diff_M} minutes ago"
                        elif diff_H > 0:
                            x["date_submitted"] = f"{diff_H} hours ago"
                            
                    elif diff==1:
                        x["date_submitted"] = "yesterday"
                            
                for x in requests:
                    date_time = x["date_time"].strftime("%j")
                    diff = int(datetime.now().strftime("%j")) - int(date_time)
                    
                    if diff == 0:
                        date_time_H = x["date_time"].strftime("%H")
                        diff_H = int(datetime.now().strftime("%H")) - int(date_time_H)
                        if diff_H == 0:
                            date_time_M = x["date_time"].strftime("%M")
                            diff_M = int(datetime.now().strftime("%M")) - int(date_time_M)
                            if diff_M == 0:
                                x["date_submitted"] = "now"
                            else:
                                x["date_submitted"] = f"{diff_M} minutes ago"
                        elif diff_H > 0:
                            x["date_submitted"] = f"{diff_H} hours ago"
                            
                    elif diff==1:
                        x["date_submitted"] = "yesterday"
                    
                for x in projects:
                    date_time = x["date_time"].strftime("%j")
                    diff = int(datetime.now().strftime("%j")) - int(date_time)
                    
                    if diff == 0:
                        date_time_H = x["date_time"].strftime("%H")
                        diff_H = int(datetime.now().strftime("%H")) - int(date_time_H)
                        if diff_H == 0:
                            date_time_M = x["date_time"].strftime("%M")
                            diff_M = int(datetime.now().strftime("%M")) - int(date_time_M)
                            if diff_M == 0:
                                x["date_created"] = "now"
                            else:
                                x["date_created"] = f"{diff_M} minutes ago"
                        elif diff_H > 0:
                            x["date_creatted"] = f"{diff_H} hours ago"
                            
                    elif diff==1:
                        x["date_created"] = "yesterday"

            
                # return render_template('pages/my_submissions.html', reports=reports, requests=requests, projects=projects, user_profile=user_profile, eqpts=eqpts)
                return jsonify({reports:reports, requests:requests, projects:projects, user_profile:user_profile, eqpts:eqpts, "status" : "success"})

            
            else:
                reports =list(Report_db.get_by_sender(_id, uid))
                requests = list(Request_db.get_by_sender(_id, uid))
                projects = list(Project_db.get_by_recipient_dtls(category="one", recipient=_id, name=uid))
                
                for x in reports:
                    date_time = x["date_time"].strftime("%j")
                    diff = int(datetime.now().strftime("%j")) - int(date_time)
                    
                    if diff == 0:
                        date_time_H = x["date_time"].strftime("%H")
                        diff_H = int(datetime.now().strftime("%H")) - int(date_time_H)
                        if diff_H == 0:
                            date_time_M = x["date_time"].strftime("%M")
                            diff_M = int(datetime.now().strftime("%M")) - int(date_time_M)
                            if diff_M == 0:
                                x["date_submitted"] = "now"
                            else:
                                x["date_submitted"] = f"{diff_M} minutes ago"
                        elif diff_H > 0:
                            x["date_submitted"] = f"{diff_H} hours ago"
                            
                    elif diff==1:
                        x["date_submitted"] = "yesterday"
                            
                for x in requests:
                    date_time = x["date_time"].strftime("%j")
                    diff = int(datetime.now().strftime("%j")) - int(date_time)
                    
                    if diff == 0:
                        date_time_H = x["date_time"].strftime("%H")
                        diff_H = int(datetime.now().strftime("%H")) - int(date_time_H)
                        if diff_H == 0:
                            date_time_M = x["date_time"].strftime("%M")
                            diff_M = int(datetime.now().strftime("%M")) - int(date_time_M)
                            if diff_M == 0:
                                x["date_submitted"] = "now"
                            else:
                                x["date_submitted"] = f"{diff_M} minutes ago"
                        elif diff_H > 0:
                            x["date_submitted"] = f"{diff_H} hours ago"
                            
                    elif diff==1:
                        x["date_submitted"] = "yesterday"
                        
                    
                for x in projects:
                    date_time = x["date_time"].strftime("%j")
                    diff = int(datetime.now().strftime("%j")) - int(date_time)
                    
                    if diff == 0:
                        date_time_H = x["date_time"].strftime("%H")
                        diff_H = int(datetime.now().strftime("%H")) - int(date_time_H)
                        if diff_H == 0:
                            date_time_M = x["date_time"].strftime("%M")
                            diff_M = int(datetime.now().strftime("%M")) - int(date_time_M)
                            if diff_M == 0:
                                x["date_created"] = "now"
                            else:
                                x["date_created"] = f"{diff_M} minutes ago"
                        elif diff_H > 0:
                            x["date_creatted"] = f"{diff_H} hours ago"
                            
                    elif diff==1:
                        x["date_created"] = "yesterday"

            
                # return render_template('pages/my_submissions.html', reports=reports, requests=requests, projects=projects, user_profile=user_profile, eqpts=eqpts)
                return jsonify({reports:reports, requests:requests, projects:projects, user_profile:user_profile, eqpts:eqpts, "status" : "success"})
        else:
            # flash('permission not granted', "danger")
            # return redirect(url_for('login'))  
            return jsonify({"message" : 'permission not granted', "status" : "info"})                                                   
    else:
        # flash  ('you are not logged in!', "danger")
        # return redirect(url_for('login')) 
         return jsonify({"message" : 'You are not logged in!', "status" : "info"}) 
    
@app.get('/submissions/interns')
def intern_submissions():
    
    if "user_id" in session:
        role = session["user_role"]
        _id = session["user_id"]
        uid = session["user_uid"]
        stack = session["stack"]
        user_profile = User_db.get_user_by_oid(_id)
        eqpts = Eqpt_db.get_all_available_eqpt()
        
        if role == "Lead":
            if stack == "Software":
                position = "Software"
                reports =  list(Report_db.get_by_recipient(position))
                requests = list(Request_db.get_by_recipient(position, _id))
                projects = list(Project_db.get_by_sender(_id, uid))
                interns = list(User_db.get_users_by_stack(stack))
                
                for x in reports:
                    date_time = x["date_time"].strftime("%j")
                    diff = int(datetime.now().strftime("%j")) - int(date_time)
                    
                    if diff == 0:
                        date_time_H = x["date_time"].strftime("%H")
                        diff_H = int(datetime.now().strftime("%H")) - int(date_time_H)
                        if diff_H == 0:
                            date_time_M = x["date_time"].strftime("%M")
                            diff_M = int(datetime.now().strftime("%M")) - int(date_time_M)
                            if diff_M == 0:
                                x["date_submitted"] = "now"
                            else:
                                x["date_submitted"] = f"{diff_M} minutes ago"
                        elif diff_H > 0:
                            x["date_submitted"] = f"{diff_H} hours ago"
                            
                    elif diff==1:
                        x["date_submitted"] = "yesterday"
                            
                for x in requests:
                    date_time = x["date_time"].strftime("%j")
                    diff = int(datetime.now().strftime("%j")) - int(date_time)
                    
                    if diff == 0:
                        date_time_H = x["date_time"].strftime("%H")
                        diff_H = int(datetime.now().strftime("%H")) - int(date_time_H)
                        if diff_H == 0:
                            date_time_M = x["date_time"].strftime("%M")
                            diff_M = int(datetime.now().strftime("%M")) - int(date_time_M)
                            if diff_M == 0:
                                x["date_submitted"] = "now"
                            else:
                                x["date_submitted"] = f"{diff_M} minutes ago"
                        elif diff_H > 0:
                            x["date_submitted"] = f"{diff_H} hours ago"
                            
                    elif diff==1:
                        x["date_submitted"] = "yesterday"
                
                for x in projects:
                    date_time = x["date_time"].strftime("%j")
                    diff = int(datetime.now().strftime("%j")) - int(date_time)
                    
                    if diff == 0:
                        date_time_H = x["date_time"].strftime("%H")
                        diff_H = int(datetime.now().strftime("%H")) - int(date_time_H)
                        if diff_H == 0:
                            date_time_M = x["date_time"].strftime("%M")
                            diff_M = int(datetime.now().strftime("%M")) - int(date_time_M)
                            if diff_M == 0:
                                x["date_created"] = "now"
                            else:
                                x["date_created"] = f"{diff_M} minutes ago"
                        elif diff_H > 0:
                            x["date_created"] = f"{diff_H} hours ago"
                            
                    elif diff==1:
                        x["date_created"] = "yesterday"

            
                # return render_template('pages/intern_submissions.html', reports=reports, requests=requests, projects=projects, user_profile=user_profile, interns=interns)
                return jsonify({reports:reports, requests:requests, projects:projects, user_profile:user_profile, interns:interns, "status" : "success"})
            else:
                position = "Hardware"
                reports = list(Report_db.get_by_recipient(position))
                requests = list(Request_db.get_by_recipient(position, _id))
                projects = list(Project_db.get_by_sender(_id, uid))
                interns = list(User_db.get_users_by_stack(stack))
                
                for x in reports:
                    date_time = x["date_time"].strftime("%j")
                    diff = int(datetime.now().strftime("%j")) - int(date_time)
                    
                    if diff == 0:
                        date_time_H = x["date_time"].strftime("%H")
                        diff_H = int(datetime.now().strftime("%H")) - int(date_time_H)
                        if diff_H == 0:
                            date_time_M = x["date_time"].strftime("%M")
                            diff_M = int(datetime.now().strftime("%M")) - int(date_time_M)
                            if diff_M == 0:
                                x["date_submitted"] = "now"
                            else:
                                x["date_submitted"] = f"{diff_M} minutes ago"
                        elif diff_H > 0:
                            x["date_submitted"] = f"{diff_H} hours ago"
                            
                    elif diff==1:
                        x["date_submitted"] = "yesterday"
                            
                for x in requests:
                    date_time = x["date_time"].strftime("%j")
                    diff = int(datetime.now().strftime("%j")) - int(date_time)
                    
                    if diff == 0:
                        date_time_H = x["date_time"].strftime("%H")
                        diff_H = int(datetime.now().strftime("%H")) - int(date_time_H)
                        if diff_H == 0:
                            date_time_M = x["date_time"].strftime("%M")
                            diff_M = int(datetime.now().strftime("%M")) - int(date_time_M)
                            if diff_M == 0:
                                x["date_submitted"] = "now"
                            else:
                                x["date_submitted"] = f"{diff_M} minutes ago"
                        elif diff_H > 0:
                            x["date_submitted"] = f"{diff_H} hours ago"
                            
                    elif diff==1:
                        x["date_submitted"] = "yesterday"
                
                for x in projects:
                    date_time = x["date_time"].strftime("%j")
                    diff = int(datetime.now().strftime("%j")) - int(date_time)
                    
                    if diff == 0:
                        date_time_H = x["date_time"].strftime("%H")
                        diff_H = int(datetime.now().strftime("%H")) - int(date_time_H)
                        if diff_H == 0:
                            date_time_M = x["date_time"].strftime("%M")
                            diff_M = int(datetime.now().strftime("%M")) - int(date_time_M)
                            if diff_M == 0:
                                x["date_created"] = "now"
                            else:
                                x["date_created"] = f"{diff_M} minutes ago"
                        elif diff_H > 0:
                            x["date_created"] = f"{diff_H} hours ago"
                            
                    elif diff==1:
                        x["date_created"] = "yesterday"


                # return render_template('pages/intern_submissions.html', reports=reports, requests=requests, projects=projects, user_profile=user_profile, interns=interns)
                return jsonify({reports:reports, requests:requests, projects:projects, user_profile:user_profile, interns:interns, "status" : "success"})

        
        elif role == "Admin":
            position = "Admin"
            reports = list(Report_db.get_by_recipient(position))
            requests = list(Request_db.get_by_recipient(position, _id))
            projects = list(Project_db.get_by_sender(_id, uid))
            interns = list(User_db.get_all_users())
            
            for x in reports:
                    date_time = x["date_time"].strftime("%j")
                    diff = int(datetime.now().strftime("%j")) - int(date_time)
                    
                    if diff == 0:
                        date_time_H = x["date_time"].strftime("%H")
                        diff_H = int(datetime.now().strftime("%H")) - int(date_time_H)
                        if diff_H == 0:
                            date_time_M = x["date_time"].strftime("%M")
                            diff_M = int(datetime.now().strftime("%M")) - int(date_time_M)
                            if diff_M == 0:
                                x["date_submitted"] = "now"
                            else:
                                x["date_submitted"] = f"{diff_M} minutes ago"
                        elif diff_H > 0:
                            x["date_submitted"] = f"{diff_H} hours ago"
                            
                    elif diff==1:
                        x["date_submitted"] = "yesterday"
                            
            for x in requests:
                date_time = x["date_time"].strftime("%j")
                diff = int(datetime.now().strftime("%j")) - int(date_time)
                
                if diff == 0:
                    date_time_H = x["date_time"].strftime("%H")
                    diff_H = int(datetime.now().strftime("%H")) - int(date_time_H)
                    if diff_H == 0:
                        date_time_M = x["date_time"].strftime("%M")
                        diff_M = int(datetime.now().strftime("%M")) - int(date_time_M)
                        if diff_M == 0:
                            x["date_submitted"] = "now"
                        else:
                            x["date_submitted"] = f"{diff_M} minutes ago"
                    elif diff_H > 0:
                        x["date_submitted"] = f"{diff_H} hours ago"
                        
                elif diff==1:
                    x["date_submitted"] = "yesterday"
            
            for x in projects:
                    date_time = x["date_time"].strftime("%j")
                    diff = int(datetime.now().strftime("%j")) - int(date_time)
                    
                    if diff == 0:
                        date_time_H = x["date_time"].strftime("%H")
                        diff_H = int(datetime.now().strftime("%H")) - int(date_time_H)
                        if diff_H == 0:
                            date_time_M = x["date_time"].strftime("%M")
                            diff_M = int(datetime.now().strftime("%M")) - int(date_time_M)
                            if diff_M == 0:
                                x["date_created"] = "now"
                            else:
                                x["date_created"] = f"{diff_M} minutes ago"
                        elif diff_H > 0:
                            x["date_creatted"] = f"{diff_H} hours ago"
                            
                    elif diff==1:
                        x["date_created"] = "yesterday"

            
            # return render_template('pages/intern_submissions.html', reports=reports, requests=requests, projects=projects, user_profile=user_profile, interns=interns, eqpts=eqpts)
            return jsonify({reports:reports, requests:requests, projects:projects, user_profile:user_profile, interns:interns, eqpts:eqpts, "status" : "success"})

        else:
            # flash('permission not granted', "danger")
            # return redirect(url_for('login'))  
            return jsonify({"message" : 'permission not granted', "status" : "info"})                                                   
    else:
        # flash  ('you are not logged in!', "danger")
        # return redirect(url_for('login')) 
         return jsonify({"message" : 'You are not logged in!', "status" : "info"}) 


@app.post('/request/create')
def create_request():
    
    if "user_id" in session:
        user_id = session["user_id"]
        uid = session["user_uid"]
        
        title = request.json.get("title")
        type = request.json.get("type")
        request_dtls = request.json.get("request_dtls")
            
        receipient = request.json.get("receipient")
        sender = uid
        sender_name = User_db.get_user_fullname(uid)
        # status =  Approved, Declined or pending
        date_submitted = get_date_now()
        date_time = datetime.now()
        
        rec_not_title = "You received a new Request"
        rec_not_receivers = receipient
        rec_not_type = "Request"
        rec_not_message = f"You just received a new request from {sender_name}. Check it out in your requests tab!"
        rec_not_status = "unread"
        rec_not_sentAt = datetime.now()
        notification = Notification(rec_not_title, rec_not_receivers, rec_not_type, rec_not_message, rec_not_status, rec_not_sentAt)
        
        requested = Request(title, type, sender, receipient, date_submitted, date_time, request_dtls)
        request_id = Request_db.insert_new(requested)
            
        if request_id: 
            Notifications.send_notification(notification)
            return jsonify({"message" : "Request submitted successfully!", "status" : "success"}), 200
        else:
            return jsonify({"message" : "Request unable to be submitted. Please try again!", "status" : "error"}), 500
        
    else:
        return jsonify({"message" : 'You are not logged in!', "status" : "info"}), 401

@app.get('/request/view/<request_id>')
def view_request(request_id):
    
    if "user_id" in session:
        
        request = Request_db.get_by_request_id(request_id)
        # eqpts = Eqpt_db.get_all_available_eqpt()
    
        # return render_template('pages/view_request.html', request=request, user_profile=user_profile, eqpts=eqpts)
        response = convert_to_json_serializable({"request":request, "status" : "success"})
        return jsonify(response), 200
    else:
        return jsonify({"message" : 'You are not logged in!', "status" : "info"}), 401
    
@app.get('/request/approve/<request_id>')
def approve_request(request_id):
    
    if "user_id" in session:
        uid = session["user_uid"]
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
    else:
        # flash  ('you are not logged in!', "danger")
        # return redirect(url_for('login')) 
         return jsonify({"message" : 'You are not logged in!', "status" : "info"}), 401
    
@app.get('/request/decline/<request_id>')
def decline_request(request_id):
    
    if "user_id" in session:
        uid = session["user_uid"]
        declined = Request_db.decline_request(request_id)
        title = Request_db.get_by_request_id(request_id)['title']
        
        not_title = "Request Declined"
        not_receivers = [uid]
        not_type = "Request"
        not_message = f"Your request '{title}' has been declined. Check it out in your requests tab!"
        not_status = "unread"
        not_sentAt = datetime.now()
        notification = Notification(not_title, not_receivers, not_type, not_message, not_status, not_sentAt)

        if declined: 
            # flash('Request declined',"success")
            # return redirect(url_for('view_request', request_id=request_id))
            Notifications.send_notification(notification)
            return jsonify({"message" : 'Request declined', "status" : "success"})                                                   
        else:
            # flash('An error occurred! Try again', "danger")
            # return redirect(url_for('view_request', request_id=request_id))
            return jsonify({"message" : 'An error occurred! Try again', "status" : "danger"})
    else:
        # flash  ('you are not logged in!', "danger")
        # return redirect(url_for('login')) 
         return jsonify({"message" : 'You are not logged in!', "status" : "info"})

@app.post('/request/edit/<request_id>') # Remove
def edit_request(request_id):
    
    if "user_id" in session:
        user_id = session["user_id"]
        uid = session["user_uid"]
        
        title = request.form.get("title")
        type = request.form.get("type")
        eqpt_id = request.form.get("eqpt_id")
        
        if type == "Equipment":
            eqpt = {
                "id": eqpt_id,
                "name": Eqpt_db.get_eqpt_by_id(eqpt_id)["name"] 
            }
        else:
            eqpt = "None"
            
            
        quantity = request.form.get("quantity")
        date_from = request.form.get("date_from")
        date_to = request.form.get("date_to")
        purpose = request.form.get("purpose")
        recipient = request.form.get("recipient")
        sender = {
            "_id": user_id,
            "uid": uid  
                  
        }
        status = "Pending"
        now = datetime.now().strftime
        month = now("%B")
        date = now("%d")
        year = now("%Y")
        date_submitted = "{0} {1}, {2}".format(month, date, year)
        date_time = datetime.now()
        
        if recipient == "Admin":
            role = "Admin"
            id = User_db.get_user_by_role_one(role)["_id"]
            
            recipient_dtls = {
                "position": "Admin",
                "id": id
            }
            dtls = Request(title, type, eqpt, quantity, date_from, date_to, purpose, sender, recipient_dtls, status, date_submitted, date_time)
            updated = Request_db.update_request_dtls(request_id,dtls)
            
            if updated:
                # flash("Request edited successfully!", "success")
                # return redirect(url_for('view_request', request_id=request_id))
                return jsonify({"message" : 'Request edited successfully!', "status" : "success"})                                                   
            else:
                # flash('An error occurred! Try again', "danger")
                # return redirect(url_for('view_request', request_id=request_id))
                return jsonify({"message" : 'An error occurred! Try again', "status" : "danger"})

        elif recipient == "software":
            stack = "Software"
            id = User_db.get_lead(stack)["_id"]
            
            recipient_dtls = {
                "position": "Software",
                "id": id
            }
            dtls = Request(title, type, eqpt, quantity, date_from, date_to, purpose, sender, recipient_dtls, status, date_submitted, date_time)
            updated = Request_db.update_request_dtls(request_id,dtls)
            if updated:
                # flash("Request edited successfully!", "success")
                # return redirect(url_for('view_request', request_id=request_id))
                return jsonify({"message" : 'Request edited successfully!', "status" : "success"})  
            else:
                # flash('An error occurred! Try again', "danger")
                # return redirect(url_for('view_request', request_id=request_id))
                return jsonify({"message" : 'An error occurred! Try again', "status" : "danger"})

        elif recipient == "hardware":
            stack="Hardware" 
            id = User_db.get_lead(stack)["_id"]
            recipient_dtls = {
                "position": "Hardware",
                "id": id
            }
        
            dtls = Request(title, type, eqpt, quantity, date_from, date_to, purpose, sender, recipient_dtls, status, date_submitted, date_time)
            updated = Request_db.update_request_dtls(request_id,dtls)
            if updated:
                return jsonify({"message" : 'Request edited successfully!', "status" : "success"})  
            else:
                return jsonify({"message" : 'An error occurred! Try again', "status" : "danger"})
        else:
            return jsonify({"message" : 'permission not granted', "status" : "info"})                                                   
    else:
         return jsonify({"message" : 'You are not logged in!', "status" : "info"})

@app.get('/request/delete/<request_id>') # Who can delete a request?
def delete_request(request_id):
    
    if "user_id" in session:
            
        deleted = Request_db.delete_request(request_id)
        
        if deleted:
            return jsonify({"message" : 'Request deleted successfully!', "status" : "success"}), 200     
        else:
            return jsonify({"message" : 'The request was unsuccessful!', "status" : "danger"}), 500  
    else:
         return jsonify({"message" : 'You are not logged in!', "status" : "info"}), 401
  
# @app.post('/report/create')
# @jwt_required()
# def create_report():
#     data = request.json
#     report_type = data.get('report_type')
#     title = data.get('title')
#     stack = data.get('stack')
#     receiver = data.get('receiver')
#     sender = data.get('sender')
    
#     sender_avatar = User_db.get_by_uid(sender)['avatar']
    
#     if report_type == "activity":
#         duration = data.get('duration')
#         completed = data.get('completed')
#         ongoing = data.get('ongoing')
#         next = data.get('next')
#         report = ActivityReport(title=title, stack=stack, receiver=receiver, sender=sender, duration=duration, completed=completed, ongoing=ongoing, next=next, report_type=report_type, avatar=sender_avatar)
#     elif report_type == "project":
#         summary = data.get('summary')   
#         report = ProjectReport(title=title, stack=stack, summary=summary, report_type=report_type, receiver=receiver, sender=sender,  avatar=sender_avatar) 
#     else:
#         return jsonify({"message": "Invalid report type", "status": "error"}), 400
    
#     report_id = Report_db.insert_new(report)
    
#     if report_id:
#         return jsonify({"message": "Report created successfully!", "status": "success"}), 200
#     else:
#         return jsonify({"message": "Failed to create report", "status": "error"}), 500
    
# @app.get('/report/get_all')
# @jwt_required()
# def get_all_reports():
#     try:
#         user_uid = get_jwt_identity()
#         info = get_jwt()
#         user_role = info['user_role']
#         stack = info['stack']
        
#         if not user_role or not stack:
#             return jsonify({"message": "Something went wrong. Try logging in again.", "status": "error"}), 401
        
#         if user_role == 'Admin':
#             reports = Report_db.get_all()
#         elif user_role == 'Lead':
#             reports = Report_db.get_by_stack(stack)
#         else:
#             reports = Report_db.get_by_isMember(user_uid)
            
#         response = convert_to_json_serializable({'reports': list(reports), 'status': 'success'})
#         return jsonify(response), 200
    
#     except Exception as e:
#         return jsonify({"message": f'Something went wrong: {e}', 'status': "error"}), 500
    
# @app.get('/report/get_one/<report_id>')
# @jwt_required()
# def get_one(report_id):
#     try:
#         report = Report_db.get_by_report_id(report_id)
        
#         if not report:
#             return jsonify({"message": "Report not found", "status": "error"}), 404
        
#         response = convert_to_json_serializable({'report': report, 'status': 'success'}), 200
#         return jsonify(response), 200
        
#     except Exception as e:
#         return jsonify({"message": f'Something went wrong: {e}', 'status': "error"}), 500
        
# @app.post('/report/give_feedback/<report_id>') 
# @jwt_required()
# def give_feedback(report_id):
#     try:
#         feedback = request.json.get("feedback")
#         report = Report_db.get_by_report_id(report_id)
        
#         if not report:
#             return jsonify({"message": "Report not found", "status": "error"}), 404
        
#         feedback_dtls = {"feedback": feedback, "created_at": datetime.now()}
#         submitted = Report_db.give_feedback(report_id, feedback_dtls)
        
#         if not submitted: 
#             return jsonify({"message" : 'An error occured! Try again', "status" : "success"}), 500
        
#         return jsonify({"message": "Feedback sent successfully", "status": "success"}), 200
        
#     except Exception as e:
#         return jsonify({"message": f'Something went wrong: {e}', 'status': "error"}), 500
    
# @app.delete('/report/delete/<report_id>')
# @jwt_required()
# @admin_and_lead_role_required
# def delete_report(report_id):
#     try:
#         deleted = Report_db.delete_report(report_id)
#         if not deleted:
#             return jsonify({"message" : "An error occured! Try again!", "status" : "error"}), 500
        
#         return jsonify({"message" : "Report deleted successfully!", "status" : "success"}), 200
    
#     except Exception as e:
#         return jsonify({"message": f'Something went wrong: {e}', 'status': "error"}), 500
    
# @app.patch('/report/add_doc/<report_id>')
# @jwt_required()
# def add_doc(report_id):
#     try:
#         report = Report_db.get_by_report_id(report_id)
#         if not report:
#             return jsonify({"message": "Report not found", "status": "error"}), 404
        
#         doc = request.files.get("doc")
#         if not doc:
#             return jsonify({"message": "No file uploaded", "status": "error"})
        
#         filename = secure_filename(doc.filename)
#         if not AllowedExtension.files(filename):
#             return jsonify({"message" : 'Invalid file format! Try again', "status" : "error"}), 401
        
#         try:
#             uploaded = upload_func(doc, "SSRL_Lab_App/report_submissions/")
#             if not uploaded:
#                 return jsonify({"message" : 'File upload error! Try again', "status" : "danger"}), 500
            
#         except Exception as e:
#              return jsonify({"message": f'File upload error: {e}', 'status': "error"}), 500

#         doc_submission = {"filename": filename, "download_link": uploaded['secure_url'], "date_submitted": datetime.now()}
#         submitted = Report_db.add_doc(report_id, doc_submission)
        
#         if not submitted:
#             return jsonify({"message" : 'An error occurred! Try again', "status" : "danger"}), 500
        
#         return jsonify({"message": 'Document submitted successfully', "status" : "success"}), 200
        
#     except Exception as e:
#         return jsonify({"message": f'Something went wrong: {e}', 'status': "error"}), 500
    
# @app.patch('/report/add_link/<report_id>')
# @jwt_required()
# def add_link(report_id):
#     try:
#         report = Report_db.get_by_report_id(report_id)
#         if not report:
#             return jsonify({"message": "Report not found", "status": "error"}), 404
        
#         link = request.json.get('link')
#         link_submission = {"link": link, "submitted_at": datetime.now()}
#         submitted = Report_db.add_link(report_id, link_submission)
        
#         if not submitted:
#             return jsonify({"message" : 'An error occurred! Try again', "status" : "danger"}), 500
        
#         return jsonify({"message": 'Document submitted successfully', "status" : "success"}), 200
    
#     except Exception as e:
#         return jsonify({"message": f'Something went wrong: {e}', 'status': "error"}), 500

# @app.post('/project/create') 
# @jwt_required()
# def create_project():
#     try:
#         uid = get_jwt_identity()
        
#         data = request.json
#         name = data.get("name")
#         description = data.get("description")
#         objectives = data.get("objectives") 
#         leads = data.get("leads")
#         team_members = data.get("team_members") 
#         stack = data.get("stack")
#         deadline = data.get("deadline")
        
#         team_avatars = []
        
#         for lead in leads:
#             profile = User_db.get_user_by_uid(lead['id'])
#             if not profile:
#                 continue
#             else:
#                 avatar = profile['avatar']
#                 if avatar != 'NIL':
#                     team_avatars.append(avatar['secure_url'])
#                 else: team_avatars.append('NIL')
                    
#         for member in team_members:
#             profile = User_db.get_user_by_uid(member['id'])
#             if not profile:
#                 continue
#             else:
#                 avatar = profile['avatar']
#                 if avatar != 'NIL':
#                     team_avatars.append(avatar['secure_url'])
#                 else: team_avatars.append('NIL')
            
#         createdBy = uid
#         submissions = {"docs": [], "links": []} 
           
#         date_created = datetime.now()
#         project_status = "Uncompleted"
        
#         project = Project(name, description, objectives, leads, team_members, team_avatars, stack, createdBy, project_status, submissions, date_created, deadline) #Removed recipient_dtls
#         project_id = Project_db.insert_new(project)
#         # project_id = None
        
#         not_title = "New Project"
#         not_receivers = leads + team_members
#         not_type = "Project"
#         not_message = f"You have been added to a new project {name}. Check it out in your projects tab!"
#         notification = Notification(not_title, not_receivers, not_type, not_message)
        
#         if project_id:
#             response = convert_to_json_serializable({"message" : "Project created successfully!", "status" : "success", "project_id" : project_id})
#             Notifications.send_notification(notification)
#         else:
#             response = convert_to_json_serializable({"message" : f"Project with name '{name}' already exists.", "status": "error"})
#         return(response)
#     except Exception as e:
#         import traceback
#         error_details = traceback.format_exc()
#         print(error_details)  
#         return {'message': f'An error occurred: {str(e)}', 'status': 'error', "traceback": error_details}, 500

# @app.get('/project/view/<project_id>')
# @jwt_required()
# def view_project(project_id):
#     try:
#         project = Project_db.get_by_project_id(project_id)
        
#         if not project:
#             return jsonify({"message": "Invalid project id", "status": "error"}), 400
            
#         response = convert_to_json_serializable({"project": project, "status": "success"})
#         return jsonify(response), 200
#     except Exception as e:
#         return jsonify({"message": f'Something went wrong: {e}', 'status': "error"}), 500
    
# @app.get('/project/get_all')
# @jwt_required()
# def get_all_projects():
#     try:
#         uid = get_jwt_identity()
#         user_role = get_jwt()['user_role']
#         stack = get_jwt()['stack']
        
#         if user_role=="Admin":
#             projects = list(Project_db.get_all())
#         elif user_role == "Lead":
#             projects = list(Project_db.get_by_stack(stack, uid))
#         else: projects = list(Project_db.get_by_isMember(uid))
        
#         response = convert_to_json_serializable({"projects": projects, "status": "success"})
#         return jsonify(response), 200
    
#     except Exception as e:
#         return jsonify({"message": f'Something went wrong: {e}', 'status': "error"}), 500
  
# @app.patch('/project/completed/<project_id>')
# @jwt_required()
# def mark_project_completed(project_id):
#     try:
#         project = Project_db.get_by_project_id(project_id)
        
#         if (not Project_db.project_exists(project_id)):
#             return jsonify({"message": "Invalid project id", "status": "error"}), 400
        
#         name = Project_db.get_project_name(project_id)
#         members = Project_db.get_project_members(project_id)
#         members = [member['id'] for member in members]
        
#         if (project['status'] == 'Completed'):
#             return jsonify({"message": 'Project marked as complete', "status" : "success"}), 200
        
#         marked = Project_db.mark_project(project_id, "Completed")
        
#         not_title = "Project Marked as Complete"
#         not_receivers = members
#         not_type = "Project"
#         not_message = f"Project '{name}' has been marked as complete. Check it out in your projects tab!"
#         notification = Notification(not_title, not_receivers, not_type, not_message)
        
#         if marked: 
#             Notifications.send_notification(notification)
#             return jsonify({"message": 'Project marked as complete', "status" : "success"}), 200
#         else:
#             return jsonify({"message" : 'An error occurred! Try again', "status" : "danger"}), 500
        
#     except Exception as e:
#         return jsonify({"message": f'Something went wrong: {e}', 'status': "error"}), 500
    
# @app.patch('/project/incomplete/<project_id>') 
# @jwt_required()
# def mark_project_incomplete(project_id):
#     try:
#         project = Project_db.get_by_project_id(project_id)
        
#         if (not Project_db.project_exists(project_id)):
#             return jsonify({"message": "Invalid project id", "status": "error"}), 400
        
#         name = Project_db.get_project_name(project_id)
#         members = Project_db.get_project_members(project_id)
#         members = [member['id'] for member in members]
        
#         if (project['status'] == 'Uncompleted'):
#             return jsonify({"message": 'Project marked as incomplete', "status" : "success"}), 200
        
#         marked = Project_db.mark_project(project_id, "Uncompleted")
        
#         not_title = "Project Marked as Incomplete"
#         not_receivers = members
#         not_type = "Project"
#         not_message = f"Project '{name}' has been marked as incomplete. Check it out in your projects tab!"
#         notification = Notification(not_title, not_receivers, not_type, not_message)
        
#         if marked: 
#             Notifications.send_notification(notification)
#             return jsonify({"message": 'Project marked as incomplete', "status" : "success"}), 200
#         else:
#             return jsonify({"message" : 'An error occurred! Try again', "status" : "danger"}), 500
        
#     except Exception as e:
#         return jsonify({"message": f'Something went wrong: {e}', 'status': "error"}), 500

# @app.patch('/project/edit/<project_id>') # Add notifications
# @jwt_required()
# def edit_project(project_id): # Who can edit a project? Name, description, objectives, team_members, leads, deadline
#     try:
#         if (not Project_db.project_exists(project_id)):
#             return jsonify({"message": "Invalid project id", "status": "error"}), 400
        
#         data = request.json
#         print(data)
#         # name = data.get("name")
#         # existing_name = Project_db.existing_project_name(name)
        
#         # if existing_name:
#         #     return jsonify({"message" : f"Project with name '{name}' already exists.", "status": "error"}), 409
        
#         updated = Project_db.update_project_dtls(project_id, data)
#         if updated:
#             return jsonify({"message": "Project details edited successfully!", "status" : "success"}), 200
#         else:
#             return jsonify({"message" : 'An error occurred! Try again', "status" : "danger"}), 500
        
#     except Exception as e:
#         import traceback
#         print("Traceback:", traceback.format_exc())
#         return {'message': f'Something went wrong: {str(e)}', 'status': 'error', 'traceback': traceback}, 500
#         # return jsonify({"message": f'Something went wrong: {e}', 'status': "error"}), 500
    
# @app.delete('/project/delete/<project_id>')
# @jwt_required()
# def delete_project(project_id):
#     try:
#         if (not Project_db.project_exists(project_id)):
#             return jsonify({"message": "Invalid project id", "status": "error"}), 400
        
#         name = Project_db.get_project_name(project_id)
#         members = Project_db.get_project_members(project_id)
#         members = [member['id'] for member in members]
#         deleted = Project_db.delete_project(project_id, name)
            
#         not_title = "Project Deleted"
#         not_receivers = members
#         not_type = "Project"
#         not_message = f"Project '{name}' has been deleted."
#         notification = Notification(not_title, not_receivers, not_type, not_message)
            
#         if deleted:
#             Notifications.send_notification(notification)
#             return jsonify({"message": "Project deleted successfully!", "status" : "success"}), 200
#         else:
#             return jsonify({"message": 'The project could not be deleted!', "status" : "danger"}), 500
        
#     except Exception as e:
#         return jsonify({"message": f'Something went wrong: {e}', 'status': "error"}), 500

# @app.patch('/project/submit_doc/<project_id>') # Check file size and confirm that file of the same metadata does not exist.
# @jwt_required()
# def submit_project_doc(project_id): # Add notification
#     try:
#         if (not Project_db.project_exists(project_id)):
#             return jsonify({"message": "Invalid project id", "status": "error"}), 400
        
#         submission = request.files["file"]
#         filename = secure_filename(submission.filename)
        
#         if not submission:
#             return jsonify({"message": "No doc attached", "status": "error"}), 400
        
#         if not check_file_size(submission):
#             return jsonify({"message": "Doc size exceeds 1MB", "status": "error"}), 400
        
#         if not AllowedExtension.files(filename):
#             return jsonify({"message": "Invalid doc type", "status": "error"}), 400                            
        
#         try:
#             uploaded = upload_func(submission, f"SSRL_Lab_App/projects/{project_id}")
            
#             if not uploaded:
#                 return jsonify({"message" : 'An error occurred! Try again', "status" : "danger"}), 500

#             print(uploaded)
#             project_submission = {"filename": filename, "download_link": uploaded["secure_url"], "date_submitted": datetime.now()}
#             submitted = Project_db.submit_doc(project_id, project_submission)
                
#             if not submitted:
#                 return jsonify({"message" : 'An error occurred! Try again', "status" : "danger"}), 500
            
#         except Exception as e:
#             return jsonify({"message" : f"Couldn't upload your project at the moment! {e}", "status" : "danger"}),500
        
#         return jsonify({"submission": project_submission, "status" : "success"}), 200
        
#     except Exception as e:
#         return jsonify({"message": f'Something went wrong: {e}', 'status': "error"}), 500
    
# @app.patch('/project/submit_link/<project_id>') # Validate link input on frontend
# def submit_project_link(project_id): # Add notification
#     if 'user_id' in session:
        
#         if (not Project_db.project_exists(project_id)):
#             return jsonify({"message": "Invalid project id", "status": "error"}), 400
        
#         data = request.json
#         title = data.get('title')
#         link = data.get('link')
        
#         link_submission = {"title": title, "link": link, "date_submitted": get_date_now()}
#         submitted = Project_db.submit_link(project_id, link_submission)
        
#         if submitted:
#             return jsonify({"message": 'Project submitted successfully', "status" : "success"}), 200
#         else:
#             return jsonify({"message" : 'An error occurred! Try again', "status" : "danger"}), 500
#     else:
#         return jsonify({"message" : 'You are not logged in!', "status" : "info"}), 401

# @app.get('/project/submissions/<project_id>')
# def project_submissions(project_id):
    
#     if "user_id" in session:
        
#         if (not Project_db.project_exists(project_id)):
#             return jsonify({"message": "Invalid project id", "status": "error"}), 400
    
#         submissions = Project_db.get_project_submissions(project_id)
#         return jsonify({"submissions":submissions, "status" : "success"})
#     else:
#         # flash  ('you are not logged in!', "danger")
#         # return redirect(url_for('login')) 
#         return jsonify({"message" : 'You are not logged in!', "status" : "info"})
        
# @app.post('/project/send_announcement/<project_id>')
# def send_project_announcement(project_id):
    
#     if "user_id" in session:
        
#         if (not Project_db.project_exists(project_id)):
#             return jsonify({"message": "Invalid project id", "status": "error"}), 400
        
#         announcement = request.json.get('announcement')
#         receivers = request.json.get('receivers') # all | leads | team_members
        
#         all = Project_db.get_project_members(project_id)
#         leads = Project_db.get_project_leads(project_id)
#         team_members = Project_db.get_project_team_members(project_id)
        
#         if (receivers == "all"):
#             recepient = all
#         elif (receivers == "leads"):
#             recepient = leads
#         else:
#             recepient = team_members
        
#         not_title = f"New Project Announcement: {Project_db.get_project_name(project_id)}"
#         not_receivers = recepient
#         not_type = "Project"
#         not_message = announcement
#         not_status = "unread"
#         not_sentAt = datetime.now()
#         notification = Notification(not_title, not_receivers, not_type, not_message, not_status, not_sentAt)
        
#         Notifications.send_notification(notification)

#         return jsonify({"message": "Announcement made successfully", "status" : "success"}), 200

#     else:
#         # flash  ('you are not logged in!', "danger")
#         # return redirect(url_for('login')) 
#         return jsonify({"message" : 'You are not logged in!', "status" : "info"})
    
# @app.get('/project/send/feedback/<project_id>/<id>') # Remove
# def send_feedback(project_id, id):
    
#     if "user_id" in session:
#         user_id = session["user_id"]
#         user_profile = User_db.get_user_by_oid(user_id)
#         project = Project_db.get_by_project_id(project_id)
#         submissions = project["submissions"]
        
#         for x in submissions:
#             if x["id"]==id:
#                 submission=x
#                 break
        
#         # return render_template('pages/send_feedback.html', user_profile=user_profile, project=project, submission=submission)
#         return ({ user_profile:user_profile, project:project, submission:submission, "status" : "success"})
#     else:
#         # flash  ('you are not logged in!', "danger")
#         # return redirect(url_for('login')) 
#         return jsonify({"message" : 'You are not logged in!', "status" : "info"})
    
# @app.post('/submit/feedback/<project_id>/<id>') # Remove
# def submit_feedback(project_id, id):
    
#     if "user_id" in session:
#         submissions = Project_db.get_by_project_id(project_id)["submissions"]
        
#         for  x in submissions:
#             if x["id"] == id:
#                 x["feedback"] = request.form.get("feedback")
                
#         submitted = Project_db.mark_project(project_id, submissions)
    

#         if submitted: 
#             # flash('Feedback sent successfully',"success")
#             # return redirect(url_for('project_submissions', project_id=project_id))
#             return jsonify({"message" : 'Feedback sent successfully', "status" : "success"})
#         else:
#             # flash('An error occurred! Try again', "danger")
#             # return redirect(url_for('view_request', request_id=request_id))
#             return jsonify({"message" : 'An error occurred! Try again', "status" : "danger"})
#     else:
#         # flash  ('you are not logged in!', "danger")
#         # return redirect(url_for('login')) 
#         return jsonify({"message" : 'You are not logged in!', "status" : "info"})
  
@app.get('/project/submissions/download/<project_id>/<id>')
def download_project_submissions(project_id, id):
    #user_id = session["user_id"]
    #user_profile = User_db.get_user_by_oid(user_id)
    
    if "user_id" in session:

        submissions = Project_db.get_by_project_id(project_id)["submissions"]
        app.logger.info(submissions)
        
        for x in submissions:
            if x["id"]==id:
                upload = x
                break
        file_url = upload["file_path"]
        file_name = upload["file_name"]
        app.logger.info(file_url)
        
        response = send_file(urllib.request.urlopen(file_url), download_name=file_name, as_attachment=True)
        return jsonify({response:response, "status" : "success"}), 200 #Checkout for error

    else:
        # flash  ('you are not logged in!', "danger")
        # return redirect(url_for('login')) 
        return jsonify({"message" : 'You are not logged in!', "status" : "info"})  
    
@app.post('/todo/create') 
def create_todo():
    
    if "user_id" in session:
        user_id = session["user_id"]
        description = request.get_json()['description']
        
        dtls = {
            "uid": user_id,
            "description": description,
            "date_time": datetime.now(),
            "completed": False
        }
        id = str(Todos_db.create_todo(dtls))
        
        return jsonify({
            'description': description,
            'id' : id
        })
    
    else:
        # flash  ('you are not logged in!', "danger")
        # return redirect(url_for('login')) 
        return jsonify({"message" : 'You are not logged in!', "status" : "info"})

@app.get('/todo/delete/<todo_id>')
def delete_todo(todo_id):    
    if "user_id" in session:        
        deleted = Todos_db.delete_todo(todo_id)
        
        if deleted:
            return jsonify({
                'description':"deleted"
            })
        else:
            # flash('An error occurred! Try again', "danger")
            # return redirect(url_for('view_request', request_id=request_id))
            return jsonify({"message" : 'An error occurred! Try again', "status" : "danger"})
    else:
        # flash  ('you are not logged in!', "danger")
        # return redirect(url_for('login')) 
        return jsonify({"message" : 'You are not logged in!', "status" : "info"})

@app.post('/todo/<todo_id>/set-completed')
def mark_completed(todo_id):    
    
    if "user_id" in session:   
        user_id = session["user_id"]
        
        status = request.get_json()['completed']
        dtls = {
            "completed": status
        }     
        marked = Todos_db.update_todo(todo_id, dtls)
        todo = Todos_db.get_specific_todo(user_id, todo_id)
        if marked:
            return jsonify({
                'id': todo_id,
                'description': todo["description"],
                'completed':status  
            })
        else:
            # flash('An error occurred! Try again', "danger")
            # return redirect(url_for('view_request', request_id=request_id))
            return jsonify({"message" : 'An error occurred! Try again', "status" : "danger"})
    else:
        # flash  ('you are not logged in!', "danger")
        # return redirect(url_for('login')) 
        return jsonify({"message" : 'You are not logged in!', "status" : "info"})


@app.post('/todos/filter')
def task_filter():
    
    if "user_id" in session:
        user_id = session["user_id"]
        
        option = request.get_json()['filter']
        todos = list(Todos_db.get_todos_by_user_id(user_id))
        app.logger.info(option)
        
        taskCompleted = 0
        if option == "week":
            for todo in todos:
                if todo["completed"]==True:
                    if (todo["date_time"]).strftime("%U")==datetime.now().strftime("%U"):
                        taskCompleted = int(taskCompleted) + 1
                    else:
                        continue
                else:
                    continue
            
            return jsonify({ 'taskCompleted': taskCompleted})
        
        elif option == "month":
            for todo in todos:
                if todo["completed"]==True:
                    if (todo["date_time"]).strftime("%m")==datetime.now().strftime("%m"):
                        taskCompleted = int(taskCompleted) + 1
                    else:
                        continue
                else:
                    continue
            return jsonify({ 'taskCompleted': taskCompleted})
            
                
        elif option == "year":
            for todo in todos:
                if todo["completed"]==True:
                    if (todo["date_time"]).strftime("%Y")==datetime.now().strftime("%Y"):
                        taskCompleted = int(taskCompleted) + 1
                    else:
                        continue
                else:
                    continue
            return jsonify({ 'taskCompleted': taskCompleted})
    else:
        # flash  ('you are not logged in!', "danger")
        # return redirect(url_for('login')) 
        return jsonify({"message" : 'You are not logged in!', "status" : "info"})


@app.get('/all/todos')
def all_todos():
    if "user_id" in session:
        user_id = session["user_id"]
        user_profile = User_db.get_user_by_oid(user_id)
        all_todos = list(Todos_db.get_todos_by_user_id(user_id))
        
        return render_template('pages/all_todos.html', all_todos=all_todos, user_profile=user_profile)

    else:
        # flash  ('you are not logged in!', "danger")
        # return redirect(url_for('login')) 
        return jsonify({"message" : 'You are not logged in!', "status" : "info"})

@app.get('/attendance')
def mark_atendance():
    if "user_id" in session:
        
        date_time = datetime.now()
        user_uid = session["user_uid"]
        user_id = session["user_id"]
        app.logger.info(date_time)
        body = request.args
        status = body['status']
        curr_latitude = float(body.get('curr_latitude')) * 10000000
        curr_longitude = float(body.get('curr_longitude')) * 10000000
        app.logger.info(curr_latitude)
        app.logger.info(curr_longitude)
        app.logger.info(status)
        
        long_lower = 51340485
        long_upper = 51345743
        lat_lower = 72977636
        lat_upper = 73001205
        
        if status == "in":
            app.logger.info("marking...")
            if "signed_in" in session and (session["signed_in"]).strftime("%x") == date_time.strftime("%x"):
                app.logger.info('already signed in....')
            
                flash ('you are already signed in', "info")
                return redirect(url_for('home'))
                
            elif int(curr_latitude) in range(lat_lower, lat_upper) and int(curr_longitude) in range(long_lower, long_upper):
                app.logger.info('getting data....')
                try:
                    attendance_id = Attendance_db.sign_in({"user_id": user_id, "user_uid": user_uid, "date_time":date_time, "date": date_time.strftime("%x"), "time_in": date_time.strftime("%X"), "time_out":"", "status": status})
                    session["attendance_id"] = str(attendance_id)
                    session["signed_in"] = date_time
                    app.logger.info('signed in....')
                    
                    flash ('successfully signed in', "success")
                    return redirect(url_for('home'))
            
                except:
                    flash ('unable to sign you in at this time, try again!', "danger")
                    return redirect(url_for("home"))
            else:
                flash ('Unable to sign you in a this time, seems you aren\'t in the laboratory!', "danger")
                return redirect(url_for("home"))
                
        elif status == "out":
            if "signed_in" in session and (session["signed_in"]).strftime("%x") == date_time.strftime("%x"):
                app.logger.info('you need to sign in')
                if "signed_out" in session and (session["signed_out"]).strftime("%x") == date_time.strftime("%x"):
                    
                    app.logger.info('you already sign out at' + (session["signed_out"]).strftime("%x"))
                    
                    flash ('you are already signed out', "info")
                    return redirect(url_for('home'))
                    
                elif curr_latitude in range(lat_lower, lat_upper) and curr_longitude in range(long_lower, long_upper):
                    app.logger.info("signing out....")
                    try:
                        attendance_id = session["attendance_id"]
                        Attendance_db.sign_out(attendance_id, date_time.strftime("%X"), status)
                    
                        session["signed_out"] = date_time
                        app.logger.info('signed out....')
                        
                        flash ('successfully signed out', "success")
                        return redirect(url_for('home'))
                    except:
                        flash ('unable to sign you out at this time, try again!', "danger")
                        return redirect(url_for("home"))
            else:
                flash ("You haven't signed in for today", "danger")
                return redirect(url_for('home'))

    else:
        # flash  ('you are not logged in!', "danger")
        # return redirect(url_for('login')) 
        return jsonify({"message" : 'You are not logged in!', "status" : "info"})
        

@app.post('/api/user/attendance')
def mark_atendance_api():
        
        body = request.get_json()
        date_time = datetime.now()
        user_uid = body["user_uid"]
        scanned_data = body["scanned_data"]
        pwd = body["pwd"]
        app.logger.info(user_uid)
        app.logger.info(scanned_data)
        app.logger.info(pwd)
        
        scanned_date_time, encrypted_secret_key = scanned_data.split(",") 
        secret_key = decrypt(encrypted_secret_key)
        app.logger.info(date_time)
        
        app.logger.info(secret_key)
        app.logger.info(SSRL_SECTRET_KEY)
        date = scanned_date_time.split(" ")
        app.logger.info(date[0])   
        original_datetime = datetime.fromisoformat(str(date_time))
        
        formatted_datetime_str = original_datetime.strftime("%Y-%m-%d")
        
        if secret_key == SSRL_SECTRET_KEY and date[0] == formatted_datetime_str:
            authenticated = authenticate_user_for_attendance(user_uid, pwd)    
            
            if not authenticated:
                return jsonify({
                    "success": False,
                    "response": "Failed authentication"
                }), 401
                
            
            user = list(Attendance_db_v2.get_user_attendance_by_date(user_uid, date_time.strftime("%x")))      
                
            app.logger.info(user)
            if user:
                attendance_id = user[0]["_id"]
                                        
                try:
                    Attendance_db_v2.sign_out(attendance_id, date_time.strftime("%X"), status = "out")
                
                    app.logger.info(f'{user_uid} Marked out')
                    
                    return jsonify({
                        "success": True,
                        "response": "Marked out"
                    }), 200
                except:
                    app.logger.warning("Failed to mark user out!")
                    return jsonify({
                        "success": False,
                        "response": "Server error"
                    }), 500
                    
            else:
                app.logger.info("marking...")
                
                try:
                    attendance_id = Attendance_db_v2.sign_in({"user_uid": user_uid, "date_time":date_time, "date": date_time.strftime("%x"), "time_in": date_time.strftime("%X"), "time_out":"", "status": "in"})
                    app.logger.info(f'{user_uid} Marked in')
                    
                    return jsonify({
                        "success": True,
                        "response": "Marked in"
                    }), 200
                except:
                    app.logger.warning("Failed to mark user in!")
                    return jsonify({
                        "success": False,
                        "response": "Server error"
                    }), 500
                
        else:
            return jsonify({
                "success": False,
                "response": "Invalid data"   
            }), 401
   
        
@app.post('/api/user/login')
def api_authenticate_user():
    body = request.get_json()
    
    user_uid = body["user_uid"]
    pwd = body["pwd"]
    date_time = datetime.now()
    date = date_time.strftime("%x")
    authenticated = authenticate_user_for_attendance(user_uid, pwd)
    
    marked_in_users = Attendance_db_v2.get_marked_in_users(date)
    app.logger.info(list(marked_in_users))
    if authenticated:
        return jsonify({
            "success": True,
            "response": "Authenticated"
        }), 200
    else:
        return jsonify({
            "success": False,
            "response": "Unauthorized"
        }), 401
        
        
@app.get('/api/users')
def marked_in_users():
    date_time = datetime.now()
    date = date_time.strftime("%x")
    
    try:
        marked_in_users = formatAttendance(list(Attendance_db_v2.get_marked_in_users(date)))
        app.logger.info(marked_in_users)
        
        return jsonify({
            "success": True,
            "response": marked_in_users
        }), 200
    except:
        return jsonify({
            "success": False,
            "response": "Server error"
        }), 500
        
@app.post("/upload_file")
def upload_file(): 
    if 'file' not in request.files:
        return "No file part", 400
    file = request.files['file']
    if file.filename == '':
        return "No selected file", 400
    print("File: ", file)
    response = upload_file_func(file.read(), "test")
    return response['secure_url'] 

#uploaded = uploader.upload(project, folder="smart_app/projects", resource_type="raw")

@app.post('/test_image_single')
def testImage():
    image = request.files.get('image')
    # print(request.files)
    print(image)
    if not image:
        return jsonify({'message': 'No image provided', 'status': 'error'}), 400

    if not image.content_type.startswith('image/'):
        return jsonify({'message': 'File is not an image', 'status': 'error'}), 400
    
    print(image.filename, image.content_type)
 
    try:
        upload_result = upload_func(image, folder='hospital/logo', filename=image.filename)
        print(upload_result)
        image_url = upload_result['secure_url']
    except Exception as e:
        import traceback
        print("Upload Error:", str(e))
        print("Traceback:", traceback.format_exc())
        return jsonify({
            'message': f'Error uploading image: {str(e)}',
            'status': 'error',
            'detail': traceback.format_exc()
        }), 500
    
    # print(image_url)
    
    return jsonify({'message': 'Image uploaded successfully', 'status': 'success'}), 200


