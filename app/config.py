# app/config.py - VERSÃO COM WORKAROUND BASE64

import os
import base64
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Classe de configuração da aplicação"""
    
    # Database
    DB_CONNECTION_URL = os.getenv('CONN_URL')
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
    VAPID_CLAIM_EMAIL = os.getenv('VAPID_CLAIM_EMAIL')
    
    # ===================================================================
    # WORKAROUND: Suportar VAPID_PRIVATE_KEY em Base64 ou texto normal
    # ===================================================================
    VAPID_PRIVATE_KEY = os.getenv('VAPID_PRIVATE_KEY')
    VAPID_PRIVATE_KEY_BASE64 = os.getenv('VAPID_PRIVATE_KEY_BASE64')
    
    if VAPID_PRIVATE_KEY_BASE64:
        # Se usar Base64, decodificar
        try:
            VAPID_PRIVATE_KEY = base64.b64decode(VAPID_PRIVATE_KEY_BASE64).decode('utf-8')
            print("✅ VAPID_PRIVATE_KEY carregada via Base64")
        except Exception as e:
            print(f"❌ Erro ao decodificar VAPID_PRIVATE_KEY_BASE64: {e}")
            VAPID_PRIVATE_KEY = None
    elif VAPID_PRIVATE_KEY:
        # Processar chave normal
        VAPID_PRIVATE_KEY = (
            VAPID_PRIVATE_KEY
            .strip()
            .strip('"')
            .strip("'")
            .replace("\\n", "\n")
        )
    
    # Debug (ajuda a diagnosticar)
    if VAPID_PRIVATE_KEY:
        print(f"🔑 VAPID_PRIVATE_KEY (primeiros 50 chars): {VAPID_PRIVATE_KEY[:50]}")
        print(f"🔑 VAPID_PRIVATE_KEY (últimos 50 chars): {VAPID_PRIVATE_KEY[-50:]}")
        print(f"🔑 VAPID_PRIVATE_KEY (tamanho total): {len(VAPID_PRIVATE_KEY)} chars")
    else:
        print("⚠️ VAPID_PRIVATE_KEY não definida!")
    
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
