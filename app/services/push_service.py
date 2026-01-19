# app/services/push_service.py

import json
from pywebpush import webpush, WebPushException
from app.repositories.push_repository import PushRepository
from app.config import Config

class PushService:
    """
    Serviço para gerenciar Web Push Notifications
    """
    
    @staticmethod
    def get_vapid_public_key():
        """
        Retorna a chave pública VAPID
        """
        return Config.VAPID_PUBLIC_KEY
    
    @staticmethod
    def save_subscription(user_id, subscription_data):
        """
        Salva a subscription de um usuário
        
        Args:
            user_id (int): ID do usuário
            subscription_data (dict): Dados da subscription
            
        Returns:
            bool: True se salvo com sucesso
        """
        try:
            endpoint = subscription_data.get('endpoint')
            p256dh = subscription_data.get('keys', {}).get('p256dh')
            auth = subscription_data.get('keys', {}).get('auth')
            
            if not all([endpoint, p256dh, auth]):
                print("❌ Dados de subscription incompletos")
                return False
            
            # Verificar se já existe
            existing = PushRepository.find_by_endpoint(endpoint)
            
            if existing:
                # Atualizar
                return PushRepository.update_subscription(
                    user_id, endpoint, p256dh, auth
                )
            else:
                # Criar novo
                return PushRepository.create_subscription(
                    user_id, endpoint, p256dh, auth
                )
                
        except Exception as e:
            print(f"❌ Erro ao salvar subscription: {e}")
            return False
    
    @staticmethod
    def remove_subscription(user_id, endpoint):
        """
        Remove a subscription de um usuário
        
        Args:
            user_id (int): ID do usuário
            endpoint (str): Endpoint da subscription
            
        Returns:
            bool: True se removido com sucesso
        """
        try:
            return PushRepository.delete_subscription(user_id, endpoint)
        except Exception as e:
            print(f"❌ Erro ao remover subscription: {e}")
            return False
    
    @staticmethod
    def send_notification(user_id, title, body, data=None, icon=None, badge=None):
        """
        Envia uma notificação push para um usuário
        
        Args:
            user_id (int): ID do usuário destinatário
            title (str): Título da notificação
            body (str): Corpo da notificação
            data (dict): Dados adicionais
            icon (str): URL do ícone
            badge (str): URL do badge
            
        Returns:
            bool: True se enviado com sucesso
        """
        try:
            # Buscar subscriptions do usuário
            subscriptions = PushRepository.find_by_user_id(user_id)
            
            if not subscriptions:
                print(f"⚠️ Nenhuma subscription encontrada para user {user_id}")
                return False
            
            # Preparar payload
            payload = {
                'title': title,
                'body': body,
                'icon': icon or '/assets/icons/icon-192.png',
                'badge': badge or '/assets/icons/icon-192.png',
                'data': data or {}
            }
            
            success_count = 0
            
            # Enviar para todas as subscriptions do usuário
            for sub in subscriptions:
                try:
                    subscription_info = {
                        'endpoint': sub['endpoint'],
                        'keys': {
                            'p256dh': sub['p256dh'],
                            'auth': sub['auth']
                        }
                    }
                    
                    # Enviar push
                    webpush(
                        subscription_info=subscription_info,
                        data=json.dumps(payload),
                        vapid_private_key=Config.VAPID_PRIVATE_KEY,
                        vapid_claims={
                            'sub': f'mailto:{Config.VAPID_CLAIM_EMAIL}'
                        }
                    )
                    
                    success_count += 1
                    print(f"✅ Push enviado para endpoint: {sub['endpoint'][:50]}...")
                    
                except WebPushException as e:
                    print(f"⚠️ Erro ao enviar push: {e}")
                    
                    # Se subscription expirou, remover
                    if e.response and e.response.status_code in [404, 410]:
                        print(f"🗑️ Removendo subscription expirada")
                        PushRepository.delete_subscription(user_id, sub['endpoint'])
                        
            return success_count > 0
            
        except Exception as e:
            print(f"❌ Erro ao enviar notificação: {e}")
            return False
    
    @staticmethod
    def send_message_notification(sender_user, receiver_user_id, message_content):
        """
        Envia notificação de nova mensagem
        
        Args:
            sender_user: Objeto User do remetente
            receiver_user_id (int): ID do destinatário
            message_content (str): Conteúdo da mensagem
            
        Returns:
            bool: True se enviado com sucesso
        """
        # Truncar mensagem se muito longa
        preview = message_content[:100]
        if len(message_content) > 100:
            preview += '...'
        
        return PushService.send_notification(
            user_id=receiver_user_id,
            title=f"💬 {sender_user.name}",
            body=preview,
            data={
                'type': 'message',
                'senderId': sender_user.id,
                'senderName': sender_user.name
            }
        )
