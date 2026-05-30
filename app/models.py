from flask_sqlalchemy import SQLAlchemy
from app import db

playlist_songs = db.Table('playlist_songs',
    db.Column('playlist_id', db.Integer, db.ForeignKey('playlist.id'), primary_key=True),
    db.Column('song_id', db.Integer, db.ForeignKey('music.id'), primary_key=True),
    db.Column('position', db.Integer, nullable=False, default=0)  # Track order in playlist
)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), unique=False, nullable=False)
    
    def to_dict(self):
        user_dict = {
            'username': self.username
        }
        return user_dict
    
class Playlist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    songs = db.relationship('Music', secondary=playlist_songs, backref='playlists')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'song_count': len(self.songs),
            'songs': [song.to_dict() for song in self.songs]
        }
    
class Music(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    song_name = db.Column(db.String(200), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    song_length = db.Column(db.Integer, nullable=False)
    song_size = db.Column(db.Float, nullable=False)
    cover_image = db.Column(db.String(500), nullable=False, default="/app/covers/default.png")
    votes = db.Column(db.Integer, nullable=False, default=0)

    def to_dict(self):
        song_dict = {
            'id': self.id,
            'song_name': self.song_name,
            'file_path': self.file_path,
            'length': self.song_length,
            'cover': self.cover_image,
            'size': self.song_size,
            'votes': self.votes
        }
        return song_dict

class Comments(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(50), nullable=False)
    content = db.Column(db.String(500), nullable=False)

    def to_dict(self):
        comment_dict = {
            'id': self.id,
            'name': self.name,
            'content': self.content
        }
        return comment_dict

