from flask_mail import Mail
import cloudinary
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
import os
from  pymongo import MongoClient

load_dotenv()

uri = os.getenv('MONGO_URI')

mongo_client = MongoClient(uri)
mail = Mail()
jwt = JWTManager()

def init_cloudinary(app):
    cloudinary.config(
        cloud_name=app.config['CLOUDINARY_CLOUD_NAME'],
        api_key=app.config['CLOUDINARY_API_KEY'],
        api_secret=app.config['CLOUDINARY_API_SECRET']
    )
    