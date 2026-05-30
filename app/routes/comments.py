from flask import Blueprint, request, jsonify, session, send_from_directory, abort, current_app
from flask_socketio import emit
from app import db, socketio
from app.models import Comments
from .rules import login_required, login_not_required


comment_bp = Blueprint("comments", __name__)


@comment_bp.route("/", methods=["GET"])
def all_comments() -> dict:
    """Returns all comments"""
    all_comments = Comments.query.all()
    comment_list = [comment.to_dict() for comment in all_comments]

    return jsonify({"comments": comment_list}), 200

@comment_bp.route("/", methods=["POST"])
def create_comment() -> dict:
    """Creates a new comment"""

    data = request.get_json()
    if not data.get("name") or not data.get("content"):
        return jsonify({"error": "Missing name or comment content"}), 400
    
    comment = Comments(name=data['name'], content=data['content'])
    db.session.add(comment)
    db.session.commit()

    return jsonify({"message": "Comment created!"}), 201

@comment_bp.route("/<int:comment_id>", methods=["DELETE"])
@login_required
def delete_comment(comment_id:int) -> dict:
    """Deletes a comment based on comment_id provided in the endpoint"""
    comment = Comments.query.filter_by(id=comment_id).first()

    db.session.delete(comment)
    db.session.commit()

    return jsonify({"message": "Comment deleted!"}), 204

