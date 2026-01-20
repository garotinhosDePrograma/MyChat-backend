# app/services/push_service.py - VERSÃO COM HTTPX (SEM PYWEBPUSH)

import json
import time
import base64
import hashlib
import hmac
from urllib.parse import urlparse
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.backends import default_backend
import httpx

from py_vapid import Vapid01, Vapid02
from app.repositories.push_repository import PushRepository
from app.config import Config

class PushService:
    """
    Serviço para gerenciar Web Push Notifications - USANDO HTTPX
    """
    
    _vapid_instance = None
    _processing = {}
    _processing_timeout = 10
    
    @staticmethod
    def _get_vapid():
        """Obtém instância Vapid (com cache)"""
        if PushService._vapid_instance is None:
            try:
                private_key = Config.VAPID_PRIVATE_KEY
                
                if not private_key:
                    raise ValueError("VAPID_PRIVATE_KEY não configurada")
                
                print(f"🔑 Carregando VAPID (tamanho: {len(private_key)} chars)")
                
                try:
                    vapid = Vapid02.from_string(private_key)
                    print("✅ Usando Vapid02 (draft-02)")
                except Exception as e1:
                    print(f"⚠️ Vapid02 falhou: {e1}")
                    try:
                        vapid = Vapid01.from_string(private_key)
                        print("✅ Usando Vapid01 (draft-01)")
                    except Exception as e2:
                        print(f"❌ Vapid01 falhou: {e2}")
                        raise Exception(f"Não foi possível carregar VAPID: {e1}, {e2}")
                
                PushService._vapid_instance = vapid
                print("✅ Vapid carregado com sucesso")
                
            except Exception as e:
                print(f"❌ Erro ao carregar Vapid: {e}")
                raise
        
        return PushService._vapid_instance
    
    @staticmethod
    def get_vapid_public_key():
        """Retorna a chave pública VAPID"""
        return Config.VAPID_PUBLIC_KEY
    
    @staticmethod
    def _generate_vapid_headers(endpoint, vapid_claims):
        """
        Gera headers VAPID para autenticação
        """
        try:
            vapid = PushService._get_vapid()
            
            # Extrair audience do endpoint
            parsed = urlparse(endpoint)
            audience = f"{parsed.scheme}://{parsed.netloc}"
            
            # Gerar JWT token
            vapid_claims['aud'] = audience
            vapid_claims['exp'] = str(int(time.time()) + 43200)  # 12 horas
            
            # Assinar com VAPID
            if isinstance(vapid, Vapid02):
                token = vapid.sign(vapid_claims, crypto_key=Config.VAPID_PUBLIC_KEY)
            else:
                token = vapid.sign(vapid_claims)
            
            return {
                'Authorization': f'vapid t={token}, k={Config.VAPID_PUBLIC_KEY}'
            }
            
        except Exception as e:
            print(f"❌ Erro ao gerar headers VAPID: {e}")
            raise
    
    @staticmethod
    def save_subscription(user_id, subscription_data):
        """Salva a subscription de um usuário"""
        try:
            endpoint = subscription_data.get('endpoint')
            p256dh = subscription_data.get('keys', {}).get('p256dh')
            auth = subscription_data.get('keys', {}).get('auth')
            
            if not all([endpoint, p256dh, auth]):
                print("❌ Dados de subscription incompletos")
                return False
            
            existing = PushRepository.find_by_endpoint(endpoint)
            
            if existing:
                return PushRepository.update_subscription(
                    user_id, endpoint, p256dh, auth
                )
            else:
                return PushRepository.create_subscription(
                    user_id, endpoint, p256dh, auth
                )
                
        except Exception as e:
            print(f"❌ Erro ao salvar subscription: {e}")
            return False
    
    @staticmethod
    def remove_subscription(user_id, endpoint):
        """Remove a subscription de um usuário"""
        try:
            return PushRepository.delete_subscription(user_id, endpoint)
        except Exception as e:
            print(f"❌ Erro ao remover subscription: {e}")
            return False
    
    @staticmethod
    def send_notification(user_id, title, body, data=None, icon=None, badge=None):
        """
        Envia uma notificação push para um usuário - USANDO HTTPX
        """
        try:
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
            
            payload_json = json.dumps(payload)
            
            success_count = 0
            
            # Validar VAPID_CLAIM_EMAIL
            claim_email = Config.VAPID_CLAIM_EMAIL
            if not claim_email:
                claim_email = 'mailto:admin@mychat.com'
                print(f"⚠️ VAPID_CLAIM_EMAIL não configurado, usando padrão: {claim_email}")
            
            if not claim_email.startswith('mailto:'):
                claim_email = f'mailto:{claim_email}'
            
            print(f"📧 Usando VAPID claim email: {claim_email}")
            print(f"📤 Enviando push para {len(subscriptions)} subscription(s)")
            
            # Criar cliente httpx
            with httpx.Client(timeout=10.0) as client:
                for sub in subscriptions:
                    try:
                        endpoint = sub['endpoint']
                        
                        # Gerar headers VAPID
                        vapid_headers = PushService._generate_vapid_headers(
                            endpoint,
                            {'sub': claim_email}
                        )
                        
                        # Headers completos
                        headers = {
                            **vapid_headers,
                            'Content-Type': 'application/octet-stream',
                            'Content-Encoding': 'aes128gcm',
                            'TTL': '86400'
                        }
                        
                        # ✅ ENVIAR PUSH VIA HTTPX (NÃO USA urllib3/requests)
                        response = client.post(
                            endpoint,
                            content=payload_json.encode('utf-8'),
                            headers=headers
                        )
                        
                        if response.status_code in [200, 201]:
                            success_count += 1
                            print(f"✅ Push enviado para endpoint: {endpoint[:50]}...")
                        elif response.status_code in [404, 410]:
                            print(f"🗑️ Subscription expirada, removendo...")
                            PushRepository.delete_subscription(user_id, endpoint)
                        else:
                            print(f"⚠️ Status {response.status_code}: {response.text[:100]}")
                        
                    except httpx.HTTPError as e:
                        print(f"❌ Erro HTTP ao enviar push: {e}")
                    except Exception as e:
                        print(f"❌ Erro inesperado ao enviar push:")
                        print(f"   Type: {type(e).__name__}")
                        print(f"   Message: {str(e)}")
            
            return success_count > 0
            
        except Exception as e:
            print(f"❌ Erro ao enviar notificação: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    @staticmethod
    def send_message_notification(sender_user, receiver_user_id, message_content):
        """
        Envia notificação de nova mensagem
        """
        notification_key = f"{sender_user.id}-{receiver_user_id}-{hash(message_content[:50])}"
        
        current_time = time.time()
        PushService._processing = {
            k: v for k, v in PushService._processing.items()
            if current_time - v < PushService._processing_timeout
        }
        
        if notification_key in PushService._processing:
            print(f"⚠️ Notificação duplicada detectada, pulando")
            return False
        
        try:
            PushService._processing[notification_key] = current_time
            
            preview = message_content[:100]
            if len(message_content) > 100:
                preview += '...'
            
            result = PushService.send_notification(
                user_id=receiver_user_id,
                title=f"💬 {sender_user.name}",
                body=preview,
                data={
                    'type': 'message',
                    'senderId': sender_user.id,
                    'senderName': sender_user.name
                }
            )
            
            return result
            
        finally:
            import threading
            def cleanup():
                time.sleep(1)
                PushService._processing.pop(notification_key, None)
            
            threading.Thread(target=cleanup, daemon=True).start()
