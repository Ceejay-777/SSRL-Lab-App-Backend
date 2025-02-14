from flask import Flask
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from app.routes.auth import auth_bp
from app.routes.personnel import personnel_bp
from app.routes.project import project_bp
from app.routes.report import report_bp
from app.routes.request import request_bp

from app.extensions import mail, jwt, init_cloudinary

def create_app():
    app = Flask(__name__)
    app.config.from_object('app.config.Config')
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(personnel_bp)
    app.register_blueprint(project_bp)
    app.register_blueprint(report_bp)
    app.register_blueprint(request_bp)

    Bcrypt(app)

    mail.init_app(app)
    jwt.init_app(app)
    init_cloudinary(app)
    
    CORS(app, supports_credentials=True, resources={r"*": {"origins": "*", "allow_headers": "*"}})
    
    return app

