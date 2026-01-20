# app/services/push_service.py - VERSÃO FINAL CORRIGIDA

import json
import time
import base64
import os
from urllib.parse import urlparse
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
import httpx

from py_vapid import Vapid01, Vapid02
from app.repositories.push_repository import PushRepository
from app.config import Config

class PushService:
    """
    Serviço para gerenciar Web Push Notifications
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
    def _base64_url_decode(data):
        """Decodifica Base64URL"""
        padding = '=' * (4 - len(data) % 4)
        return base64.urlsafe_b64decode(data + padding)
    
    @staticmethod
    def _base64_url_encode(data):
        """Codifica em Base64URL"""
        return base64.urlsafe_b64encode(data).rstrip(b'=').decode('utf-8')
    
    @staticmethod
    def _encrypt_payload(payload_json, p256dh, auth):
        """
        Criptografa o payload usando AES-GCM (RFC 8291)
        """
        try:
            # Decodificar chaves do cliente
            client_public_key = PushService._base64_url_decode(p256dh)
            auth_secret = PushService._base64_url_decode(auth)
            
            # Gerar chave ECDH efêmera
            private_key = ec.generate_private_key(ec.SECP256R1(), default_backend())
            public_key = private_key.public_key()
            
            # Serializar chave pública do servidor (65 bytes não comprimida)
            server_public_key = public_key.public_bytes(
                encoding=serialization.Encoding.X962,
                format=serialization.PublicFormat.UncompressedPoint
            )
            
            # Carregar chave pública do cliente
            client_public_key_obj = ec.EllipticCurvePublicKey.from_encoded_point(
                ec.SECP256R1(),
                client_public_key
            )
            
            # Calcular shared secret via ECDH
            shared_secret = private_key.exchange(ec.ECDH(), client_public_key_obj)
            
            # Derivar chave de criptografia usando HKDF
            ikm_info = b'WebPush: info\x00' + client_public_key + server_public_key
            
            ikm = HKDF(
                algorithm=hashes.SHA256(),
                length=32,
                salt=auth_secret,
                info=ikm_info,
                backend=default_backend()
            ).derive(shared_secret)
            
            # Gerar salt aleatório (16 bytes)
            salt = os.urandom(16)
            
            # Derivar CEK (Content Encryption Key)
            cek_info = b'Content-Encoding: aes128gcm\x00'
            
            cek = HKDF(
                algorithm=hashes.SHA256(),
                length=16,
                salt=salt,
                info=cek_info,
                backend=default_backend()
            ).derive(ikm)
            
            # Derivar nonce
            nonce_info = b'Content-Encoding: nonce\x00'
            
            nonce = HKDF(
                algorithm=hashes.SHA256(),
                length=12,
                salt=salt,
                info=nonce_info,
                backend=default_backend()
            ).derive(ikm)
            
            # Preparar payload
            payload_bytes = payload_json.encode('utf-8')
            
            # Padding (mínimo 2 bytes: 0x02 0x00)
            padding = b'\x02\x00'
            plaintext = payload_bytes + padding
            
            # Criptografar com AES-GCM
            aesgcm = AESGCM(cek)
            ciphertext = aesgcm.encrypt(nonce, plaintext, None)
            
            # Montar mensagem final: salt (16) + rs (4) + idlen (1) + keyid (65) + ciphertext
            rs = (4096).to_bytes(4, 'big')  # Record size
            idlen = (65).to_bytes(1, 'big')  # Tamanho da chave pública
            
            encrypted_message = salt + rs + idlen + server_public_key + ciphertext
            
            print(f"🔐 Payload criptografado: {len(encrypted_message)} bytes")
            
            return encrypted_message
            
        except Exception as e:
            print(f"❌ Erro ao criptografar payload: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    @staticmethod
    def _generate_vapid_headers(endpoint, vapid_claims):
        """
        Gera headers VAPID para autenticação
        ✅ FORMATO CORRETO: t=token; k=publicKey
        """
        try:
            vapid = PushService._get_vapid()
            
            # Extrair audience do endpoint
            parsed = urlparse(endpoint)
            audience = f"{parsed.scheme}://{parsed.netloc}"
            
            # Preparar claims
            claims = {
                'sub': vapid_claims.get('sub', 'mailto:admin@mychat.com'),
                'aud': audience,
                'exp': int(time.time()) + 43200  # 12 horas
            }
            
            print(f"🔐 VAPID claims: {claims}")
            
            # ✅ FIX: Assinar corretamente dependendo da versão do Vapid
            if isinstance(vapid, Vapid02):
                # Vapid02 retorna um dicionário com Authorization header
                result = vapid.sign(claims)
                
                # Se retornou um dict com 'Authorization'
                if isinstance(result, dict) and 'Authorization' in result:
                    auth_header = result['Authorization']
                    print(f"✅ VAPID header (Vapid02): {auth_header[:80]}...")
                    return {'Authorization': auth_header}
                else:
                    # Se retornou apenas o token
                    token = result
                    auth_header = f"vapid t={token}, k={Config.VAPID_PUBLIC_KEY}"
                    print(f"✅ VAPID header (manual): {auth_header[:80]}...")
                    return {'Authorization': auth_header}
            else:
                # Vapid01
                token = vapid.sign(claims)
                auth_header = f"WebPush {token}"
                print(f"✅ VAPID header (Vapid01): {auth_header[:80]}...")
                return {'Authorization': auth_header}
            
        except Exception as e:
            print(f"❌ Erro ao gerar headers VAPID: {e}")
            import traceback
            traceback.print_exc()
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
        Envia uma notificação push para um usuário
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
            print(f"📦 Payload JSON ({len(payload_json)} chars): {payload_json[:100]}...")
            
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
                for i, sub in enumerate(subscriptions, 1):
                    try:
                        endpoint = sub['endpoint']
                        p256dh = sub['p256dh']
                        auth = sub['auth']
                        
                        print(f"\n📨 Subscription {i}/{len(subscriptions)}")
                        print(f"   Endpoint: {endpoint[:60]}...")
                        print(f"   p256dh: {p256dh[:20]}...")
                        print(f"   auth: {auth[:20]}...")
                        
                        # ✅ CRIPTOGRAFAR PAYLOAD
                        encrypted_payload = PushService._encrypt_payload(
                            payload_json,
                            p256dh,
                            auth
                        )
                        
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
                        
                        print(f"📋 Headers:")
                        for k, v in headers.items():
                            print(f"   {k}: {v[:80] if len(str(v)) > 80 else v}")
                        
                        # ✅ ENVIAR PUSH COM PAYLOAD CRIPTOGRAFADO
                        response = client.post(
                            endpoint,
                            content=encrypted_payload,
                            headers=headers
                        )
                        
                        print(f"📬 Response: {response.status_code}")
                        
                        if response.status_code in [200, 201]:
                            success_count += 1
                            print(f"✅ Push enviado com sucesso!")
                        elif response.status_code in [404, 410]:
                            print(f"🗑️ Subscription expirada, removendo...")
                            PushRepository.delete_subscription(user_id, endpoint)
                        else:
                            print(f"⚠️ Status {response.status_code}")
                            print(f"   Response: {response.text[:300]}")
                        
                    except httpx.HTTPError as e:
                        print(f"❌ Erro HTTP ao enviar push: {e}")
                    except Exception as e:
                        print(f"❌ Erro inesperado ao enviar push:")
                        print(f"   Type: {type(e).__name__}")
                        print(f"   Message: {str(e)}")
                        import traceback
                        traceback.print_exc()
            
            print(f"\n📊 Resultado: {success_count}/{len(subscriptions)} enviados com sucesso")
            
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
