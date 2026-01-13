from app.repositories.contact_repository import ContactRepository
from app.repositories.user_repository import UserRepository
from app.models.contact import Contact

class ContactService:
    @staticmethod
    def add_contact(user_id, contact_user_id, contact_name=None):
        if user_id == contact_user_id:
            return None, "Você não pode adicionar a si mesmo como contato"
        
        contact_user = ContactRepository.find_by_id(contact_user_id)
        if not contact_user:
            return None, "Usuário não encontrado"
        
        if ContactRepository.contact_exists(user_id, contact_user_id):
            return None, "Contato já adicionado"
        
        if not contact_name:
            contact_name = contact_user.name
        
        contact = Contact(
            user_id=user_id,
            contact_user_id=contact_user_id,
            contact_name=contact_name
        )

        try:
            contact = ContactRepository.create(contact)
            return contact, None
        except Exception as e:
            return None, f"Erro ao adicionar contato: {str(e)}"
    
    @staticmethod
    def get_user_contacts(user_id):
        try:
            contacts = ContactRepository.find_all_by_user(user_id)
            return contacts
        except Exception as e:
            print(f"Erro ao buscar contatos: {e}")
            return []
    
    @staticmethod
    def update_contact_name(contact_id, user_id, new_name):
        if not new_name or not new_name.strip():
            return False, "Nome não pode ser vazio"
        
        contact = ContactRepository.find_by_id(contact_id)
        if not contact:
            return False, "Contato não encontrado"
        
        if contact.user_id != user_id:
            return False, "Você não tem permissão para editar este contato"
        
        try:
            success = ContactRepository.update_contact_name(contact_id, new_name.strip())
            if success:
                return True, None
            return False, "Erro ao atualizar contato"
        except Exception as e:
            return False, f"Erro ao atualizar contato: {str(e)}"
    
    @staticmethod
    def remove_contact(contact_id, user_id):
        contact = ContactRepository.find_by_id(contact_id)
        if not contact:
            return False, "Contato não encontrado"
        
        if contact.user_id != user_id:
            return False, "Você não tem permissão para remover esse contato"
        
        try:
            success = ContactRepository.delete(contact_id)
            if success:
                return True, None
            return False, "Erro ao remover contato"
        except Exception as e:
            return False, f"Erro ao remover contato: {str(e)}"
    
    @staticmethod
    def search_users_to_add(user_id, search_term):
        if not search_term or len(search_term.strip()) < 2:
            return []
        
        try:
            users = UserRepository.search_by_email_or_name(search_term.strip(), user_id)
            return [
                {
                    'id': user.id,
                    'name': user.name,
                    'email': user.email
                }
                for user in users
            ]
        except Exception as e:
            print(f"Erro ao buscar usuários: {e}")
            return []