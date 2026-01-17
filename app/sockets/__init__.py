# app/sockets/__init__.py - VERSÃO OTIMIZADA

from flask_socketio import emit, join_room, leave_room, disconnect
from app.services.auth_service import AuthService
from app.repositories.user_repository import UserRepository
from app.services.message_service import MessageService

connected_users = {}
typing_users = {}

def register_socket_events(socketio):
    
    @socketio.on('connect')
    def handle_connect(auth):
        print(f"Client conectado: {auth}")

        token = auth.get('token') if auth else None
        if not token:
            print("Conexão recusada: sem token")
            disconnect()
            return False
        
        user = AuthService.get_user_from_token(token)
        if not user:
            print("Conexão recusada: token inválido")
            disconnect()
            return False
        
        from flask import request
        connected_users[user.id] = request.sid

        emit('user_online', {
            'user_id': user.id,
            'name': user.name
        }, broadcast=True, skip_sid=request.sid)

        print(f"Usuário {user.name} (ID: {user.id}) conectado")
        return True
    
    # ============================================================
    # SEND MESSAGE - VERSÃO OTIMIZADA COM CONFIRMAÇÃO RÁPIDA
    # ============================================================
    
    @socketio.on('send_message')
    def handle_send_message(data):
        from flask import request 

        receiver_id = data.get('receiver_id')
        content = data.get('content')
        temp_id = data.get('temp_id')  # ⭐ ID temporário do frontend

        if not receiver_id or not content:
            emit('error', {'message': 'Dados inválidos'})
            return
        
        user_id = get_user_id_from_sid(request.sid)
        if not user_id:
            emit('error', {'message': 'Usuario não autenticado'})
            return
        
        # 1️⃣ ENVIAR CONFIRMAÇÃO IMEDIATA (antes de salvar no banco)
        # Isso reduz a latência percebida pelo usuário
        emit('message_sending', {
            'temp_id': temp_id,
            'status': 'processing'
        })
        
        # 2️⃣ SALVAR NO BANCO (assíncrono)
        message, error = MessageService.send_message(user_id, receiver_id, content)

        if error:
            # ❌ ENVIAR ERRO
            emit('message_error', {
                'temp_id': temp_id,
                'message': error
            })
            return
        
        user = UserRepository.find_by_id(user_id)

        message_data = {
            'id': message.id,
            'sender_id': message.sender_id,
            'receiver_id': message.receiver_id,
            'content': message.content,
            'is_read': message.is_read,
            'created_at': message.created_at.isoformat(),
            'sender_name': user.name,
            'temp_id': temp_id  # ⭐ Incluir ID temporário
        }

        # 3️⃣ CONFIRMAR PARA O REMETENTE (com ID real do banco)
        emit('message_confirmed', {
            'temp_id': temp_id,
            'message': message_data
        })

        # 4️⃣ ENVIAR PARA A SALA (ambos usuários)
        room_id = get_room_id(user_id, receiver_id)
        emit('new_message', message_data, room=room_id)

        # 5️⃣ NOTIFICAR DESTINATÁRIO (se estiver online mas em outra conversa)
        if receiver_id in connected_users:
            receiver_sid = connected_users[receiver_id]
            socketio.emit('message_notification', {
                'message': message_data,
                'from_user': {
                    'id': user.id,
                    'name': user.name
                }
            }, room=receiver_sid)
        
        print(f"✅ Mensagem {message.id} enviada de {user_id} para {receiver_id}")
    
    # ============================================================
    # MARCAR COMO ENTREGUE (quando destinatário recebe)
    # ============================================================
    
    @socketio.on('message_delivered')
    def handle_message_delivered(data):
        from flask import request
        
        message_id = data.get('message_id')
        sender_id = data.get('sender_id')
        
        if not message_id or not sender_id:
            return
        
        # Notificar remetente que mensagem foi entregue
        if sender_id in connected_users:
            sender_sid = connected_users[sender_id]
            socketio.emit('message_status_update', {
                'message_id': message_id,
                'status': 'delivered'
            }, room=sender_sid)
    
    # ============================================================
    # OUTROS EVENTOS (mantidos iguais)
    # ============================================================
    
    @socketio.on('disconnect')
    def handle_disconnect():
        from flask import request

        user_id = None
        for uid, sid in connected_users.items():
            if sid == request.sid:
                user_id = uid
                break
        
        if user_id:
            del connected_users[user_id]

            emit('user_offline', {
                'user_id': user_id
            }, broadcast=True)

            print(f"Usuário {user_id} desconectado")
    
    @socketio.on('join_conversation')
    def handle_join_conversation(data):
        from flask import request

        contact_user_id = data.get('contact_user_id')
        if not contact_user_id:
            return
        
        user_id = get_user_id_from_sid(request.sid)
        room_id = get_room_id(user_id, contact_user_id)

        join_room(room_id)
        print(f"Usuário {user_id} entrou na sala {room_id}")
    
    @socketio.on('leave_conversation')
    def handle_leave_conversation(data):
        from flask import request

        contact_user_id = data.get('contact_user_id')
        if not contact_user_id:
            return
        
        user_id = get_user_id_from_sid(request.sid)
        room_id = get_room_id(user_id, contact_user_id)

        leave_room(room_id)
        print(f"Usuário {user_id} saiu da sala {room_id}")
    
    @socketio.on('typing_start')
    def handle_typing_start(data):
        from flask import request
        import time

        contact_user_id = data.get('contact_user_id')
        if not contact_user_id:
            return
        
        user_id = get_user_id_from_sid(request.sid)
        room_id = get_room_id(user_id, contact_user_id)

        if room_id not in typing_users:
            typing_users[room_id] = {}
        typing_users[room_id][user_id] = time.time()

        user = UserRepository.find_by_id(user_id)
        emit('user_typing', {
            'user_id': user_id,
            'name': user.name
        }, room=room_id, skip_sid=request.sid)
    
    @socketio.on('typing_stop')
    def handle_typing_stop(data):
        from flask import request

        contact_user_id = data.get('contact_user_id')
        if not contact_user_id:
            return
        
        user_id = get_user_id_from_sid(request.sid)
        room_id = get_room_id(user_id, contact_user_id)

        if room_id in typing_users and user_id in typing_users[room_id]:
            del typing_users[room_id][user_id]
        
        emit('user_stopped_typing', {
            'user_id': user_id
        }, room=room_id, skip_sid=request.sid)
    
    @socketio.on('message_read')
    def handle_message_read(data):
        from flask import request

        sender_id = data.get('sender_id')
        if not sender_id:
            return
        
        user_id = get_user_id_from_sid(request.sid)

        MessageService.mark_conversation_as_read(user_id, sender_id)

        if sender_id in connected_users:
            sender_sid = connected_users[sender_id]
            socketio.emit('messages_read', {
                'by_user_id': user_id
            }, room=sender_sid)

def get_user_id_from_sid(sid):
    for user_id, socket_id in connected_users.items():
        if socket_id == sid:
            return user_id
    return None

def get_room_id(user1_id, user2_id):
    return f"chat_{min(user1_id, user2_id)}_{max(user1_id, user2_id)}"
