from flask import Blueprint, request, jsonify
from models.models import Reportdb, Todosdb, Notificationsdb, AllowedExtension, ActivityReport, ProjectReport
from funcs import convert_to_json_serializable
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from datetime import datetime
from funcs import *
from werkzeug.utils import secure_filename
from models.user import Userdb
from models.project import Projectdb
from models.request import Request, Requestdb

report_bp = Blueprint('report', __name__)

User_db = Userdb()
Request_db = Requestdb()
Report_db = Reportdb()
Project_db = Projectdb()
Todos_db = Todosdb()
Notifications = Notificationsdb()

@report_bp.post('/report/create')
@jwt_required()
def create_report():
    data = request.json
    report_type = data.get('report_type')
    title = data.get('title')
    receiver = data.get('receiver')
    uid = get_jwt_identity()
    
    sender = User_db.get_user_by_uid(uid)
    avatar = sender.get('avatar', 'NIL')
    stack = sender.get('stack')
    sender_name = sender.get('fullname')
    sender = {'id':uid, 'name':sender_name}
    
    if report_type == "activity":
        duration = data.get('duration') 
        completed = data.get('completed', [])
        ongoing = data.get('ongoing', [])
        next = data.get('next', [])
        report = ActivityReport(title=title, stack=stack, receiver=receiver, sender=sender, duration=duration, completed=completed, ongoing=ongoing, next=next, report_type=report_type, avatar=avatar)
    elif report_type == "project":
        summary = data.get('summary')   
        report = ProjectReport(title=title, stack=stack, summary=summary, report_type=report_type, receiver=receiver, sender=sender,  avatar=avatar) 
    else:
        return jsonify({"message": "Invalid report type", "status": "error"}), 400
    
    report_id = Report_db.insert_new(report)
    
    if report_id:
        return jsonify({"message": "Report created successfully!", "status": "success"}), 200
    else:
        return jsonify({"message": "Failed to create report", "status": "error"}), 500
    
@report_bp.get('/reports/get_all')
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
        return jsonify({"message": f'Something went wrong: {e}', 'status': "error"}), 500
    
@report_bp.get('/report/get_one/<report_id>')
@jwt_required()
def get_one(report_id):
    try:
        report = Report_db.get_by_report_id(report_id)
        
        if not report:
            return jsonify({"message": "Report not found", "status": "error"}), 404
        
        response = convert_to_json_serializable({'report': report, 'status': 'success'}), 200
        return jsonify(response), 200
        
    except Exception as e:
        return jsonify({"message": f'Something went wrong: {e}', 'status': "error"}), 500
        
@report_bp.post('/report/send_feedback/<report_id>') 
@jwt_required()
def give_feedback(report_id):
    try:
        feedback = request.json.get("feedback")
        report = Report_db.get_by_report_id(report_id)
        
        if not report:
            return jsonify({"message": "Report not found", "status": "error"}), 404
        
        feedback_dtls = {"feedback": feedback, "created_at": datetime.now()}
        submitted = Report_db.give_feedback(report_id, feedback_dtls)
        
        if not submitted: 
            return jsonify({"message" : 'An error occured! Try again', "status" : "success"}), 500
        
        return jsonify({"message": "Feedback sent successfully", "status": "success"}), 200
        
    except Exception as e:
        return jsonify({"message": f'Something went wrong: {e}', 'status': "error"}), 500
    
@report_bp.delete('/report/delete/<report_id>')
@jwt_required()
@admin_and_lead_role_required
def delete_report(report_id):
    try:
        deleted = Report_db.delete_report(report_id)
        if not deleted:
            return jsonify({"message" : "An error occured! Try again!", "status" : "error"}), 500
        
        return jsonify({"message" : "Report deleted successfully!", "status" : "success"}), 200
    
    except Exception as e:
        return jsonify({"message": f'Something went wrong: {e}', 'status': "error"}), 500
    
@report_bp.patch('/report/add_doc/<report_id>')
@jwt_required()
def add_doc(report_id):
    try:
        report = Report_db.get_by_report_id(report_id)
        if not report:
            return jsonify({"message": "Report not found", "status": "error"}), 404
        
        doc = request.files.get("doc")
        if not doc:
            return jsonify({"message": "No file uploaded", "status": "error"})
        
        filename = secure_filename(doc.filename)
        if not AllowedExtension.files(filename):
            return jsonify({"message" : 'Invalid file format! Try again', "status" : "error"}), 401
        
        try:
            uploaded = upload_file(doc, "SSRL_Lab_App/report_submissions/")
            if not uploaded:
                return jsonify({"message" : 'File upload error! Try again', "status" : "danger"}), 500
            
        except Exception as e:
             return jsonify({"message": f'File upload error: {e}', 'status': "error"}), 500

        doc_submission = {"filename": filename, "download_link": uploaded['secure_url'], "date_submitted": datetime.now()}
        submitted = Report_db.add_doc(report_id, doc_submission)
        
        if not submitted:
            return jsonify({"message" : 'An error occurred! Try again', "status" : "danger"}), 500
        
        return jsonify({"message": 'Document submitted successfully', "status" : "success"}), 200
        
    except Exception as e:
        return jsonify({"message": f'Something went wrong: {e}', 'status': "error"}), 500
    
@report_bp.patch('/report/add_link/<report_id>')
@jwt_required()
def add_link(report_id):
    try:
        report = Report_db.get_by_report_id(report_id)
        if not report:
            return jsonify({"message": "Report not found", "status": "error"}), 404
        
        link = request.json.get('link')
        link_submission = {"link": link, "submitted_at": datetime.now()}
        submitted = Report_db.add_link(report_id, link_submission)
        
        if not submitted:
            return jsonify({"message" : 'An error occurred! Try again', "status" : "danger"}), 500
        
        return jsonify({"message": 'Document submitted successfully', "status" : "success"}), 200
    
    except Exception as e:
        return jsonify({"message": f'Something went wrong: {e}', 'status': "error"}), 500
