from flask import Blueprint, request, g
from app.services.contact_service import ContactService
from app.utils.response import Response
from app.middlewares.auth_middleware import require_auth

contact_bp = Blueprint('contact', __name__, url_prefix='/api/contacts')

@contact_bp.route('', methods=["GET"])
@contact_bp.route('/', methods=["GET"])
@require_auth
def get_contacts():
    try:
        user = g.current_user
        contacts = ContactService.get_user_contacts(user.id)

        return Response.success({
            'contacts': contacts
        })
    except Exception as e:
        return Response.error(f"Erro no servidor: {str(e)}", 500)
    
@contact_bp.route('/add', methods=["POST"])
@require_auth
def add_contact():
    try:
        user = g.current_user
        data = request.get_json()

        if not data:
            return Response.error("Dados inválidos")
        
        contact_user_id = data.get('contact_user_id')
        contact_name = data.get('contact_name')

        if not contact_user_id:
            return Response.error("ID do contato é obrigatório")
        
        contact, error = ContactService.add_contact(
            user.id,
            contact_user_id,
            contact_name
        )

        if not contact:
            return Response.error(error)
        
        return Response.created({
            'contact': contact.to_dict()
        }, "Contato criado com sucesso")
    
    except Exception as e:
        return Response.error(f"Erro no servidor: {str(e)}", 500)
    
@contact_bp.route('/<int:contact_id>', methods=["PUT"])
@require_auth
def update_contact(contact_id):
    try:
        user = g.current_user
        data = request.get_json()

        if not data:
            return Response.error("Dados inválidos")
        
        new_name = data.get('contact_name')

        if not new_name:
            return Response.error("Nome do contato é obrigatório")
        
        success, error = ContactService.update_contact_name(
            contact_id,
            user.id,
            new_name
        )

        if not success:
            return Response.error(error)
        
        return Response.success(message="Contato atualizado com sucesso")
    
    except Exception as e:
        return Response.error(f"Erro no servidor: {str(e)}", 500)

@contact_bp.route('/<int:contact_id>', methods=["DELETE"])
@require_auth
def remove_contact(contact_id):
    try:
        user = g.current_user

        success, error = ContactService.remove_contact(contact_id, user.id)

        if not success:
            return Response.error(error)
        
        return Response.success(message="Contato removido com sucesso")
    
    except Exception as e:
        return Response.error(f"Erro no servidor: {str(e)}", 500)

@contact_bp.route('/search', methods=["GET"])
@require_auth
def search_users():
    try:
        user = g.current_user
        search_term = request.args.get('q', '').strip()

        if len(search_term) < 2:
            return Response.error("O termo de busca deve ter pelo menos 2 caracteres")
        
        users = ContactService.search_users_to_add(user.id, search_term)

        return Response.success({
            'users': users
        })
    
    except Exception as e:
        return Response.error(f"Erro no servidor: {str(e)}", 500)