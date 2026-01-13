from flask import Flask
from flask_cors import CORS
from app.config import Config
from app.utils.database import Database

from app.controllers.auth_controller import auth_bp
from app.controllers.contact_controller import contact_bp
from app.controllers.message_controller import message_bp

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
    app.register_blueprint(contact_bp)
    app.register_blueprint(message_bp)

    @app.route('/health', methods=['GET'])
    def health_check():
        try:
            Database.execute_query("SELECT 1", fetch=True)
            return {
                'status': 'OK',
                'database': 'connected',
                'message': 'API is running correctly'
            }, 200
        except:
            return {
                'status': 'ERROR',
                'database': 'disconnected',
                'message': 'API is not running perfectly'
            }, 503
    
    @app.route('/', methods=['GET'])
    def index():
        return {
            'name': 'MyChat API',
            'version': '1.0.0',
            'status': 'running',
            'endpoints': {
                'auth': '/api/auth',
                'contacts': '/api/contacts',
                'messages': '/api/messages'
            }
        }, 200
    
    return app