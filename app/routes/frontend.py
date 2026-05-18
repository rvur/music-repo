from flask import Blueprint, send_from_directory, current_app


main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def serve_frontend():
    return send_from_directory(current_app.static_folder, 'index.html')

# You can add other general routes here if needed
@main_bp.route('/health')
def health_check():
    return {'status': 'healthy'}