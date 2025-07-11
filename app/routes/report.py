from flask import Blueprint, request, jsonify
from models.models import Notificationsdb, AllowedExtension, Notification
from funcs import convert_to_json_serializable
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from datetime import datetime
from funcs import *
from werkzeug.utils import secure_filename
from models.user import Userdb
from models.project import Projectdb
from models.request import Request, Requestdb
from models.report import Report, Reportdb
from models.todo import Todo, Todosdb

report_bp = Blueprint('report', __name__, url_prefix='/report')

User_db = Userdb()
Request_db = Requestdb()
Report_db = Reportdb()
Project_db = Projectdb()
Todos_db = Todosdb()
Notifications = Notificationsdb()

@report_bp.post('/create')
@jwt_required()
def create_report():
    try:
        uid = get_jwt_identity()
        user = User_db.get_user_by_uid(uid)
        name = user.get('surname') + " " + user.get('firstname')
        stack = user['stack']
        
        avatar = user.get('avatar')
        if avatar:
            avatar = avatar['secure_url']
        
        sender = {'id':uid, 'name':name, 'avatar': avatar}
        
        data = request.json
        report_type = data.get('report_type')
        title = data.get('title')
        receivers = data.get('receivers')
        
        if report_type == "activity":
            duration = data.get('duration') 
            completed = data.get('completed', [])
            ongoing = data.get('ongoing', [])
            next = data.get('next', [])
            report_details = {'duration': duration, 'completed': completed, 'ongoing': ongoing, 'next': next}
            
        elif report_type == "project":
            summary = data.get('summary')   
            report_details = {'summary': summary}
            
        else:
            return jsonify({"message": "Invalid report type", "status": "error"}), 400
        
        while True:
            report_id = get_la_code('rpt')
            if not Report_db.get_by_report_id(report_id):
                break
        
        report = Report(report_type=report_type, title=title, sender=sender, receivers=receivers, report_details=report_details, stack=stack, report_id=report_id)
        
        report_created = Report_db.create_report(report)
        if not report_created:
            return jsonify({"message": "Failed to create report", "status": "error"}), 500
        
        receiver_ids = [receiver['id'] for receiver in receivers]
        
        not_title = "Report Submission"
        not_receivers = receiver_ids
        not_type = "Report"
        not_message = f"You have received a new report from {uid}. Check it out in your reports tab!"
        notification = Notification(not_title, not_receivers, not_type, not_message)
    
        Notifications.send_notification(notification)
            
        return jsonify({"message": "Report created successfully!", "status": "success"}), 200
    
    except Exception as e:
        return jsonify(return_error(e)), 500
    
@report_bp.get('/get_all')
@jwt_required()
def get_all_reports():
    try:
        user_uid = get_jwt_identity()
        info = get_jwt()
        user_role = info['user_role']
        stack = info['stack']
        
        if user_role == 'Admin':
            reports = Report_db.get_all()
        elif user_role == 'Lead':
            reports = Report_db.get_by_stack(stack)
        else:
            reports = Report_db.get_by_isMember(user_uid)
            
        response = convert_to_json_serializable({'reports': list(reports), 'status': 'success'})
        return jsonify(response), 200
    
    except Exception as e:
        return jsonify(return_error(e)), 500
    
@report_bp.get('/get/<report_id>')
@jwt_required()
def get_one(report_id):
    try:
        report = Report_db.get_by_report_id(report_id)
        if not report:
            return jsonify({"message": f"Report with id '{report_id}' not found", "status": "error"}), 404
        
        response = convert_to_json_serializable({'report': report, 'status': 'success'}), 200
        return jsonify(response), 200
        
    except Exception as e:
        return jsonify(return_error(e)), 500
        
@report_bp.post('/send_feedback/<report_id>') 
@jwt_required()
@admin_and_lead_role_required
def give_feedback(report_id):
    try:
        uid = get_jwt_identity()
        user = User_db.get_user_by_uid(uid)
        sender = user['surname'] + ' ' + user['firsname']
        
        feedback = request.json.get("feedback")
        
        report = Report_db.get_by_report_id(report_id)
        if not report:
            return jsonify({"message": f"Report with id '{report_id}' not found", "status": "error"}), 404
        
        title = report.get('title')
        sender_id = report.get('sender').get('id')
        feedback_dtls = {"feedback": feedback, "created_at": datetime.now(), 'sender': sender}
        
        submitted = Report_db.give_feedback(report_id, feedback_dtls)
        if not submitted: 
            return jsonify({"message" : 'An error occured! Try again', "status" : "success"}), 500
        
        not_title = "New reeport feedback"
        not_receivers = sender_id
        not_type = "Report"
        not_message = f"A new feedback was just added to your report: {title}. Check it out in your reports tab!"
        notification = Notification(not_title, not_receivers, not_type, not_message)
    
        Notifications.send_notification(notification)
        
        return jsonify({"message": "Feedback sent successfully", "status": "success"}), 200
        
    except Exception as e:
        return jsonify(return_error(e)), 500
    
@report_bp.delete('/delete/<report_id>')
@jwt_required()
@admin_and_lead_role_required
def delete_report(report_id):
    try:
        report = Report_db.get_by_report_id(report_id)
        if not report:
            return jsonify({"message": f"Report with id '{report_id}' not found", "status": "error"}), 404
        
        delete_details = {"deleted_at": datetime.now()}
        
        deleted = Report_db.update_report_dtls(report_id, delete_details)
        if not deleted:
            return jsonify({"message" : "An error occured! Try again!", "status" : "error"}), 500
        
        return jsonify({"message" : "Report deleted successfully!", "status" : "success"}), 200
    
    except Exception as e:
        return jsonify(return_error(e)), 500
    
@report_bp.put('/add_doc/<report_id>')
@jwt_required()
def add_doc(report_id):
    try:
        uid = get_jwt_identity()
        
        report = Report_db.get_by_report_id(report_id)
        if not report:
            return jsonify({"message": f"Report with id '{report_id}' not found", "status": "error"}), 404
        
        title = report['title']
        receiver = report['receiver']
        
        doc = request.files.get("doc")
        if not doc:
            return jsonify({"message": "No file uploaded", "status": "error"})
        
        if not check_file_size(doc, max_size_mb=2):
            return jsonify({"message": "Document size exceeds 2MB", "status": "error"}), 400
        
        filename = secure_filename(doc.filename)
        if not AllowedExtension.files(filename):
            return jsonify({"message" : 'Invalid file format! Try again', "status" : "error"}), 401
        
        try:
            uploaded = upload_file(doc, f"SSRL_Lab_App/report_submissions/{report_id}")
            if not uploaded:
                return jsonify({"message" : 'File upload error! Try again', "status" : "danger"}), 500
            
        except Exception as e:
             return jsonify({"message": f'File upload error: {e}', 'status': "error"}), 500

        doc_submission = {"filename": filename, "download_link": uploaded['secure_url'], "submitted_at": datetime.now()}
        
        submitted = Report_db.add_doc(report_id, doc_submission)
        if not submitted:
            return jsonify({"message" : 'An error occurred! Try again', "status" : "danger"}), 500
        
        not_title = "Report Document Submission"
        not_receivers = receiver
        not_type = "Report"
        not_message = f"A document: {filename} has been submitted for report '{title}' by {uid}."
        notification = Notification(not_title, not_receivers, not_type, not_message)
    
        Notifications.send_notification(notification)
        
        return jsonify({"message": 'Document submitted successfully', "status" : "success"}), 200
        
    except Exception as e:
        return jsonify(return_error(e)), 500
    
@report_bp.put('/add_link/<report_id>')
@jwt_required()
def add_link(report_id):
    try:
        uid = get_jwt_identity()
        link = request.json.get('link')
        
        report = Report_db.get_by_report_id(report_id)
        if not report:
            return jsonify({"message": f"Report with id '{report_id}' not found", "status": "error"}), 404
        
        title = report['title']
        receiver = report['receiver']
        
        link_submission = {"link": link, "submitted_at": datetime.now()}
        
        submitted = Report_db.add_link(report_id, link_submission)
        if not submitted:
            return jsonify({"message" : 'An error occurred! Try again', "status" : "danger"}), 500
        
        not_title = "Report Link Submission"
        not_receivers = receiver
        not_type = "Report"
        not_message = f"A link has been submitted for report '{title}' by {uid}."
        notification = Notification(not_title, not_receivers, not_type, not_message)
    
        Notifications.send_notification(notification)
        
        return jsonify({"message": 'Link submitted successfully', "status" : "success"}), 200
    
    except Exception as e:
        return jsonify(return_error(e)), 500
