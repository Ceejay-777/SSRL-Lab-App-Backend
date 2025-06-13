from flask import Flask, session, render_template, redirect, url_for, request, flash, send_file, jsonify
from flask_bcrypt import Bcrypt, check_password_hash, generate_password_hash
from flask_mail import Mail, Message
from flask_cors import CORS, cross_origin
from models.models import *
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
from models.user import User, Userdb
from models.project import Project, Projectdb

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

@app.get('/test')
@jwt_required()
def test():
    res = {"message" : "Test success"}
    return jsonify(res), 200
    
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


# @app.post('/request/create')
# def create_request():
    
#     if "user_id" in session:
#         user_id = session["user_id"]
#         uid = session["user_uid"]
        
#         title = request.json.get("title")
#         type = request.json.get("type")
#         request_dtls = request.json.get("request_dtls")
            
#         receipient = request.json.get("receipient")
#         sender = uid
#         sender_name = User_db.get_user_fullname(uid)
#         # status =  Approved, Declined or pending
#         date_submitted = get_date_now()
#         date_time = datetime.now()
        
#         rec_not_title = "You received a new Request"
#         rec_not_receivers = receipient
#         rec_not_type = "Request"
#         rec_not_message = f"You just received a new request from {sender_name}. Check it out in your requests tab!"
#         rec_not_status = "unread"
#         rec_not_sentAt = datetime.now()
#         notification = Notification(rec_not_title, rec_not_receivers, rec_not_type, rec_not_message, rec_not_status, rec_not_sentAt)
        
#         requested = Request(title, type, sender, receipient, date_submitted, date_time, request_dtls)
#         request_id = Request_db.insert_new(requested)
            
#         if request_id: 
#             Notifications.send_notification(notification)
#             return jsonify({"message" : "Request submitted successfully!", "status" : "success"}), 200
#         else:
#             return jsonify({"message" : "Request unable to be submitted. Please try again!", "status" : "error"}), 500
        
#     else:
#         return jsonify({"message" : 'You are not logged in!', "status" : "info"}), 401

# @app.get('/request/view/<request_id>')
# def view_request(request_id):
    
#     if "user_id" in session:
        
#         request = Request_db.get_by_request_id(request_id)
#         # eqpts = Eqpt_db.get_all_available_eqpt()
    
#         # return render_template('pages/view_request.html', request=request, user_profile=user_profile, eqpts=eqpts)
#         response = convert_to_json_serializable({"request":request, "status" : "success"})
#         return jsonify(response), 200
#     else:
#         return jsonify({"message" : 'You are not logged in!', "status" : "info"}), 401
    
# @app.get('/request/approve/<request_id>')
# def approve_request(request_id):
    
#     if "user_id" in session:
#         uid = session["user_uid"]
#         approved = Request_db.approve_request(request_id)
#         title = Request_db.get_by_request_id(request_id)['title']
        
#         not_title = "Request Approved"
#         not_receivers = [uid]
#         not_type = "Request"
#         not_message = f"Your request '{title}' has been approved. Check it out in your requests tab!"
#         not_status = "unread"
#         not_sentAt = datetime.now()
#         notification = Notification(not_title, not_receivers, not_type, not_message, not_status, not_sentAt)

#         if approved: 
#             Notifications.send_notification(notification)
#             return jsonify({"message" : 'Request approved', "status" : "success"}), 200                                                  
#         else:
#             return jsonify({"message" : 'An error occurred! Try again', "status" : "danger"}), 500
#     else:
#         # flash  ('you are not logged in!', "danger")
#         # return redirect(url_for('login')) 
#          return jsonify({"message" : 'You are not logged in!', "status" : "info"}), 401
    
# @app.get('/request/decline/<request_id>')
# def decline_request(request_id):
    
#     if "user_id" in session:
#         uid = session["user_uid"]
#         declined = Request_db.decline_request(request_id)
#         title = Request_db.get_by_request_id(request_id)['title']
        
#         not_title = "Request Declined"
#         not_receivers = [uid]
#         not_type = "Request"
#         not_message = f"Your request '{title}' has been declined. Check it out in your requests tab!"
#         not_status = "unread"
#         not_sentAt = datetime.now()
#         notification = Notification(not_title, not_receivers, not_type, not_message, not_status, not_sentAt)

#         if declined: 
#             # flash('Request declined',"success")
#             # return redirect(url_for('view_request', request_id=request_id))
#             Notifications.send_notification(notification)
#             return jsonify({"message" : 'Request declined', "status" : "success"})                                                   
#         else:
#             # flash('An error occurred! Try again', "danger")
#             # return redirect(url_for('view_request', request_id=request_id))
#             return jsonify({"message" : 'An error occurred! Try again', "status" : "danger"})
#     else:
#         # flash  ('you are not logged in!', "danger")
#         # return redirect(url_for('login')) 
#          return jsonify({"message" : 'You are not logged in!', "status" : "info"})

# @app.post('/request/edit/<request_id>') # Remove
# def edit_request(request_id):
    
#     if "user_id" in session:
#         user_id = session["user_id"]
#         uid = session["user_uid"]
        
#         title = request.form.get("title")
#         type = request.form.get("type")
#         eqpt_id = request.form.get("eqpt_id")
        
#         if type == "Equipment":
#             eqpt = {
#                 "id": eqpt_id,
#                 "name": Eqpt_db.get_eqpt_by_id(eqpt_id)["name"] 
#             }
#         else:
#             eqpt = "None"
            
            
#         quantity = request.form.get("quantity")
#         date_from = request.form.get("date_from")
#         date_to = request.form.get("date_to")
#         purpose = request.form.get("purpose")
#         recipient = request.form.get("recipient")
#         sender = {
#             "_id": user_id,
#             "uid": uid  
                  
#         }
#         status = "Pending"
#         now = datetime.now().strftime
#         month = now("%B")
#         date = now("%d")
#         year = now("%Y")
#         date_submitted = "{0} {1}, {2}".format(month, date, year)
#         date_time = datetime.now()
        
#         if recipient == "Admin":
#             role = "Admin"
#             id = User_db.get_user_by_role_one(role)["_id"]
            
#             recipient_dtls = {
#                 "position": "Admin",
#                 "id": id
#             }
#             dtls = Request(title, type, eqpt, quantity, date_from, date_to, purpose, sender, recipient_dtls, status, date_submitted, date_time)
#             updated = Request_db.update_request_dtls(request_id,dtls)
            
#             if updated:
#                 # flash("Request edited successfully!", "success")
#                 # return redirect(url_for('view_request', request_id=request_id))
#                 return jsonify({"message" : 'Request edited successfully!', "status" : "success"})                                                   
#             else:
#                 # flash('An error occurred! Try again', "danger")
#                 # return redirect(url_for('view_request', request_id=request_id))
#                 return jsonify({"message" : 'An error occurred! Try again', "status" : "danger"})

#         elif recipient == "software":
#             stack = "Software"
#             id = User_db.get_lead(stack)["_id"]
            
#             recipient_dtls = {
#                 "position": "Software",
#                 "id": id
#             }
#             dtls = Request(title, type, eqpt, quantity, date_from, date_to, purpose, sender, recipient_dtls, status, date_submitted, date_time)
#             updated = Request_db.update_request_dtls(request_id,dtls)
#             if updated:
#                 # flash("Request edited successfully!", "success")
#                 # return redirect(url_for('view_request', request_id=request_id))
#                 return jsonify({"message" : 'Request edited successfully!', "status" : "success"})  
#             else:
#                 # flash('An error occurred! Try again', "danger")
#                 # return redirect(url_for('view_request', request_id=request_id))
#                 return jsonify({"message" : 'An error occurred! Try again', "status" : "danger"})

#         elif recipient == "hardware":
#             stack="Hardware" 
#             id = User_db.get_lead(stack)["_id"]
#             recipient_dtls = {
#                 "position": "Hardware",
#                 "id": id
#             }
        
#             dtls = Request(title, type, eqpt, quantity, date_from, date_to, purpose, sender, recipient_dtls, status, date_submitted, date_time)
#             updated = Request_db.update_request_dtls(request_id,dtls)
#             if updated:
#                 return jsonify({"message" : 'Request edited successfully!', "status" : "success"})  
#             else:
#                 return jsonify({"message" : 'An error occurred! Try again', "status" : "danger"})
#         else:
#             return jsonify({"message" : 'permission not granted', "status" : "info"})                                                   
#     else:
#          return jsonify({"message" : 'You are not logged in!', "status" : "info"})

# @app.get('/request/delete/<request_id>') # Who can delete a request?
# def delete_request(request_id):
    
#     if "user_id" in session:
            
#         deleted = Request_db.delete_request(request_id)
        
#         if deleted:
#             return jsonify({"message" : 'Request deleted successfully!', "status" : "success"}), 200     
#         else:
#             return jsonify({"message" : 'The request was unsuccessful!', "status" : "danger"}), 500  
#     else:
#          return jsonify({"message" : 'You are not logged in!', "status" : "info"}), 401
  
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
    
# @app.post('/todo/create') 
# def create_todo():
    
#     if "user_id" in session:
#         user_id = session["user_id"]
#         description = request.get_json()['description']
        
#         dtls = {
#             "uid": user_id,
#             "description": description,
#             "date_time": datetime.now(),
#             "completed": False
#         }
#         id = str(Todos_db.create_todo(dtls))
        
#         return jsonify({
#             'description': description,
#             'id' : id
#         })
    
#     else:
#         # flash  ('you are not logged in!', "danger")
#         # return redirect(url_for('login')) 
#         return jsonify({"message" : 'You are not logged in!', "status" : "info"})

# @app.get('/todo/delete/<todo_id>')
# def delete_todo(todo_id):    
#     if "user_id" in session:        
#         deleted = Todos_db.delete_todo(todo_id)
        
#         if deleted:
#             return jsonify({
#                 'description':"deleted"
#             })
#         else:
#             # flash('An error occurred! Try again', "danger")
#             # return redirect(url_for('view_request', request_id=request_id))
#             return jsonify({"message" : 'An error occurred! Try again', "status" : "danger"})
#     else:
#         # flash  ('you are not logged in!', "danger")
#         # return redirect(url_for('login')) 
#         return jsonify({"message" : 'You are not logged in!', "status" : "info"})

# @app.post('/todo/<todo_id>/set-completed')
# def mark_completed(todo_id):    
    
#     if "user_id" in session:   
#         user_id = session["user_id"]
        
#         status = request.get_json()['completed']
#         dtls = {
#             "completed": status
#         }     
#         marked = Todos_db.update_todo(todo_id, dtls)
#         todo = Todos_db.get_specific_todo(user_id, todo_id)
#         if marked:
#             return jsonify({
#                 'id': todo_id,
#                 'description': todo["description"],
#                 'completed':status  
#             })
#         else:
#             # flash('An error occurred! Try again', "danger")
#             # return redirect(url_for('view_request', request_id=request_id))
#             return jsonify({"message" : 'An error occurred! Try again', "status" : "danger"})
#     else:
#         # flash  ('you are not logged in!', "danger")
#         # return redirect(url_for('login')) 
#         return jsonify({"message" : 'You are not logged in!', "status" : "info"})


# @app.post('/todos/filter')
# def task_filter():
    
#     if "user_id" in session:
#         user_id = session["user_id"]
        
#         option = request.get_json()['filter']
#         todos = list(Todos_db.get_todos_by_user_id(user_id))
#         app.logger.info(option)
        
#         taskCompleted = 0
#         if option == "week":
#             for todo in todos:
#                 if todo["completed"]==True:
#                     if (todo["date_time"]).strftime("%U")==datetime.now().strftime("%U"):
#                         taskCompleted = int(taskCompleted) + 1
#                     else:
#                         continue
#                 else:
#                     continue
            
#             return jsonify({ 'taskCompleted': taskCompleted})
        
#         elif option == "month":
#             for todo in todos:
#                 if todo["completed"]==True:
#                     if (todo["date_time"]).strftime("%m")==datetime.now().strftime("%m"):
#                         taskCompleted = int(taskCompleted) + 1
#                     else:
#                         continue
#                 else:
#                     continue
#             return jsonify({ 'taskCompleted': taskCompleted})
            
                
#         elif option == "year":
#             for todo in todos:
#                 if todo["completed"]==True:
#                     if (todo["date_time"]).strftime("%Y")==datetime.now().strftime("%Y"):
#                         taskCompleted = int(taskCompleted) + 1
#                     else:
#                         continue
#                 else:
#                     continue
#             return jsonify({ 'taskCompleted': taskCompleted})
#     else:
#         # flash  ('you are not logged in!', "danger")
#         # return redirect(url_for('login')) 
#         return jsonify({"message" : 'You are not logged in!', "status" : "info"})


# @app.get('/all/todos')
# def all_todos():
#     if "user_id" in session:
#         user_id = session["user_id"]
#         user_profile = User_db.get_user_by_oid(user_id)
#         all_todos = list(Todos_db.get_todos_by_user_id(user_id))
        
#         return render_template('pages/all_todos.html', all_todos=all_todos, user_profile=user_profile)

#     else:
#         # flash  ('you are not logged in!', "danger")
#         # return redirect(url_for('login')) 
#         return jsonify({"message" : 'You are not logged in!', "status" : "info"})

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
        return jsonify({"message" : 'You are not logged in!', "status" : "info"})
        