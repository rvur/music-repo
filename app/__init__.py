from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_socketio import SocketIO
import os
import secrets

db = SQLAlchemy()
socketio = SocketIO(cors_allowed_origins="*")

def create_app():
    app = Flask(__name__, static_folder='static', static_url_path='/static')
    
    CORS(app, 
         supports_credentials=True,  # CRITICAL for sessions
         origins="*")
    
    # Database config - use instance folder with proper permissions
    basedir = os.path.abspath(os.path.dirname(__file__))
    instance_path = os.path.join(basedir, "..", "instance")
    
    # Ensure instance directory exists
    os.makedirs(instance_path, exist_ok=True)
    
    db_path = os.path.join(instance_path, "app.db")
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    
    # Session configuration
    app.config['SECRET_KEY'] = secrets.token_hex(32)
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    app.config['SESSION_COOKIE_SECURE'] = False  # Set to True in production with HTTPS
    app.config['SESSION_PERMANENT'] = True
    
    # Upload folder config
    upload_folder = os.path.join(os.getcwd(), "music")
    cover_folder = os.path.join(os.getcwd(), "cover")
    os.makedirs(upload_folder, exist_ok=True)  # make sure it exists
    app.config["UPLOAD_FOLDER"] = upload_folder
    app.config["COVER_FOLDER"] = cover_folder
    app.config["ALLOWED_EXTENSIONS"] = {"mp3", "wav", "flac", "m4a", "webm", "mp4", "opus"}
    
    # Static folder config
    app.static_folder = 'static'
    app.static_url_path = '/static'
    
    db.init_app(app)
    socketio.init_app(app)
    
    # Import models so SQLAlchemy knows about them
    from app import models  

    # Register API blueprints
    from app.routes import register_blueprints
    register_blueprints(app)

    with app.app_context():
        db.create_all()

    return app