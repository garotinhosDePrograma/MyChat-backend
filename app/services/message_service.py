from app.models.message import Message
from app.repositories.message_repository import MessageRepository
from app.repositories.user_repository import UserRepository
from app.repositories.contact_repository import ContactRepository

class MessageService:
    @staticmethod
    def send_message(sender_id, receiver_id, content):
        if not content or not content.strip():
            return None, "A mensagem não pode estar vazia"
        
        if len(content) > 5000:
            return None, "A mensagem é muito longa (máximo 5000 caracteres)"
        
        if sender_id == receiver_id:
            return None, "Você não pode enviar mensagem para si mesmo"
        
        receiver = UserRepository.find_by_id(receiver_id)
        if not receiver:
            return None, "Destinatário não encontrado"
        
        message = Message(
            sender_id=sender_id,
            receiver_id=receiver_id,
            content=content.strip(),
            is_read=False
        )
        
        try:
            message = MessageRepository.create(message)
            return message, None
        except Exception as e:
            return None, f"Erro ao enviar mensagem: {str(e)}"
    
    @staticmethod
    def get_conversation(user_id, contact_user_id, limit=50):
        try:
            messages = MessageRepository.get_conversation(user_id, contact_user_id, limit)
            
            MessageRepository.mark_as_read(user_id, contact_user_id)
            
            return messages
        except Exception as e:
            print(f"Erro ao buscar conversa: {e}")
            return []
    
    @staticmethod
    def mark_conversation_as_read(user_id, sender_id):
        try:
            count = MessageRepository.mark_as_read(user_id, sender_id)
            return count
        except Exception as e:
            print(f"Erro ao marcar mensagens como lidas: {e}")
            return 0
    
    @staticmethod
    def get_unread_count(user_id):
        try:
            return MessageRepository.get_unread_count(user_id)
        except Exception as e:
            print(f"Erro ao contar mensagens não lidas: {e}")
            return 0
    
    @staticmethod
    def get_unread_by_contact(user_id):
        try:
            return MessageRepository.get_unread_by_sender(user_id)
        except Exception as e:
            print(f"Erro ao buscar mensagens não lidas por contato: {e}")
            return {}
    
    @staticmethod
    def delete_message(message_id, user_id):
        message = MessageRepository.find_by_id(message_id)
        
        if not message:
            return False, "Mensagem não encontrada"
        
        if message.sender_id != user_id:
            return False, "Você não tem permissão para deletar esta mensagem"
        
        try:
            success = MessageRepository.delete(message_id)
            if success:
                return True, None
            return False, "Erro ao deletar mensagem"
        except Exception as e:
            return False, f"Erro ao deletar mensagem: {str(e)}"
    
    @staticmethod
    def delete_conversation(user_id, contact_user_id):
        contact_user = UserRepository.find_by_id(contact_user_id)
        if not contact_user:
            return 0, "Contato não encontrado"
        
        try:
            count = MessageRepository.delete_conversation(user_id, contact_user_id)
            return count, None
        except Exception as e:
            return 0, f"Erro ao deletar conversa: {str(e)}"