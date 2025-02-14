from main import app
from db.models import Requestdb

Request_db = Requestdb()

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
    
# verify_smtp_connection()

