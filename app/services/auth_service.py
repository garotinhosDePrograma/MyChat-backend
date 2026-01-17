import bcrypt
import jwt
from datetime import datetime, timedelta
from app.config import Config
from app.models.user import User
from app.repositories.user_repository import UserRepository

class AuthService:
    @staticmethod
    def hash_password(password):
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    @staticmethod
    def verify_password(password, hashed_password):
        return bcrypt.checkpw(
            password.encode('utf-8'),
            hashed_password.encode('utf-8')
        )
    
    @staticmethod
    def generate_token(user_id):
        payload = {
            'user_id': user_id,
            'exp': datetime.utcnow() + timedelta(days=Config.JWT_EXPIRATION_HOURS),
            'iat': datetime.utcnow()
        }

        token = jwt.encode(
            payload,
            Config.JWT_SECRET_KEY,
            algorithm=Config.JWT_ALGORITHM
        )

        return token
    
    @staticmethod
    def verify_token(token):
        try:
            payload = jwt.decode(
                token,
                Config.JWT_SECRET_KEY,
                algorithms=[Config.JWT_ALGORITHM]
            )
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    @staticmethod
    def register(name, email, password):
        if not all([name, email, password]):
            return None, "Todos os campos são obrigatórios"
        
        if len(password) < 6:
            return None, "A senha deve conter pelo menos 6 caracteres"
        
        if UserRepository.email_exists(email):
            return None, "Email já cadastrado"
        
        password_hash = AuthService.hash_password(password)
        user = User(name=name, email=email, password_hash=password_hash)

        try:
            user = UserRepository.create(user)
            token = AuthService.generate_token(user.id)
            return user, token
        except Exception as e:
            return None, f"Erro ao criar usuário: {str(e)}"
    
    @staticmethod
    def login(email, password):
        if not all([email, password]):
            return None, "Todos os campos são obrigatórios"
        
        user = UserRepository.find_by_email(email)

        if not user:
            return None, "Email inválido"
        
        if not AuthService.verify_password(password, user.password_hash):
            return None, "Senha inválida"
        
        token = AuthService.generate_token(user.id)

        return user, token
    
    @staticmethod
    def get_user_from_token(token):
        payload = AuthService.verify_token(token)
        
        if not payload:
            return None
        
        user_id = payload.get('user_id')
        return UserRepository.find_by_id(user_id)
