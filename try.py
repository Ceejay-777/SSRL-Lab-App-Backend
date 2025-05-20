from main import app
from models.models import Requestdb
from models.user import Userdb  

Request_db = Requestdb()
User_db = Userdb()

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
        
# print(update_users())
