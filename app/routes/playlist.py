from flask import Blueprint, request, jsonify, session, send_from_directory, abort, current_app
from app.models import Playlist, playlist_songs, Music
from .rules import *
from app import db

playlist_bp = Blueprint("playlist", __name__)

@playlist_bp.route("/", methods=["GET"])
@login_required
def get_playlists():
    playlists = Playlist.query.all()
    return jsonify([playlist.to_dict() for playlist in playlists])

@playlist_bp.route("/<int:playlist_id>", methods=["GET"])
@login_required
def get_playlist_songs(playlist_id):
    playlist = Playlist.query.get_or_404(playlist_id)

    return jsonify(playlist.to_dict())

@playlist_bp.route("/create", methods=["POST"])
@login_required
def make_playlist():
    data = request.get_json()
    if not data or not data["name"]:
        return jsonify({"error": "No data in response"}), 400
    playlist_name = data["name"]
    try:
        new_playlist = Playlist(name=playlist_name)
        db.session.add(new_playlist)
        db.session.commit()
        return jsonify({"message": "Playlist created!"}), 200
    except Exception as e:
        return jsonify({"error": "Error creating table"}), 400

@playlist_bp.route("/<int:playlist_id>/songs", methods=["POST"])
@login_required
def add_song_to_playlist(playlist_id):
    data = request.get_json()
    playlist = Playlist.query.get_or_404(playlist_id)

    song_id = data.get("song_id")
    if not song_id:
        return jsonify({'error': 'song_id is required'}), 400
    
    song = Music.query.get_or_404(song_id)

    if song in playlist.songs:
        return jsonify({'error': 'Song already in playlist'}), 400
    
    max_position = db.session.query(db.func.max(playlist_songs.c.position)).filter(playlist_songs.c.playlist_id == playlist_id).scalar()
    next_position = (max_position or -1) + 1

    stmt = playlist_songs.insert().values(
        playlist_id=playlist_id,
        song_id=song_id,
        position=next_position
    )
    db.session.execute(stmt)
    db.session.commit()

    return jsonify(playlist.to_dict()), 200
