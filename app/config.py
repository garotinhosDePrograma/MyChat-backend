import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Classe de configuração da aplicação"""
    
    # Database - suporta CONN_URL (Railway) ou variáveis individuais
    DB_CONNECTION_URL = os.getenv('CONN_URL')  # URL completa do Railway
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = int(os.getenv('DB_PORT', 3306))
    DB_USER = os.getenv('DB_USER', 'root')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    DB_NAME = os.getenv('DB_NAME', 'mychat_db')
    
    # JWT
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'dev_secret_key')
    JWT_ALGORITHM = os.getenv('JWT_ALGORITHM', 'HS256')
    JWT_EXPIRATION_HOURS = int(os.getenv('JWT_EXPIRATION_HOURS', 24))
    
    # Flask
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    DEBUG = os.getenv('FLASK_DEBUG', 'False') == 'True'
    PORT = int(os.getenv('PORT', 5000))

    # Push Notifications
    VAPID_PUBLIC_KEY = os.getenv('VAPID_PUBLIC_KEY')
    VAPID_PRIVATE_KEY = os.getenv('VAPID_PRIVATE_KEY')
    VAPID_CLAIM_EMAIL = os.getenv('VAPID_CLAIM_EMAIL')
    
    # CORS
    FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:3000')
    
    @staticmethod
    def get_db_config():
        """Retorna configuração do banco de dados"""
        return {
            'host': Config.DB_HOST,
            'port': Config.DB_PORT,
            'user': Config.DB_USER,
            'password': Config.DB_PASSWORD,
            'database': Config.DB_NAME
        }
