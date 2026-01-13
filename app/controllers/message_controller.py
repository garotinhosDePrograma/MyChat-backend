from flask import Blueprint, request, g
from app.services.message_service import MessageService
from app.utils.response import Response
from app.middlewares.auth_middleware import require_auth

message_bp = Blueprint('message', __name__, url_prefix='/api/messages')

@message_bp.route('/send', methods=["POST"])
@require_auth
def send_message():
    try:
        user = g.current_user
        data = request.get_json()

        if not data:
            return Response.error("Dados inválidos")
        
        receiver_id = data.get('receiver_id')
        content = data.get('content')

        if not receiver_id:
            return Response.error("ID do destinatário é obrigatório")
        
        if not content:
            return Response.error("Conteúdo da mensagem é obrigatório")
        
        message, error = MessageService.send_message(
            user.id,
            receiver_id,
            content
        )

        if not message:
            return Response.error(error)
        
        return Response.created({
            'message': message.to_dict()
        }, "Mensagem enviada com sucesso")
    
    except Exception as e:
        return Response.error(f"Erro no servidor: {str(e)}", 500)

@message_bp.route('/conversation/<int:contact_user_id>', methods=["GET"])
@require_auth
def get_conversation(contact_user_id):
    try:
        user = g.current_user
        limit = request.args.get('limit', 50, type=int)
        
        if limit > 200:
            limit = 200
        
        messages = MessageService.get_conversation(user.id, contact_user_id, limit)
        
        return Response.success({
            'messages': messages
        })
        
    except Exception as e:
        return Response.error(f"Erro no servidor: {str(e)}", 500)

@message_bp.route('/mark-read/<int:sender_id>', methods=["PUT"])
@require_auth
def mark_as_read(sender_id):
    try:
        user = g.current_user
        count = MessageService.mark_conversation_as_read(user.id, sender_id)
        
        return Response.success({
            'count': count
        }, "Mensagens marcadas como lidas")
        
    except Exception as e:
        return Response.error(f"Erro no servidor: {str(e)}", 500)

@message_bp.route('/unread', methods=["GET"])
@require_auth
def get_unread():
    try:
        user = g.current_user
        total = MessageService.get_unread_count(user.id)
        by_contact = MessageService.get_unread_by_contact(user.id)
        
        return Response.success({
            'total': total,
            'by_contact': by_contact
        })
        
    except Exception as e:
        return Response.error(f"Erro no servidor: {str(e)}", 500)

@message_bp.route('/<int:message_id>', methods=["DELETE"])
@require_auth
def delete_message(message_id):
    try:
        user = g.current_user
        
        success, error = MessageService.delete_message(message_id, user.id)
        
        if not success:
            return Response.error(error)
        
        return Response.success(message="Mensagem deletada com sucesso")
        
    except Exception as e:
        return Response.error(f"Erro no servidor: {str(e)}", 500)

@message_bp.route('/conversation/<int:contact_user_id', methods=["DELETE"])
@require_auth
def delete_conversation(contact_user_id):
    try:
        user = g.current_user
        
        count, error = MessageService.delete_conversation(user.id, contact_user_id)
        
        if error:
            return Response.error(error)
        
        return Response.success({
            'deleted_count': count
        }, f"{count} mensagens deletadas com sucesso")
        
    except Exception as e:
        return Response.error(f"Erro no servidor: {str(e)}", 500)