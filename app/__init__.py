from flask import Flask
from flask_cors import CORS
from flask_socketio import SocketIO
from app.config import Config
from app.utils.database import Database

from app.controllers.auth_controller import auth_bp
from app.controllers.contact_controller import contact_bp
from app.controllers.message_controller import message_bp

from app.sockets import register_socket_events

socketio = SocketIO()

def create_app():
    app = Flask(__name__)

    app.url_map.strict_slashes = False

    CORS(app,
        resources={r"/api/*": {"origins": "*"}},
        allow_headers=["Content-Type", "Authorization"],
        methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        supports_credentials=True
    )

    socketio.init_app(app,
        cors_allowed_origins="*",
        async_mode='eventlet',
        logger=True,
        engineio_logger=True,
        ping_timeout=60,
        ping_interval=25
    )

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        return response

    app.register_blueprint(auth_bp)
    app.register_blueprint(contact_bp)
    app.register_blueprint(message_bp)

    register_socket_events(socketio)

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
