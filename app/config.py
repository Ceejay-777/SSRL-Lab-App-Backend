import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # SECRET_KEY = os.getenv('SECRET_KEY', 'your_secret_key')
    
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')  
    JWT_ACCESS_TOKEN_EXPIRES = 3600
    
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')  
    
    CLOUDINARY_CLOUD_NAME = os.getenv('CLOUDINARY_CLOUD_NAME')
    CLOUDINARY_API_KEY = os.getenv('CLOUDINARY_API_KEY')
    CLOUDINARY_API_SECRET = os.getenv('CLOUDINARY_API_SECRET')
    
    MAIL_DEFAULT_SENDER = ("Smart Systems Research Lab", os.getenv('MAIL_DEFAULT_SENDER'))