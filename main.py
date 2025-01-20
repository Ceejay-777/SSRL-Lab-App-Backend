from flask import Flask
from flask_bcrypt import Bcrypt
from flask_mail import Mail
from flask_cors import CORS
from db.models import *
from properties import *
import cloudinary
from flask_jwt_extended import JWTManager
# from dotenv import load_dotenv

# load_dotenv()

def create_app():

    app = Flask(__name__)
    Bcrypt(app)
    CORS(app, supports_credentials=True, resources={r"*": {"origins": "*"}}, withCredentials = True)


    UPLOAD_FOLDER = 'static/images'
    PROJECT_FOLDER = 'submissions/projects'

    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.config['PROJECT_FOLDER'] = PROJECT_FOLDER
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 465
    app.config['MAIL_USERNAME'] = 'covenantcrackslord03@gmail.com'
    app.config['MAIL_PASSWORD'] = email_pswd
    app.config['MAIL_USE_TLS'] = False
    app.config['MAIL_USE_SSL'] = True
    app.config['CLOUDINARY_CLOUD_NAME'] = "dy39txnxp"
    app.config['CLOUDINARY_API_KEY'] = "614134161466845"
    app.config['CLOUDINARY_API_SECRET'] = "yxilIicreF-wO9SSXUdEWKuNj4k"
    app.config['JWT_SECRET_KEY'] = '33fa732c553cf6eebac80fab24b77ef8d49faf8d153b5695b0e61554183fc6c1'
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 3600
    

    cloudinary.config(
            cloud_name=app.config['CLOUDINARY_CLOUD_NAME'],
            api_key=app.config['CLOUDINARY_API_KEY'],
            api_secret=app.config['CLOUDINARY_API_SECRET']
        )

    Mail(app)
    JWTManager(app)
    
    return app

