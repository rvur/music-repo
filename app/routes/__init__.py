from flask import Blueprint
from .users import users_bp
from .music import music_bp
from .frontend import main_bp
from .playlist import playlist_bp

def register_blueprints(app):
    app.register_blueprint(users_bp, url_prefix="/api/users")
    app.register_blueprint(music_bp, url_prefix="/api/music")
    app.register_blueprint(playlist_bp, url_prefix="/api/playlist")
    app.register_blueprint(main_bp)