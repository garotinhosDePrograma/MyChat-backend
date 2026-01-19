# app/controllers/push_controller.py

from flask import Blueprint, request, g
from app.services.push_service import PushService
from app.utils.response import Response
from app.middlewares.auth_middleware import require_auth

push_bp = Blueprint('push', __name__, url_prefix='/api/push')

@push_bp.route('/vapid-public-key', methods=['GET'])
@require_auth
def get_vapid_public_key():
    """
    Retorna a chave pública VAPID para o cliente
    """
    try:
        public_key = PushService.get_vapid_public_key()
        return Response.success({
            'publicKey': public_key
        })
    except Exception as e:
        return Response.error(f"Erro ao obter chave VAPID: {str(e)}", 500)

@push_bp.route('/subscribe', methods=['POST'])
@require_auth
def subscribe():
    """
    Salva a subscription do usuário
    
    Body:
        {
            "subscription": {
                "endpoint": "https://...",
                "keys": {
                    "p256dh": "...",
                    "auth": "..."
                }
            }
        }
    """
    try:
        user = g.current_user
        data = request.get_json()
        
        if not data or 'subscription' not in data:
            return Response.error("Dados inválidos")
        
        subscription = data['subscription']
        
        success = PushService.save_subscription(user.id, subscription)
        
        if success:
            return Response.success(message="Subscription salva com sucesso")
        else:
            return Response.error("Erro ao salvar subscription")
            
    except Exception as e:
        return Response.error(f"Erro no servidor: {str(e)}", 500)

@push_bp.route('/unsubscribe', methods=['POST'])
@require_auth
def unsubscribe():
    """
    Remove a subscription do usuário
    
    Body:
        {
            "endpoint": "https://..."
        }
    """
    try:
        user = g.current_user
        data = request.get_json()
        
        if not data or 'endpoint' not in data:
            return Response.error("Endpoint é obrigatório")
        
        endpoint = data['endpoint']
        
        success = PushService.remove_subscription(user.id, endpoint)
        
        if success:
            return Response.success(message="Subscription removida com sucesso")
        else:
            return Response.error("Erro ao remover subscription")
            
    except Exception as e:
        return Response.error(f"Erro no servidor: {str(e)}", 500)

@push_bp.route('/test', methods=['POST'])
@require_auth
def send_test_notification():
    """
    Envia uma notificação de teste para o usuário
    """
    try:
        user = g.current_user
        
        success = PushService.send_notification(
            user.id,
            title="🔔 Notificação de Teste",
            body="As notificações estão funcionando!",
            data={'type': 'test'}
        )
        
        if success:
            return Response.success(message="Notificação enviada")
        else:
            return Response.error("Erro ao enviar notificação")
            
    except Exception as e:
        return Response.error(f"Erro no servidor: {str(e)}", 500)
