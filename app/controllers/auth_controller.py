from flask import Blueprint, request, g
from app.services.auth_service import AuthService
from app.utils.response import Response
from app.middlewares.auth_middleware import require_auth

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        
        if not data:
            return Response.error("Dados inválidos")
        
        name = data.get('name', '').strip()
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        user, result = AuthService.register(name, email, password)
        
        if not user:
            return Response.error(result)
        
        return Response.created({
            'user': user.to_dict(),
            'token': result
        }, "Usuário registrado com sucesso")
        
    except Exception as e:
        return Response.error(f"Erro no servidor: {str(e)}", 500)

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        
        if not data:
            return Response.error("Dados inválidos")
        
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        user, result = AuthService.login(email, password)
        
        if not user:
            return Response.error(result)
        
        return Response.success({
            'user': user.to_dict(),
            'token': result
        }, "Login realizado com sucesso")
        
    except Exception as e:
        return Response.error(f"Erro no servidor: {str(e)}", 500)

@auth_bp.route('/me', methods=['GET'])
@require_auth
def get_current_user():
    try:
        user = g.current_user
        return Response.success({'user': user.to_dict()})
    except Exception as e:
        return Response.error(f"Erro no servidor: {str(e)}", 500)

@auth_bp.route('/verify', methods=['GET'])
@require_auth
def verify_token():
    return Response.success(message="Token válido")