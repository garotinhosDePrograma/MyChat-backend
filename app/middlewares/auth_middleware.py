from functools import wraps
from flask import request, g
from app.services.auth_service import AuthService
from app.utils.response import Response

def require_auth(f):
    wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')

        if not auth_header:
            return Response.unauthorized("Token não fornecido.")
        
        parts = auth_header.split()

        if len(parts) != 2 or parts[0].lower() != 'bearer':
            return Response.unauthorized("Formato de token inválido.")
        
        token = parts[1]

        user = AuthService.verify_token(token)

        if not user:
            return Response.unauthorized("Token inválido ou expirado.")

        g.current_user = user

        return f(*args, **kwargs)
    
    return decorated_function