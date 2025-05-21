from main import app
from models.user import Userdb  
from models.models import Notificationsdb

User_db = Userdb()
Notifications_db = Notificationsdb()

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
        
# print(update_users())
# update_notifications()
