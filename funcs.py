import base64
from bson import ObjectId
from datetime import datetime
from db.models import Sessionsdb
from cloudinary.uploader import upload

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

def upload_file_func(file, folder, filename):
    return upload(file, folder=folder, upload_preset="intern_submissions", resource_type="raw", unique_filename=True,overwrite=True, public_id=filename, use_filename_as_display_name=True)
    
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
