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

app = Flask(__name__)
bcrypt = Bcrypt(app)
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

cloudinary.config(
        cloud_name=app.config['CLOUDINARY_CLOUD_NAME'],
        api_key=app.config['CLOUDINARY_API_KEY'],
        api_secret=app.config['CLOUDINARY_API_SECRET']
    )

mail = Mail(app)
JWTManager(app)

if __name__=="__main__":
    app.run(debug=True)