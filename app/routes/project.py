from flask import Blueprint, request, jsonify
from models.models import generate, updatePwd, Reportdb, Requestdb, Todosdb, Notificationsdb, Notification, AllowedExtension
from funcs import convert_to_json_serializable
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from flask_mail import Message
from app.extensions import mail
from datetime import datetime, timedelta
from funcs import *
import json
from werkzeug.utils import secure_filename
from models.project import Project, Projectdb
from models.user import Userdb

project_bp = Blueprint('project', __name__, url_prefix='/project')

User_db = Userdb()
Project_db = Projectdb()
Notifications = Notificationsdb()

@project_bp.post('/create') 
@jwt_required()
def create_project():
    try:
        uid = get_jwt_identity()
        
        data = request.json
        name = data.get("name")
        description = data.get("description")
        objectives = data.get("objectives") 
        leads = data.get("leads")
        team_members = data.get("team_members") 
        stack = data.get("stack").lower()
        deadline = data.get("deadline")
        
        if Project_db.existing_project_name(name):
            response = convert_to_json_serializable({"message" : f"Project with name '{name}' already exists.", "status": "error"})
            return(response)
            
        team_avatars = []
        
        for lead in leads:
            profile = User_db.get_user_by_uid(lead['id'])
            if not profile:
                continue
            
            avatar = profile['avatar']
            if not avatar:
                team_avatars.append(avatar['secure_url'])
            else: team_avatars.append(None)
                    
        for member in team_members:
            profile = User_db.get_user_by_uid(member['id'])
            if not profile:
                continue
                    
            avatar = profile['avatar']
            if not avatar :
                team_avatars.append(avatar['secure_url'])
            else: team_avatars.append(None)
            
        project_id = get_la_code('pjt')
           
        project = Project(project_id=project_id, name=name, description=description, objectives=objectives, leads=leads, team_members=team_members, team_avatars=team_avatars, stack=stack, created_at=uid, deadline=deadline) 
        
        project_created = Project_db.create_project(project)
        if not project_created:
            response = convert_to_json_serializable({"message" : "Unable to create project. Please try again", "status" : "error"})
        
        not_title = "New Project"
        not_receivers = leads + team_members
        not_type = "Project"
        not_message = f"You have been added to a new project '{name}'. Check it out in your projects tab!"
        notification = Notification(not_title, not_receivers, not_type, not_message)
        
        response = convert_to_json_serializable({"message" : "Project created successfully!", "status" : "success", "project_id" : project_id})
        Notifications.send_notification(notification)
            
    except Exception as e:
        return jsonify({return_error(e)}), 500

@project_bp.get('/get_project/<project_id>')
@jwt_required()
def view_project(project_id):
    try:
        project = Project_db.get_by_project_id(project_id)
        
        if not project:
            return jsonify({"message": "Project with ID '{project_id}' not found", "status": "error"}), 404
            
        response = convert_to_json_serializable({"project": project, "status": "success", "message": "Project fetched successfully"})
        return jsonify(response), 200
    
    except Exception as e:
        return jsonify(return_error(e)), 500
    
@project_bp.get('/get_all')
@jwt_required()
def get_all_projects():
    try:
        uid = get_jwt_identity()
        user_role = get_jwt()['user_role']
        stack = get_jwt()['stack']
        
        if user_role=="Admin":
            projects = list(Project_db.get_all())
        elif user_role == "Lead":
            projects = list(Project_db.get_by_stack(stack, uid))
        else: projects = list(Project_db.get_by_isMember(uid))
        
        response = convert_to_json_serializable({"projects": projects, "status": "success"})
        return jsonify(response), 200
    
    except Exception as e:
        return jsonify({"message": f'Something went wrong: {e}', 'status': "error"}), 500
  
@project_bp.patch('/project/completed/<project_id>')
@jwt_required()
def mark_project_completed(project_id):
    try:
        project = Project_db.get_by_project_id(project_id)
        
        if (not Project_db.project_exists(project_id)):
            return jsonify({"message": "Invalid project id", "status": "error"}), 400
        
        name = Project_db.get_project_name(project_id)
        members = Project_db.get_project_members(project_id)
        members = [member['id'] for member in members]
        
        if (project['status'] == 'Completed'):
            return jsonify({"message": 'Project marked as complete', "status" : "success"}), 200
        
        marked = Project_db.mark_project(project_id, "Completed")
        
        not_title = "Project Marked as Complete"
        not_receivers = members
        not_type = "Project"
        not_message = f"Project '{name}' has been marked as complete. Check it out in your projects tab!"
        notification = Notification(not_title, not_receivers, not_type, not_message)
        
        if marked: 
            Notifications.send_notification(notification)
            return jsonify({"message": 'Project marked as complete', "status" : "success"}), 200
        else:
            return jsonify({"message" : 'An error occurred! Try again', "status" : "danger"}), 500
        
    except Exception as e:
        return jsonify({"message": f'Something went wrong: {e}', 'status': "error"}), 500
    
@project_bp.patch('/project/incomplete/<project_id>') 
@jwt_required()
def mark_project_incomplete(project_id):
    try:
        project = Project_db.get_by_project_id(project_id)
        
        if (not Project_db.project_exists(project_id)):
            return jsonify({"message": "Invalid project id", "status": "error"}), 400
        
        name = Project_db.get_project_name(project_id)
        members = Project_db.get_project_members(project_id)
        members = [member['id'] for member in members]
        
        if (project['status'] == 'Uncompleted'):
            return jsonify({"message": 'Project marked as incomplete', "status" : "success"}), 200
        
        marked = Project_db.mark_project(project_id, "Uncompleted")
        
        not_title = "Project Marked as Incomplete"
        not_receivers = members
        not_type = "Project"
        not_message = f"Project '{name}' has been marked as incomplete. Check it out in your projects tab!"
        notification = Notification(not_title, not_receivers, not_type, not_message)
        
        if marked: 
            Notifications.send_notification(notification)
            return jsonify({"message": 'Project marked as incomplete', "status" : "success"}), 200
        else:
            return jsonify({"message" : 'An error occurred! Try again', "status" : "danger"}), 500
        
    except Exception as e:
        return jsonify({"message": f'Something went wrong: {e}', 'status': "error"}), 500

@project_bp.patch('/project/edit/<project_id>') # Add notifications
@jwt_required()
def edit_project(project_id): # Who can edit a project? Name, description, objectives, team_members, leads, deadline
    try:
        if (not Project_db.project_exists(project_id)):
            return jsonify({"message": "Invalid project id", "status": "error"}), 400
        
        data = request.json
        print(data)
        
        updated = Project_db.update_project_dtls(project_id, data)
        if updated:
            return jsonify({"message": "Project details edited successfully!", "status" : "success"}), 200
        else:
            return jsonify({"message" : 'An error occurred! Try again', "status" : "danger"}), 500
        
    except Exception as e:
        import traceback
        print("Traceback:", traceback.format_exc())
        return {'message': f'Something went wrong: {str(e)}', 'status': 'error', 'traceback': traceback}, 500
        # return jsonify({"message": f'Something went wrong: {e}', 'status': "error"}), 500
    
@project_bp.delete('/project/delete/<project_id>')
@jwt_required()
def delete_project(project_id):
    try:
        if (not Project_db.project_exists(project_id)):
            return jsonify({"message": "Invalid project id", "status": "error"}), 400
        
        name = Project_db.get_project_name(project_id)
        members = Project_db.get_project_members(project_id)
        members = [member['id'] for member in members]
        deleted = Project_db.delete_project(project_id, name)
            
        not_title = "Project Deleted"
        not_receivers = members
        not_type = "Project"
        not_message = f"Project '{name}' has been deleted."
        notification = Notification(not_title, not_receivers, not_type, not_message)
            
        if deleted:
            Notifications.send_notification(notification)
            return jsonify({"message": "Project deleted successfully!", "status" : "success"}), 200
        else:
            return jsonify({"message": 'The project could not be deleted!', "status" : "danger"}), 500
        
    except Exception as e:
        return jsonify({"message": f'Something went wrong: {e}', 'status': "error"}), 500

@project_bp.patch('/project/submit_doc/<project_id>')
@jwt_required()
def submit_project_doc(project_id): # Add notification
    try:
        if (not Project_db.project_exists(project_id)):
            return jsonify({"message": "Invalid project id", "status": "error"}), 400
        
        submission = request.files["file"]
        filename = secure_filename(submission.filename)
        
        if not submission:
            return jsonify({"message": "No doc attached", "status": "error"}), 400
        
        if not check_file_size(submission):
            return jsonify({"message": "Doc size exceeds 1MB", "status": "error"}), 400
        
        if not AllowedExtension.files(filename):
            return jsonify({"message": "Invalid doc type", "status": "error"}), 400                            
        
        try:
            uploaded = upload_func(submission, f"SSRL_Lab_App/projects/{project_id}")
            
            if not uploaded:
                return jsonify({"message" : 'An error occurred! Try again', "status" : "danger"}), 500

            print(uploaded)
            project_submission = {"filename": filename, "download_link": uploaded["secure_url"], "date_submitted": datetime.now()}
            submitted = Project_db.submit_doc(project_id, project_submission)
                
            if not submitted:
                return jsonify({"message" : 'An error occurred! Try again', "status" : "danger"}), 500
            
        except Exception as e:
            return jsonify({"message" : f"Couldn't upload your project at the moment! {e}", "status" : "danger"}),500
        
        return jsonify({"submission": project_submission, "status" : "success"}), 200
        
    except Exception as e:
        return jsonify({"message": f'Something went wrong: {e}', 'status': "error"}), 500
    
@project_bp.patch('/project/submit_link/<project_id>') # Validate link input on frontend
def submit_project_link(project_id): # Add notification
    try:    
        if (not Project_db.project_exists(project_id)):
            return jsonify({"message": "Invalid project id", "status": "error"}), 400
        
        data = request.json
        title = data.get('title')
        link = data.get('link')
        
        link_submission = {"title": title, "link": link, "date_submitted": get_date_now()}
        submitted = Project_db.submit_link(project_id, link_submission)
        
        if submitted:
            return jsonify({"message": 'Project submitted successfully', "status" : "success"}), 200
        else:
            return jsonify({"message" : 'An error occurred! Try again', "status" : "danger"}), 500
        
    except Exception as e:
        return jsonify({"message": f'Something went wrong: {e}', 'status': "error"}), 500
        
        
@project_bp.post('/project/send_announcement/<project_id>')
@jwt_required()
def send_project_announcement(project_id):
    try:    
        uid = get_jwt_identity()
        if (not Project_db.project_exists(project_id)):
            return jsonify({"message": "Invalid project id", "status": "error"}), 400
        
        announcement = request.json.get('announcement')
        receivers = request.json.get('receivers') 
        
        all = Project_db.get_project_members(project_id)
        leads = Project_db.get_project_leads(project_id)
        
        recepient = (leads, all)[receivers == "all"]
        recepient.append(uid)
        
        not_title = f"New Project Announcement: {Project_db.get_project_name(project_id)}"
        not_receivers = recepient
        not_type = "Project"
        not_message = announcement
        not_status = "unread"
        not_sentAt = datetime.now()
        notification = Notification(not_title, not_receivers, not_type, not_message, not_status, not_sentAt)
        
        Notifications.send_notification(notification)

        return jsonify({"message": "Announcement made successfully", "status" : "success"}), 200

    except Exception as e:
        return jsonify({"message": f'Something went wrong: {e}', 'status': "error"}), 500
    
@project_bp.post('/project/send_feedback/<project_id>') 
@jwt_required()
def send_feedback(project_id):
    try:
        feedback = request.json.get('feedback')
        user_id = get_jwt_identity()
        user_profile = User_db.get_user_by_uid(user_id)
        
        sender = user_profile.get('fullname')
        
        if (not Project_db.project_exists(project_id)):
            return jsonify({"message": "Invalid project id", "status": "error"}), 400
        
        all = Project_db.get_project_members(project_id)
        project_name = {Project_db.get_project_name(project_id)}
        
        send_feedback = Project_db.send_feedback(project_id, sender, feedback)
        if not send_feedback:
            return jsonify({"message": "Could not send feedback right now! Try again", "status" : "danger"}), 500
        
        not_title = f"New Project Feedback: {project_name}"
        not_receivers = all
        not_type = "Project"
        not_message = f"A new feedback has been created for {project_name}, check it out in the projects tab."
        not_status = "unread"
        not_sentAt = datetime.now()
        notification = Notification(not_title, not_receivers, not_type, not_message, not_status, not_sentAt)
        
        Notifications.send_notification(notification)
        
        return ({"message": "Feedback sent successfully", "status" : "success"}), 200
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(error_details)
        return jsonify({"message": f'Something went wrong: {e}', 'status': "error"}), 500
    

