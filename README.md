# MyChat API - Backend

Sistema de chat em tempo real com autenticação JWT, WebSockets e notificações push.

---

## 🚀 Tecnologias Utilizadas

### Core
- **Python 3.11+**
- **Flask** - Framework web
- **Flask-SocketIO** - WebSockets em tempo real
- **MySQL 8.0+** - Banco de dados
- **Eventlet** - Servidor ASGI

### Segurança
- **JWT (PyJWT)** - Autenticação via tokens
- **bcrypt** - Criptografia de senhas
- **CORS** - Controle de acesso entre origens

### Notificações Push
- **py-vapid** - Geração de chaves VAPID
- **cryptography** - Criptografia AES-GCM (RFC 8291)
- **httpx** - Cliente HTTP para envio de push

---

## 📁 Estrutura do Projeto

```
mychat-backend/
├── app/
│   ├── __init__.py                 # Inicialização do Flask
│   ├── config.py                   # Configurações (DB, JWT, VAPID)
│   ├── controllers/                # Endpoints da API
│   │   ├── auth_controller.py      # Login/Registro
│   │   ├── contact_controller.py   # Gerenciamento de contatos
│   │   ├── message_controller.py   # Envio/recebimento de mensagens
│   │   └── push_controller.py      # Notificações push
│   ├── services/                   # Lógica de negócio
│   │   ├── auth_service.py
│   │   ├── contact_service.py
│   │   ├── message_service.py
│   │   └── push_service.py         # Web Push (RFC 8291)
│   ├── repositories/               # Acesso ao banco de dados
│   │   ├── user_repository.py
│   │   ├── contact_repository.py
│   │   ├── message_repository.py
│   │   └── push_repository.py
│   ├── models/                     # Modelos de dados
│   │   ├── user.py
│   │   ├── contact.py
│   │   └── message.py
│   ├── middlewares/
│   │   └── auth_middleware.py      # Verificação de JWT
│   ├── sockets/
│   │   └── __init__.py             # Eventos WebSocket
│   └── utils/
│       ├── database.py             # Connection pool MySQL
│       └── response.py             # Padronização de respostas
├── run.py                          # Ponto de entrada
├── requirements.txt
├── render.yaml                     # Config para deploy no Render
├── .env.example
└── README.md
```

---

## ⚙️ Configuração Inicial

### 1. Clonar o Repositório
```bash
git clone <seu-repositorio>
cd mychat-backend
```

### 2. Criar Ambiente Virtual
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. Instalar Dependências
```bash
pip install -r requirements.txt
```

### 4. Configurar Variáveis de Ambiente

Copie `.env.example` para `.env` e configure:

```env
# Database (Railway/outro host MySQL)
CONN_URL=mysql://user:password@host:3306/database
# OU
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=sua_senha
DB_NAME=mychat_db

# JWT
JWT_SECRET_KEY=sua_chave_secreta_super_segura
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# Flask
FLASK_ENV=development
FLASK_DEBUG=True
PORT=5000

# VAPID para Push Notifications
VAPID_PUBLIC_KEY=sua_chave_publica_base64url
VAPID_PRIVATE_KEY=sua_chave_privada_pem
VAPID_CLAIM_EMAIL=mailto:admin@seudominio.com

# Frontend URL (para CORS)
FRONTEND_URL=https://seu-frontend.onrender.com
```

#### Gerando Chaves VAPID

```bash
# Instalar vapid localmente
pip install py-vapid

# Gerar chaves
vapid --gen

# Isso retorna:
# Public Key: BOa1b2c3...
# Private Key: -----BEGIN EC PRIVATE KEY-----...
```

**IMPORTANTE:** Para deploy no Render, codifique a private key em Base64:

```bash
# Linux/Mac
echo "-----BEGIN EC PRIVATE KEY-----
MHcCAQEEIExamplePrivateKeyHere...
-----END EC PRIVATE KEY-----" | base64 -w 0

# Windows (PowerShell)
[Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes("-----BEGIN EC PRIVATE KEY-----..."))
```

Use a versão Base64 na variável `VAPID_PRIVATE_KEY_BASE64` no Render.

---

## 🗄️ Banco de Dados

### Executar Script SQL

1. Acesse o MySQL:
```bash
mysql -u root -p
```

2. Execute o script:
```sql
CREATE DATABASE mychat_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE mychat_db;
SOURCE mychat.sql;
```

### Tabelas Criadas

- **users** - Usuários do sistema
- **contacts** - Relacionamentos entre usuários
- **messages** - Mensagens trocadas
- **push_subscriptions** - Subscriptions de notificações push

---

## 🏃 Executar Localmente

```bash
# Com Flask dev server (NÃO para produção)
python run.py

# Com Gunicorn (produção local)
gunicorn --worker-class gevent --workers 1 --bind 0.0.0.0:5000 run:app
```

API estará disponível em: `http://localhost:5000`

---

## 📡 Endpoints da API

### Autenticação

| Método | Endpoint | Descrição | Auth |
|--------|----------|-----------|------|
| POST | `/api/auth/register` | Registrar usuário | ❌ |
| POST | `/api/auth/login` | Fazer login | ❌ |
| GET | `/api/auth/me` | Dados do usuário | ✅ |
| GET | `/api/auth/verify` | Verificar token | ✅ |

### Contatos

| Método | Endpoint | Descrição | Auth |
|--------|----------|-----------|------|
| GET | `/api/contacts` | Listar contatos | ✅ |
| POST | `/api/contacts/add` | Adicionar contato | ✅ |
| PUT | `/api/contacts/:id` | Atualizar nome | ✅ |
| DELETE | `/api/contacts/:id` | Remover contato | ✅ |
| GET | `/api/contacts/search?q=termo` | Buscar usuários | ✅ |

### Mensagens

| Método | Endpoint | Descrição | Auth |
|--------|----------|-----------|------|
| POST | `/api/messages/send` | Enviar mensagem | ✅ |
| GET | `/api/messages/conversation/:id` | Obter conversa | ✅ |
| PUT | `/api/messages/mark-read/:id` | Marcar como lida | ✅ |
| GET | `/api/messages/unread` | Contador não lidas | ✅ |
| DELETE | `/api/messages/:id` | Deletar mensagem | ✅ |
| DELETE | `/api/messages/conversation/:id` | Deletar conversa | ✅ |

### Push Notifications

| Método | Endpoint | Descrição | Auth |
|--------|----------|-----------|------|
| GET | `/api/push/vapid-public-key` | Obter chave pública | ✅ |
| POST | `/api/push/subscribe` | Salvar subscription | ✅ |
| POST | `/api/push/unsubscribe` | Remover subscription | ✅ |
| POST | `/api/push/test` | Testar notificação | ✅ |

### Health Check

| Método | Endpoint | Descrição | Auth |
|--------|----------|-----------|------|
| GET | `/health` | Status da API | ❌ |
| GET | `/` | Info da API | ❌ |

---

## 🔌 WebSocket Events

### Cliente → Servidor

```javascript
// Conectar
socket.connect({ auth: { token: 'jwt_token' } });

// Entrar em conversa
socket.emit('join_conversation', { contact_user_id: 123 });

// Enviar mensagem
socket.emit('send_message', {
  receiver_id: 123,
  content: 'Olá!',
  temp_id: 'temp_123'
});

// Digitando
socket.emit('typing_start', { contact_user_id: 123 });
socket.emit('typing_stop', { contact_user_id: 123 });

// Marcar como lida
socket.emit('message_read', { sender_id: 123 });
```

### Servidor → Cliente

```javascript
// Mensagem confirmada
socket.on('message_sent', (data) => {
  console.log('Mensagem enviada:', data.message);
});

// Nova mensagem recebida
socket.on('new_message', (message) => {
  console.log('Nova mensagem:', message);
});

// Usuário digitando
socket.on('user_typing', (data) => {
  console.log('Usuário digitando:', data.name);
});

// Status online/offline
socket.on('user_online', (data) => {});
socket.on('user_offline', (data) => {});

// Mensagens lidas
socket.on('messages_read', (data) => {});
```

---

## 📲 Push Notifications

### Implementação (RFC 8291)

1. **Cliente solicita chave VAPID:**
```javascript
const response = await fetch('/api/push/vapid-public-key');
const { publicKey } = await response.json();
```

2. **Cliente cria subscription:**
```javascript
const subscription = await registration.pushManager.subscribe({
  userVisibleOnly: true,
  applicationServerKey: urlBase64ToUint8Array(publicKey)
});
```

3. **Cliente envia subscription ao backend:**
```javascript
await fetch('/api/push/subscribe', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({ subscription })
});
```

4. **Backend envia notificação:**
```python
PushService.send_notification(
    user_id=receiver_id,
    title="💬 João Silva",
    body="Olá, tudo bem?",
    data={'type': 'message', 'senderId': 123}
)
```

### Formato de Notificação Push

```json
{
  "title": "💬 Nome do Remetente",
  "body": "Conteúdo da mensagem...",
  "icon": "/assets/icons/icon-192.png",
  "badge": "/assets/icons/icon-192.png",
  "data": {
    "type": "message",
    "senderId": 123,
    "senderName": "João Silva"
  }
}
```

---

## 🚀 Deploy no Render

### 1. Criar Conta no Render
- Acesse [render.com](https://render.com)
- Conecte com GitHub

### 2. Criar Web Service
- **New → Web Service**
- Conecte seu repositório
- Configurações:
  - **Build Command:** `pip install -r requirements.txt`
  - **Start Command:** `gunicorn --worker-class gevent --workers 1 --bind 0.0.0.0:$PORT run:app`
  - **Environment:** Python 3

### 3. Configurar Variáveis de Ambiente

No painel do Render, adicione:

```
CONN_URL=mysql://user:pass@railway.url/db
JWT_SECRET_KEY=sua_chave_secreta
VAPID_PUBLIC_KEY=BOa1b2c3...
VAPID_PRIVATE_KEY_BASE64=LS0tLS1CRUdJTi...  # Base64 da chave PEM
VAPID_CLAIM_EMAIL=mailto:admin@seudominio.com
FRONTEND_URL=https://seu-frontend.onrender.com
FLASK_ENV=production
FLASK_DEBUG=False
PORT=10000
```

### 4. Deploy Automático
- Cada push no branch `main` faz deploy automático
- Logs disponíveis no painel do Render

---

## 🔧 Troubleshooting

### Erro: "VAPID key inválida"
**Causa:** Chave privada não está em formato PEM correto ou codificação Base64 está errada.

**Solução:**
```bash
# Re-gerar chaves
vapid --gen

# Codificar corretamente
echo "sua_chave_pem_completa" | base64 -w 0
```

### Erro: "Connection pool exhausted"
**Causa:** Muitas conexões simultâneas ao MySQL.

**Solução:** Aumentar `pool_size` em `app/utils/database.py`:
```python
connection_pool = pooling.MySQLConnectionPool(
    pool_name="mychat_pool",
    pool_size=10,  # Aumentar para 10
    ...
)
```

### Erro: "CORS blocked"
**Causa:** URL do frontend não configurada corretamente.

**Solução:** Verificar `FRONTEND_URL` no `.env` ou Render.

### Push Notifications não funcionam
1. Verificar se VAPID keys estão corretas
2. Testar endpoint `/api/push/test`
3. Ver logs no console do navegador
4. Confirmar que subscription foi salva com sucesso

---

## 📊 Monitoramento

### Logs no Render
```bash
# Acessar logs em tempo real
render logs --tail
```

### Health Check
```bash
curl https://sua-api.onrender.com/health
```

Resposta esperada:
```json
{
  "status": "OK",
  "database": "connected",
  "message": "API is running correctly"
}
```

---

## 🔒 Segurança

### Implementações
- ✅ Senhas criptografadas com bcrypt
- ✅ Autenticação JWT com expiração
- ✅ CORS configurado
- ✅ SQL Injection prevention (prepared statements)
- ✅ XSS prevention (escaping de HTML no frontend)
- ✅ Rate limiting (via Render)

### Recomendações Adicionais
- [ ] Implementar rate limiting customizado
- [ ] Adicionar CAPTCHA no registro
- [ ] Logs de auditoria
- [ ] Monitoramento de falhas de login
- [ ] Rotação de secrets JWT

---

## 📝 Licença

MIT License - Sinta-se livre para usar em projetos pessoais e comerciais.

---

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch: `git checkout -b feature/nova-feature`
3. Commit: `git commit -m 'Adiciona nova feature'`
4. Push: `git push origin feature/nova-feature`
5. Abra um Pull Request

---

## 📞 Suporte

- **Email:** l8758711@gmail.com
- **Docs API:** Ver `README.md` na raiz do projeto
