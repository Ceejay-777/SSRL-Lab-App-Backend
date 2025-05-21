from flask import Blueprint, request, jsonify
from models.models import generate, Notificationsdb, Notification, AllowedExtension
from funcs import convert_to_json_serializable
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from flask_mail import Message
from app.extensions import mail
from datetime import datetime, timedelta
from funcs import *
import json
from werkzeug.utils import secure_filename
from models.project import Project, Projectdb
from models.request import Request, Requestdb
from models.report import Report, Reportdb
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
            response = {"message" : f"Project with name '{name}' already exists.", "status": "error"}
            return jsonify(response)
            
        for lead in leads:
            profile = User_db.get_user_by_uid(lead["id"])
            if not profile:
                continue
            
            avatar = profile['avatar']
            if avatar:
                lead.update({"avatar": avatar['secure_url']})
            else: lead.update({"avatar": None})
                    
        for member in team_members:
            profile = User_db.get_user_by_uid(member['id'])
            if not profile:
                continue
                    
            avatar = profile['avatar']
            if avatar:
                member.update({"avatar": avatar['secure_url']})
            else: member.update({"avatar": None})
            
        project_id = get_la_code('pjt')
           
        project = Project(project_id=project_id, name=name, description=description, objectives=objectives, leads=leads, team_members=team_members, stack=stack, deadline=deadline, created_by=uid) 
        
        project_created = Project_db.create_project(project)
        if not project_created:
            response = convert_to_json_serializable({"message" : "Unable to create project. Please try again", "status" : "error"})
            return jsonify(response), 500
        
        project = Project_db.get_by_project_id(project_id=project_id)
        
        leads_id = [lead['id'] for lead in leads]
        team_members_id = [member['id'] for member in team_members]
        
        not_title = "New Project"
        not_receivers = leads_id + team_members_id
        not_type = "Project"
        not_message = f"You have been added to a new project '{name}'. Check it out in your projects tab!"
        notification = Notification(not_title, not_receivers, not_type, not_message)
        
        response = convert_to_json_serializable({"message" : "Project created successfully!", "status" : "success", "project" : project})
        Notifications.send_notification(notification)
        return jsonify(response), 200
            
    except Exception as e:
        return jsonify(return_error(e)), 500

@project_bp.get('/get/<project_id>')
@jwt_required()
def view_project(project_id):
    try:
        print(project_id)
        project = Project_db.get_by_project_id(project_id)
        
        if not project:
            return jsonify({"message": f"Project with ID '{project_id}' not found", "status": "error"}), 404
            
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
            projects = list(Project_db.get_by_stack(stack))
        else: projects = list(Project_db.get_by_isMember(uid))
        
        total_projects = len(projects)
        
        response = convert_to_json_serializable({"projects": projects, "status": "success", "message": "Projects fetched successfully", "total_projects": total_projects})
        return jsonify(response), 200
    
    except Exception as e:
        return jsonify({"message": f'Something went wrong: {e}', 'status': "error"}), 500
  
@project_bp.patch('/mark_as_completed/<project_id>')
@jwt_required()
def mark_project_completed(project_id):
    try:
        project = Project_db.get_by_project_id(project_id)
        
        if not project:
            return jsonify({"message": f"Project with ID '{project_id}' not found", "status": "error"}), 404
        
        name = project.get('name')
        members = project['leads'] + project['team_members']
        members_id = [member['id'] for member in members]
        
        if (project['status'] == 'completed'):
            return jsonify({"message": 'Project marked as complete', "status" : "success"}), 200
        
        marked = Project_db.mark_project(project_id, "completed")
        if not marked:
            return jsonify({"message" : 'An error occurred! Please try again', "status" : "danger"}), 500
        
        not_title = "Project Marked as Complete"
        not_receivers = members_id
        not_type = "Project"
        not_message = f"Project '{name}' has been marked as complete. Check it out in your projects tab!"
        notification = Notification(not_title, not_receivers, not_type, not_message)
        
        Notifications.send_notification(notification)
        return jsonify({"message": 'Project marked as complete', "status" : "success"}), 200
        
    except Exception as e:
        return jsonify(return_error(e)), 500
    
@project_bp.patch('/mark_as_incompleted/<project_id>')
@jwt_required()
def mark_project_incompleted(project_id):
    try:
        project = Project_db.get_by_project_id(project_id)
        if not project:
            return jsonify({"message": "Project with ID '{project_id}' not found", "status": "error"}), 404
        
        name = project.get('name')
        members = project['leads'] + project['team_members']
        members_id = [member['id'] for member in members]
        status = project['status']
        
        if (status == 'incompleted'):
            return jsonify({"message": 'Project marked as incomplete', "status" : "success"}), 200
        
        marked = Project_db.mark_project(project_id, "incompleted")
        if not marked:
            return jsonify({"message" : 'An error occurred! Please try again', "status" : "danger"}), 500
        
        not_title = "Project Marked as Incomplete"
        not_receivers = members_id
        not_type = "Project"
        not_message = f"Project '{name}' has been marked as incomplete. Check it out in your projects tab!"
        notification = Notification(not_title, not_receivers, not_type, not_message)
        
        Notifications.send_notification(notification)
        return jsonify({"message": 'Project marked as incomplete', "status" : "success"}), 200
        
    except Exception as e:
        return jsonify(return_error(e)), 500
    
@project_bp.patch('/edit/<project_id>') 
@jwt_required()
def edit_project(project_id): # Name, description, objectives, team_members, leads, deadline
    try:
        data = request.json
        uid = get_jwt_identity()
        role = get_jwt()['user_role']
        
        project = Project_db.get_by_project_id(project_id)
        if not project:
            return jsonify({"message": f"Project with ID '{project_id}' not found", "status": "error"}), 404
        
        leads = project['leads']
        leads_ids = [lead['id'] for lead in leads]
        team_members = project['team_members']
        team_members_ids = [team_member['id'] for team_member in team_members]
        name = project['name']
        
        if role != 'Admin' or uid not in leads:
            return jsonify({"message": "You don't have permission to edit this project. Contact the leads on this project", 'status': 'error'})
        
        updated = Project_db.update_project_details(project_id, data)
        if not updated:
            return jsonify({"message" : 'An error occurred! Try again', "status" : "danger"}), 500
        
        not_title = "Project Edited"
        not_receivers = leads_ids + team_members_ids
        not_type = "Project"
        not_message = f"Project '{name}' has been edited by {uid}. Check it out in your projects tab!"
        notification = Notification(not_title, not_receivers, not_type, not_message)
        
        Notifications.send_notification(notification)
        return jsonify({"message": "Project details edited successfully!", "status" : "success"}), 200
        
    except Exception as e:
        return jsonify(return_error(e)), 500
    
@project_bp.delete('/delete/<project_id>')
@jwt_required()
def delete_project(project_id):
    try:
        uid = get_jwt_identity()
        
        project = Project_db.get_by_project_id(project_id)
        if not project:
            return jsonify({"message": f"Project with ID '{project_id}' not found", "status": "error"}), 404
        
        name = project['name']
        members = project['leads'] + project['team_members']
        members_ids = [member['id'] for member in members]
        deleted = Project_db.delete_project(project_id)
            
        if not deleted:
            return jsonify({"message": 'The project could not be deleted. Please try again', "status" : "danger"}), 500
        
        not_title = "Project Deleted"
        not_receivers = members_ids
        not_type = "Project"
        not_message = f"Project '{name}' has been deleted by {uid}."
        notification = Notification(not_title, not_receivers, not_type, not_message)
    
        Notifications.send_notification(notification)
        return jsonify({"message": "Project deleted successfully!", "status" : "success"}), 200
        
    except Exception as e:
        return jsonify(return_error(e)), 500

@project_bp.patch('/submit_doc/<project_id>')
@jwt_required()
def submit_project_doc(project_id): 
    try:
        uid = get_jwt_identity()
        
        project = Project_db.get_by_project_id(project_id)
        if not project:
            return jsonify({"message": f"Project with ID '{project_id}' not found", "status": "error"}), 404
        
        submission = request.files["doc"]
        filename = secure_filename(submission.filename)
        
        if not submission:
            return jsonify({"message": "No document attached", "status": "error"}), 400
        
        if not check_file_size(submission, max_size_mb=2):
            return jsonify({"message": "Document size exceeds 2MB", "status": "error"}), 400
        
        if not AllowedExtension.files(filename):
            return jsonify({"message": "Invalid document type. Valid types are 'pdf', 'doc', 'docs','docx' and 'txt' ", "status": "error"}), 400        
        
        project = Project_db.get_by_project_id(project_id)
        if not project:
            return jsonify({"message": f"Project with ID '{project_id}' not found", "status": "error"}), 404
        
        name = project['name']
        members = project['leads'] + project['team_members']
        members_ids = [member['id'] for member in members]
        
        try:
            uploaded = upload_file(submission, f"SSRL_Lab_App/project_submissions/{project_id}")
            print(uploaded)
            
            if not uploaded:
                return jsonify({"message" : 'An error occurred! Try again', "status" : "error"}), 500

        except Exception as e:
            return jsonify({"message" : f"Couldn't upload your project at the moment! {e}", "status" : "error"}),500
        
        project_submission = {"filename": filename, "download_link": uploaded["secure_url"], "submitted_at": datetime.now()}
        
        submitted = Project_db.submit_doc(project_id, project_submission)
        if not submitted:
            return jsonify({"message" : 'An error occurred! Try again', "status" : "error"}), 500
        
        not_title = "Project Document Submission"
        not_receivers = members_ids
        not_type = "Project"
        not_message = f"A document: {filename} has been submitted for project '{name}' by {uid}."
        notification = Notification(not_title, not_receivers, not_type, not_message)
    
        Notifications.send_notification(notification)
        
        return jsonify({"message": "Document submitted successfully", "status" : "success"}), 200
        
    except Exception as e:
        return jsonify(return_error(e)), 500
    
@project_bp.patch('/submit_link/<project_id>') # Validate link input on frontend
@jwt_required()
def submit_project_link(project_id): 
    try:    
        uid = get_jwt_identity()
        data = request.json
        title = data.get('title')
        link = data.get('link')
        
        project = Project_db.get_by_project_id(project_id)
        if not project:
            return jsonify({"message": f"Project with ID '{project_id}' not found", "status": "error"}), 404
        
        name = project['name']
        members = project['leads'] + project['team_members']
        members_ids = [member['id'] for member in members]
        
        link_submission = {"title": title, "link": link, "date_submitted": datetime.now()}
        
        submitted = Project_db.submit_link(project_id, link_submission)
        if not submitted:
            return jsonify({"message" : 'An error occurred! Try again', "status" : "error"}), 500
        
        not_title = "Project Link addition"
        not_receivers = members_ids
        not_type = "Project"
        not_message = f"A link has been added for project '{name}' by {uid}."
        notification = Notification(not_title, not_receivers, not_type, not_message)
    
        Notifications.send_notification(notification)
        
        return jsonify({"message": 'Link submitted successfully', "status" : "success"}), 200
        
    except Exception as e:
        return jsonify(return_error(e)), 500
        
@project_bp.post('/send_announcement/<project_id>')
@jwt_required()
def send_project_announcement(project_id):
    try:    
        uid = get_jwt_identity()
        announcement = request.json.get('announcement')
        receivers = request.json.get('receivers') 
        
        project = Project_db.get_by_project_id(project_id)
        if not project:
            return jsonify({"message": "Project with ID '{project_id}' not found", "status": "error"}), 404

        name = project['name']
        
        leads = project['leads']
        leads_ids = [lead['id'] for lead in leads]
        
        members = project['team_members']
        members_ids = [member['id'] for member in members]
        
        all = leads_ids  + members_ids
        recepient = (leads, all)[receivers == "all"]
        recepient.append(uid)
        
        not_title = f"New Project Announcement: {name}"
        not_receivers = recepient
        not_type = "Project"
        not_message = announcement
        notification = Notification(not_title, not_receivers, not_type, not_message)
        
        Notifications.send_notification(notification)

        return jsonify({"message": "Announcement made successfully", "status" : "success"}), 200

    except Exception as e:
        return jsonify(return_error(e)), 500
    
@project_bp.patch('/send_feedback/<project_id>') 
@jwt_required()
def send_feedback(project_id):
    try:
        uid = get_jwt_identity()
        feedback = request.json.get('feedback')
        
        user = User_db.get_user_by_uid(uid)
        sender = user.get('firstname') + " " + user.get('surname')
        
        project = Project_db.get_by_project_id(project_id)
        if not project:
            return jsonify({"message": f"Project with ID '{project_id}' not found", "status": "error"}), 404
        
        name = project['name']
        
        leads = project['leads']
        leads_ids = [lead['id'] for lead in leads]
        
        members = project['team_members']
        members_ids = [member['id'] for member in members]
        
        send_feedback = Project_db.send_feedback(project_id, sender, feedback)
        if not send_feedback:
            return jsonify({"message": "Could not send feedback right now! Try again", "status" : "error"}), 500
        
        not_title = f"New Project Feedback: {name}"
        not_receivers = leads_ids + members_ids
        not_type = "Project"
        not_message = f"A new feedback has been created for project {name} by {uid}, check it out in the projects tab."
        notification = Notification(not_title, not_receivers, not_type, not_message)
        
        Notifications.send_notification(notification)
        
        return ({"message": "Feedback sent successfully", "status" : "success"}), 200
    
    except Exception as e:
        return jsonify(return_error(e)), 500
    

