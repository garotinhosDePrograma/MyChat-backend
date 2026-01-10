from flask import Flask
from flask_cors import CORS
from app.config import Config
from app.controllers.auth_controller import auth_bp

def create_app():
    app = Flask(__name__)

    CORS(app, resources={
        r"/api/*": {
            "origins": [Config.FRONTEND_URL, "http://localhost:8080"],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })

    app.register_blueprint(auth_bp)

    @app.route('/health', methods=['GET'])
    def health_check():
        return {
            'status': 'OK',
            'message': 'MyChat API is running'
        }, 200
    
    @app.route('/', methods=['GET'])
    def index():
        return {
            'name': 'MyChat API',
            'version': '1.0.0',
            'status': 'running'
        }, 200
    
    return app