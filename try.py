from main import app
from models.user import Userdb  
from models.models import Notificationsdb
from models.project import Projectdb
from datetime import datetime
from funcs import get_la_code

User_db = Userdb()
Notifications_db = Notificationsdb()
Project_db = Projectdb()

# def update_request_time():
#     Request_db.update_many_reqs()
    
# update_request_time()


def verify_smtp_connection():
    import smtplib
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
        server.quit()
        print("SMTP connection successful")
    except Exception as e:
        print(f"SMTP connection failed: {str(e)}")
        
def update_users():
    all_users = list(User_db.get_all_users())
    count = 0
    
    for user in all_users:
        if user['avatar'] == 'NIL':
            uid = user['uid']
        
            User_db.update_user(uid, {'avatar': None})
            count += 1
        
    return count

def update_notifications():
    all_notifications = list(Notifications_db.get_all())
    
    for notification in all_notifications:
        _id = notification['_id']
        sentAt = notification.get('sentAt')
        
        if sentAt:
            details = {'created_at': sentAt}
            updated = Notifications_db.update_notification_details(_id, details)
            unset = Notifications_db.unset_field(_id, 'sentAt')
        
def update_users():
    all_users = list(User_db.get_all_users())
    
    for user in all_users:
        uid = user['uid']
        created_at = user.get('created_at')
        
        if not created_at:
            details = {'created_at': datetime.now()}
            updated = User_db.update_dtl(uid, details)
            unset = User_db.unset_field(uid, 'datetime_created')
            
def update_projects():
    all_projects = list(Project_db.get_all_projects())

    for project in all_projects:
        _id = project['_id']
        pid = project.get('project_id')
        date_created = project.get('date_created')
        created_at = project.get('created_at')
        team_avatar = project.get('team_avatar')
        leads = project.get('leads')
        team_members = project.get('team_members')
        
update_projects()