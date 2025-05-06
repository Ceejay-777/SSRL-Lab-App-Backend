from flask import Blueprint, request, jsonify
from models.models import generate, updatePwd
from flask_bcrypt import Bcrypt, check_password_hash, generate_password_hash
from funcs import convert_to_json_serializable, return_error
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_jwt
from flask_mail import Message
from app.extensions import mail
from datetime import datetime, timedelta
from models.user import User, Userdb

auth_bp = Blueprint('auth', __name__, url_prefix="/auth" )
User_db = Userdb()

@auth_bp.get('/test')
def test():
    return jsonify({"message": "Hello World", "status": "success"}), 200

@auth_bp.post('/login')
def login():
    try:
        data = request.json
        user_uid = data.get("user_uid")
        password = data.get("password")
        
        user_profile = User_db.get_user_by_uid(user_uid)
        if not user_profile:
            return {"message": f"Intern with UID {user_uid} not found", "status" : "error"}, 401
        
        if user_profile["suspended"] == "True":
            return jsonify({"message": "This account has been suspended. Please contact the admin or your stack lead.", "status": "error"}), 401
        
        authenticated = check_password_hash(user_profile["hashed_pwd"], password)
        if not authenticated:
            return {"message": "Invalid password", "status" : "error"}, 401
            
        user_profile = convert_to_json_serializable(user_profile)
        fullname = user_profile['surname'] + ' ' + user_profile['firstname']
        
        extra_claims = {
            "user_id": user_profile['_id'],
            "uid": user_profile['uid'],
            "user_role":  user_profile['role'],
            "stack":  user_profile['stack']
            }
        
        access_token = create_access_token(identity=user_uid, additional_claims=extra_claims)
        
        response = {
            "message": f"Welcome! {fullname}",
            "status" : "success",
            "user_profile": user_profile,
            "access_token": access_token
        }
        return response, 200
    except Exception as e:
        return jsonify(return_error(e)), 500

@auth_bp.get('/logout')
@jwt_required()
def logout():
    return jsonify({"message": "Logged out successfully", "status": "success"}), 200 # Return to login

@auth_bp.post('/forgot_password')
def forgot_password():
    try:
        data = request.json
        uid = data.get("uid")
        email = data.get("email")
        
        user = User_db.get_user_by_uid(uid)
        if not user:
                return {"message": "Intern with UID {user_uid} not found", "status" : "error"}, 401        
            
        if not user.get("email", None) == email:
            return jsonify( {"message": "Please confirm that the provided email is correct!", "status": "error"}), 403
        
        otp = generate.OTP()
        details = {'otp': otp, 'expiry': (datetime.now() + timedelta(minutes=10))}
        set_otp = User_db.update_user(uid, {'otp': details})
        
        if not set_otp["success"]:
            return jsonify({'message': set_otp['error'], 'status': 'error'}), 500

        try: 
            msg = Message('SSRL Password Recovery', recipients = [email])
            msg.body = f"Your passowrd recovery OTP is {otp}\n\nThe OTP will expire in 24 hours\n\n\nFrom SSRL Team"
            
            mail.send(msg)
            
        except Exception as e:
            print(return_error(e)['message'])
        
        response = {"message": "OTP sent successfully", "status" : "success",}
        
        return jsonify(response), 200
    
    except Exception as e:
        return jsonify(return_error(e)), 500
        
@auth_bp.post('/confirm_otp')
def confirm_otp():
    try:
        data = request.json
        input_otp = data.get("otp")
        uid = data.get("uid")
        
        if not input_otp:
            return jsonify({'message': 'OTP is required', 'status': 'error'}), 401
        
        user = User_db.get_user_by_uid(uid)
        if not user:
            return jsonify( {"message": f"Intern with uid '{uid}' does not exist", "status": "error"}), 403
        
        otp = user.get('otp', {}).get('otp', None)
        otp_expiry = user.get('otp', {}).get('expiry', None)
        
        if not otp:
            return jsonify({"message": "OTP not found. Enter your email in the forgot passowrd field to get an OTP", "status" : "error"}), 401
         
        if input_otp != otp:
            return jsonify({"message": "Invalid OTP", "status" : "error"}), 403
        
        if otp_expiry < datetime.now():
            return jsonify({"message": "OTP has expired", "status" : "error"}), 401 
        
        return jsonify({"message": "OTP confirmed. Proceed to change password.", "status" : "success"}), 200
        
    except Exception as e:
        return jsonify(return_error(e)), 500

@auth_bp.patch('/change_password')
def change_password():
    data = request.json
    new_password = data.get("new_password")
    uid = data.get('uid')
    
    try: 
        hashed_pwd = generate_password_hash(new_password)
        details = {"hashed_pwd": hashed_pwd}
        
        updated = User_db.update_user(uid, details)
        if not updated['success']:
            print(updated['message'])
            return jsonify({'message': 'Could not change your password right now. Please try again later', 'status': 'error'}), 500
            
        return jsonify({"message": f"Password changed successfully!", "status" : "success"}), 200 
    
    except Exception as e:
        return jsonify(return_error(e)), 500
