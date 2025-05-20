from flask import Blueprint, request, jsonify
from models.models import generate, updatePwd, Reportdb, Todosdb, Notificationsdb, Notification, AllowedExtension, Todo
from flask_bcrypt import Bcrypt, check_password_hash, generate_password_hash
from funcs import convert_to_json_serializable
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_jwt
from flask_mail import Message
from app.extensions import mail
from datetime import datetime, timedelta
from funcs import *
import json
from werkzeug.utils import secure_filename
from models.user import Userdb
from models.project import Project, Projectdb
from models.request import Request, Requestdb

todo_bp = Blueprint('todo', __name__)

User_db = Userdb()
Request_db = Requestdb()
Report_db = Reportdb()
Project_db = Projectdb()
Todos_db = Todosdb()
Notifications = Notificationsdb()

@todo_bp.post('/todo/create') 
@jwt_required()
def create_todo():
    try:
        uid = get_jwt_identity()
        # uid = "CovenantSSRL812"
        todo = request.json.get("todo")
        
        existing_todo = Todos_db.get_todo_by_user_id(uid)
        
        if not existing_todo:
            new_todo = Todo(uid)
            created_new_todo = Todos_db.create_todo(new_todo)
            
            if not created_new_todo:
                return jsonify({"message" : 'Could not create new todo! Try again 1', "status" : "error"}), 500
            
        added_todo = Todos_db.add_todo(uid, todo)
        if not added_todo[0]:
            return jsonify({"message" : 'Could not create new todo! Try again 2', "status" : "error"}), 500
            
        return jsonify({"message" : 'Todo created successfully', "status" : "success", "id": added_todo[1]}), 200
    
    except Exception as e:
        return jsonify({"message": f'Something went wrong: {e}', 'status': "error"}), 500
        
@todo_bp.delete('/todo/delete/<todo_id>')
@jwt_required()
def delete_todo(todo_id):    
    try:
        uid = get_jwt_identity()
        deleted = Todos_db.delete_todo(uid, todo_id)
        
        if not deleted:
            return jsonify({"message" : 'An error occurred! Try again', "status" : "error"}), 500
        
        return jsonify({"message" : 'Todo deleted successfully', "status" : "success"}), 200
        
    except Exception as e:
        return jsonify({"message": f'Something went wrong: {e}', 'status': "error"}), 500

@todo_bp.patch('/todo/change_status/<todo_id>')
@jwt_required()
def change_status(todo_id):    
    try:
        uid = get_jwt_identity()
        status = request.json.get("status")
        change_status = Todos_db.change_status(uid, todo_id, status)
        
        if not change_status:
            return jsonify({"message" : 'An error occurred! Try again', "status" : "error"})
        
        return jsonify({"message" : 'Todo updated successfully', "status" : "success"}), 200
        
    except Exception as e:
        return jsonify({"message": f'Something went wrong: {e}', 'status': "error"}), 500

@todo_bp.get('/todo/get_all')
@jwt_required()
def all_todos():
    try:
        uid = get_jwt_identity()
        all_todos = convert_to_json_serializable(list(Todos_db.get_todo_by_user_id(uid).get("todo", {})))
        
        return jsonify({"todos": all_todos, 'status': 'success'}), 200
        
    except Exception as e:
        return jsonify({"message": f'Something went wrong: {e}', 'status': "error"}), 500
    
@todo_bp.patch('/todo/edit/<todo_id>')
@jwt_required()
def edit_todo(todo_id):
    try:
        uid = get_jwt_identity()
        todo = request.json.get("todo")
        
        edited = Todos_db.edit_todo(uid, todo_id, todo)
        if not edited:
            return jsonify({"message": "No changes made", "status": "error"}), 404
        
        return jsonify({"message": "Todo edited successfully", "status": "success"})

    except Exception as e:
        return jsonify({"message": f'Something went wrong: {e}', 'status': "error"}), 500