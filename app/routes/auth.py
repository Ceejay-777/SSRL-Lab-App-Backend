from flask import Blueprint, request, jsonify
from db.models import Userdb, generate, updatePwd
from flask_bcrypt import Bcrypt, check_password_hash, generate_password_hash
from funcs import convert_to_json_serializable
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_jwt
from flask_mail import Message
from app.extensions import mail
from datetime import datetime, timedelta

auth_bp = Blueprint('auth', __name__)

User_db = Userdb()

@auth_bp.post('/login')
def login():
    user_uid = request.json.get("user_uid")
    pwd = request.json.get("pwd")
    user_profile = User_db.get_user_by_uid(user_uid)
    
    if not user_profile:
        return {"message": "Invalid login ID", "status" : "danger"}, 401
    
    if user_profile["deleted"] == "True":
        return jsonify({"message": "Could not find user with the inputted credentials.", "status": "error"}), 404
    
    if user_profile["suspended"] == "True":
        return jsonify({"message": "This account has been suspended. Please contact the admin or your stack lead.", "status": "error"}), 401
    
    authenticated = check_password_hash(user_profile["hashed_pwd"], pwd)
    if not authenticated:
        return {"message": "Invalid password","status" : "danger"}, 401
        
    user_profile = convert_to_json_serializable(user_profile)
    
    extra_claims = {
        "user_id": user_profile['_id'],
        "user_role":  user_profile['role'],
        "stack":  user_profile['stack']
        }
    
    access_token = create_access_token(identity=user_uid, additional_claims=extra_claims)
    
    response = {
        "message": f"Welcome! {user_profile['fullname']}",
        "status" : "success",
        "user_profile": user_profile,
        "access_token": access_token
    }
    return response, 200

@auth_bp.get('/logout')
@jwt_required()
def logout():
    return jsonify({"message": "Logged out successfully", "status": "success"}), 200 # Return to login

@auth_bp.post('/forgot_password')
def forgot_password():
    try:
        uid = request.json.get("uid")
        email = request.json.get("email")
        user = User_db.get_user_by_uid(uid)
        
        if not user:
            return jsonify( {"message": "Please confirm that your username is correct!", "status": "danger"}), 403
        
        if not user.get("email", None) == email:
            return jsonify( {"message": "Please confirm that your email is correct!", "status": "danger"}), 403
        
        otp = generate.OTP()
        dtl = {'otp': otp, 'expiry': (datetime.now() + timedelta(days=1))}
        set_otp = User_db.update_dtl(uid, {'otp': dtl})
        
        if not set_otp:
            return jsonify({'message': 'Could not send OTP right now. Please try again later', 'status': 'error'}), 500
    
        msg = Message('SSRL Password Recovery', recipients = [email])
        msg.body = f"Enter the OTP below into the required field \nThe OTP will expire in 24 hours\n\nOTP: {otp}  \n\n\nFrom SSRL Team"
        
        mail.send(msg)
        
        print(otp)
        print(email)
        
        response = {
            "message": "OTP sent successfully",
            "otp": otp, 
            "status" : "success",
        }
        
        return jsonify(response), 200
    
    except Exception as e:
        # import traceback
        # error = traceback.format_exc()
        # print(error)
        print(e)
        response = {
            "message": "Unable to recover your account at the moment! Please confirm that the input email is correct or check your internet connection.",
            "status": "danger",
            "error": str(e),
            
        }
        return jsonify(response), 500
        
@auth_bp.post('/confirm/otp')
def confirm_otp():
    try:
        input_otp = request.json.get("otp")
        uid = request.json.get("uid")
        user = User_db.get_user_by_uid(uid)
        
        if not user:
            return jsonify( {"message": "Please confirm that your username is correct!", "status": "danger"}), 403
        
        otp = user.get('otp', {}).get('otp', None)
        otp_expiry = user.get('otp', {}).get('expiry', None)
        
        if otp and input_otp == otp and otp_expiry > datetime.now():
            return jsonify({"message": "OTP confirmed. Proceed to change password.", "status" : "success"}), 200 
        
        else:
            return jsonify({"message": "Invalid OTP!", "status" : "danger"}), 401
        
    except Exception as e:
        return jsonify({"message": f'Something went wrong: {e}', 'status': "error"}), 500

@auth_bp.patch('/change_password')
def change_password():
    new_pwd = request.json.get("new_pwd")
    print(new_pwd)
    uid = request.json.get('uid')
    
    try: 
        hashed_pwd = generate_password_hash(new_pwd)
        dtls = {"hashed_pwd": hashed_pwd}
        updated = User_db.update_dtl(uid, dtls)
        
        if not updated:
            return jsonify({'message': 'Could not change your password right now. Please try again later', 'status': 'error'}), 500
            
        return jsonify({"message": f"Password changed successfully!", "status" : "success"}), 200 
    
    except Exception as e:
        print(e)
        return jsonify({"message": f"Something went wrong! Please, try again", "status" : "danger"}), 500
