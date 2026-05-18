from flask import Blueprint, request, jsonify, session, send_from_directory, abort, current_app
from flask_socketio import emit
from app import db, socketio
from app.models import Music
from .rules import login_required, login_not_required
from .helper import *
from werkzeug.utils import secure_filename
import os
import mutagen

music_bp = Blueprint("music", __name__)

@music_bp.route("/", methods=['GET'])
def get_music():
    print(session.get("logged_in"))
    all_songs = Music.query.all()
    return jsonify([song.to_dict() for song in all_songs])

@music_bp.route("/", methods=['POST'])
@login_required
def upload_music():
    
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        save_path = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)

        file.save(save_path)

        try:
            audio = mutagen.File(save_path)
            song_length = int(audio.info.length)
        except Exception:
            song_length = 0

        MB_SIZE = 1048576
        total_bytes = os.path.getsize(save_path)
        total_mb = total_bytes / MB_SIZE

        new_song = Music(song_name=filename,
                         file_path=save_path,
                         song_length=song_length,
                         song_size=total_mb)
        db.session.add(new_song)
        db.session.commit()
        
        socketio.emit("new_song", new_song.to_dict())
        return jsonify(new_song.to_dict()), 201
    return jsonify({"error": "File type not allowed"}), 400

@music_bp.route("/yt", methods=["POST"])
@login_required
def yt_upload():
    data = request.get_json()

    if not data.get("yt_link"):
        return jsonify({"error": "No link provided"}), 400
    
    try:
        yt_link = data.get("yt_link")
        file_path, info, thumbnail = download_audio(yt_link, output_dir=current_app.config["UPLOAD_FOLDER"])
        
        # Calculate file size
        MB_SIZE = 1048576
        file_size_mb = os.path.getsize(file_path) / MB_SIZE
        
        # Get song length
        try:
            audio = mutagen.File(file_path)
            song_length = int(audio.info.length)
        except Exception as e:
            print(f"Mutagen error: {e}")
            song_length = 0
        
        # Create new song entry
        new_song = Music(
            song_name=info.get('title', 'Unknown'),  # Safer access
            file_path=file_path,
            song_length=song_length,
            cover_image=thumbnail,
            song_size=file_size_mb
        )
        
        db.session.add(new_song)
        db.session.commit()
        socketio.emit("new_song", new_song.to_dict())
        return jsonify(new_song.to_dict()), 201
        
    except Exception as e:
        print(f"YouTube download error: {e}")  # Log the actual error
        import traceback
        traceback.print_exc()  # Print full stack trace
        return jsonify({"error": f"Error downloading youtube audio: {str(e)}"}), 400


@music_bp.route("/stream/<int:song_id>", methods=["GET"])
@login_required
def stream_music(song_id):

    song = Music.query.get(song_id)
    if not song:
        return abort(404, description="Song not found")

    # Ensure file exists on disk
    if not os.path.exists(song.file_path):
        return abort(404, description="File not found on server")

    # Use send_from_directory to serve file
    directory, filename = os.path.split(song.file_path)
    socketio.emit("current_listening", song.to_dict())
    return send_from_directory(directory, filename, as_attachment=False)

@music_bp.route("/delete/<int:song_id>", methods=["DELETE"])
@login_required
def delete_music(song_id):
    song = Music.query.filter_by(id=song_id).first()
    if not song:
        return jsonify({"error": "Song does not exist"}), 404
    
    if not os.path.exists(song.file_path):
        return jsonify({"error": "Song not found on server"}), 404
    
    os.remove(song.file_path)
    db.session.delete(song)
    db.session.commit()
    
    socketio.emit("song_removed", song.to_dict())
    return jsonify({"message": "Song deleted"}), 200

@music_bp.route("/size", methods=["GET"])
@login_required
def total_size():
    
    all_songs = Music.query.all()
    total_mb = 0
    for song in all_songs:
        total_mb += song.song_size
    return jsonify({"message": {"size": total_mb}})

