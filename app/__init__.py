from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_migrate import Migrate
from flask_login import LoginManager
from dotenv import load_dotenv
import os
from google_auth_oauthlib.flow import Flow
from .extensions import db, mail, migrate, login
import pathlib
# Import routes và models
from app import  models
from app import admin
import cloudinary.uploader

load_dotenv()
app = Flask(__name__)
# Flask secret key
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"  #để đăng nhập đc trên localhost

# Database config
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Mail config
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT'))
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS') == 'True'
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')

#Cloudinary Config
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_NAME"),
    api_key=os.getenv("CLOUDINARY_KEY"),
    api_secret=os.getenv("CLOUDINARY_SECRET")
)



GOOGLE_CLIENT_SECRETS_FILE = os.path.join(pathlib.Path(__file__).parent, "oauth_config.json")

flow = Flow.from_client_secrets_file(
    GOOGLE_CLIENT_SECRETS_FILE,
    scopes=["https://www.googleapis.com/auth/userinfo.profile",
            "https://www.googleapis.com/auth/userinfo.email",
            "openid"],
    redirect_uri="http://localhost:5050/callback"

)

# RAG and CNN
app.config['QDRANT_API_KEY'] = os.getenv('QDRANT_API_KEY')
app.config['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY')
app.config['MODEL_LLM_NAME'] = os.getenv('MODEL_LLM_NAME')
app.config['MODEL_EMBEDDING_NAME'] = os.getenv('MODEL_EMBEDDING_NAME')
app.config['MODEL_CROSS_ENCODER_NAME'] = os.getenv('MODEL_CROSS_ENCODER_NAME')
app.config['COLLECTION_NAME'] = os.getenv('COLLECTION_NAME')
app.config['QDRANT_URL'] = os.getenv('QDRANT_URL')



# App settings
PAGE_SIZE = 8
# Khởi tạo các extension
db.init_app(app)
mail.init_app(app)
migrate.init_app(app, db)
login.init_app(app)


#import RAG CV cho rag
from app.rag_chatbot import rag_chatbot
from app.cv_model import cv_model