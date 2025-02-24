import base64
from bson import ObjectId
from datetime import datetime
from db.models import Sessionsdb
from cloudinary.uploader import upload
from flask_jwt_extended import get_jwt  
from functools  import wraps
import os
from uuid import uuid4

Sessions_db = Sessionsdb()

def convert_to_json_serializable(doc):
    if isinstance(doc, list):
        return [convert_to_json_serializable(d) for d in doc]
    if isinstance(doc, dict):
        for k, v in doc.items():
            if isinstance(v, ObjectId):
                doc[k] = str(v)
            elif isinstance(v, bytes):
                doc[k] = base64.b64encode(v).decode('utf-8')
            elif isinstance(v, (dict, list)):
                doc[k] = convert_to_json_serializable(v)
    return doc

def get_resource_type(filename):
    extension = filename.lower().split('.')[-1] if '.' in filename else ''
    
    if extension in ['png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp', 'svg', 'tiff']:
        return 'image'
    elif extension in ['mp4', 'mov', 'avi', 'wmv', 'flv', 'mkv', 'webm']:
        return 'video'
    elif extension in ['pdf', 'doc', 'docx', 'txt', 'csv', 'xls', 'xlsx']:
        return 'raw'
    else:
        return 'raw'

def upload_func(file, folder):
    _, file_extension = os.path.splitext(file.filename)
    type = get_resource_type(file.filename)
    public_id = f"{folder}/{uuid4()}"
    upload_options = {
            "public_id": public_id,  
            "unique_filename": False,  
            "resource_type": type,  
            "use_filename": False,    
            "overwrite": True      
        }
    
    if type == 'raw':
            _, file_extension = os.path.splitext(file.filename)
            upload_options["public_id"] = f"{public_id}{file_extension.lower()}"
            
    return upload(file, asset_folder=folder, upload_preset="upload_test", **upload_options)
    
def get_date_now():
    now = datetime.now().strftime
    month = now("%B")
    date = now("%d")
    year = now("%Y")
    return "{0} {1}, {2}".format(month, date, year)

def check_session(session_id):
    if session_id == "":
        return False

    session = Sessions_db.get_session(session_id)
    
    if not session:
        return False
    
    return session["user_data"]
 

def admin_role_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        user_role = get_jwt()['user_role']
        if user_role != 'Admin':
            return {'message': 'Unauthorized access to admin dashboard, try changing you role', 'status': 'error'}, 401
        return f(*args, **kwargs)
    return decorated

def admin_and_lead_role_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        user_role = get_jwt()['user_role']
        roles = ['Admin', 'Lead']
        
        if user_role not in roles:
            return {'message': 'Unauthorized access, please contact the admin or lead', 'status': 'error'}, 401
        return f(*args, **kwargs)
    return decorated

allowed_ext =  ['jpg', 'jpeg', 'png', 'gif']
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_ext

def check_file_size(file, max_size_mb = 1):
    file.seek(0, os.SEEK_END)
    size_bytes = file.tell()
    file.seek(0)  
    
    size_mb = size_bytes / (1024 * 1024)  
    
    return size_mb < max_size_mb
        