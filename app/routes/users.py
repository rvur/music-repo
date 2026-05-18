from flask import Blueprint, request, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from app.models import User
from .rules import login_not_required, login_required


users_bp = Blueprint("users", __name__)



@users_bp.route("/", methods=["GET"])
@login_required
def get_users():
    if not session.get("logged_in"):
        return jsonify({'error': "Not logged in"}), 401
    
    # Since you only allow one user, return that user
    user = User.query.first()
    if not user:
        return jsonify({'error': "No user found"}), 404
    
    return jsonify(user.to_dict())

@users_bp.route("/register", methods=["POST"])
@login_not_required
def register():
    if User.query.first():
        return jsonify({"error": "Account already created"}), 400
    
    data = request.get_json()
    if not data.get("username") or not data.get("password"):
        return jsonify({"error": "Missing username or password"}), 400
    
    if len(data.get("password")) < 8:
        return jsonify({"error": "Password must be at least 8 characters"}), 400
    
    if not data.get("re_password") or data.get("password") != data.get("re_password"):
        return jsonify({'error': "Please retype your password"}), 400
    
    hashed_pw = generate_password_hash(data["password"])
    user = User(username=data['username'],password=hashed_pw)
    db.session.add(user)
    db.session.commit()

    return jsonify({'message': "Account created successfully"}), 201

@users_bp.route("/login", methods=["POST"])
@login_not_required
def login():
    if session.get("logged_in"):
        return jsonify({"error": "You are already logged in"}), 401
    data = request.get_json()

    if not data.get("username") or not data.get("password"):
        return jsonify({"error": "Username or password is missing"})
    
    user = User.query.filter_by(username = data.get("username")).first()

    if not user or not check_password_hash(user.password, data.get("password")):
        return jsonify({"error": "Invalid credentials"}), 401
    
    session["logged_in"] = True
    session.permanent = True
    return jsonify({
        "message": "Login successful",
        "username": user.username,
        "id": user.id
    }), 200

@users_bp.route("/logout", methods=["POST"])
@login_required
def logout():
    session.clear()
    return jsonify({"message": "Logged out"}), 200



