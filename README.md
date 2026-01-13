# MyChat API - Documentação Completa

## Base URL
```
https://mychat-backend-m7el.onrender.com
```

## Autenticação
A maioria dos endpoints requer autenticação via JWT token no header:
```
Authorization: Bearer <seu_token_jwt>
```

---

## 📋 Endpoints de Autenticação

### 1. Registrar Usuário
**POST** `/api/auth/register`

**Body:**
```json
{
  "name": "João Silva",
  "email": "joao@example.com",
  "password": "senha123"
}
```

**Response 201:**
```json
{
  "success": true,
  "message": "Usuário registrado com sucesso",
  "data": {
    "user": {
      "id": 1,
      "name": "João Silva",
      "email": "joao@example.com",
      "created_at": "2026-01-10T12:00:00",
      "updated_at": "2026-01-10T12:00:00"
    },
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }
}
```

### 2. Login
**POST** `/api/auth/login`

**Body:**
```json
{
  "email": "joao@example.com",
  "password": "senha123"
}
```

**Response 200:**
```json
{
  "success": true,
  "message": "Login realizado com sucesso",
  "data": {
    "user": {...},
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }
}
```

### 3. Obter Dados do Usuário Autenticado
**GET** `/api/auth/me`

**Headers:** `Authorization: Bearer <token>`

**Response 200:**
```json
{
  "success": true,
  "data": {
    "user": {
      "id": 1,
      "name": "João Silva",
      "email": "joao@example.com",
      "created_at": "2026-01-10T12:00:00",
      "updated_at": "2026-01-10T12:00:00"
    }
  }
}
```

### 4. Verificar Token
**GET** `/api/auth/verify`

**Headers:** `Authorization: Bearer <token>`

**Response 200:**
```json
{
  "success": true,
  "message": "Token válido"
}
```

---

## 👥 Endpoints de Contatos

### 1. Listar Contatos
**GET** `/api/contacts/`

**Headers:** `Authorization: Bearer <token>`

**Response 200:**
```json
{
  "success": true,
  "data": {
    "contacts": [
      {
        "contact_id": 1,
        "contact_user_id": 2,
        "contact_name": "Maria Santos",
        "user_name": "Maria Santos",
        "user_email": "maria@example.com",
        "last_message": "Oi, tudo bem?",
        "last_message_time": "2026-01-10T14:30:00",
        "unread_count": 3
      }
    ]
  }
}
```

### 2. Adicionar Contato
**POST** `/api/contacts/add`

**Headers:** `Authorization: Bearer <token>`

**Body:**
```json
{
  "contact_user_id": 2,
  "contact_name": "Maria" // Opcional
}
```

**Response 201:**
```json
{
  "success": true,
  "message": "Contato adicionado com sucesso",
  "data": {
    "contact": {
      "id": 1,
      "user_id": 1,
      "contact_user_id": 2,
      "contact_name": "Maria",
      "created_at": "2026-01-10T12:00:00"
    }
  }
}
```

### 3. Atualizar Nome do Contato
**PUT** `/api/contacts/{contact_id}`

**Headers:** `Authorization: Bearer <token>`

**Body:**
```json
{
  "contact_name": "Maria Silva"
}
```

**Response 200:**
```json
{
  "success": true,
  "message": "Contato atualizado com sucesso"
}
```

### 4. Remover Contato
**DELETE** `/api/contacts/{contact_id}`

**Headers:** `Authorization: Bearer <token>`

**Response 200:**
```json
{
  "success": true,
  "message": "Contato removido com sucesso"
}
```

### 5. Buscar Usuários para Adicionar
**GET** `/api/contacts/search?q={termo}`

**Headers:** `Authorization: Bearer <token>`

**Query Params:**
- `q`: termo de busca (mínimo 2 caracteres)

**Response 200:**
```json
{
  "success": true,
  "data": {
    "users": [
      {
        "id": 2,
        "name": "Maria Santos",
        "email": "maria@example.com"
      }
    ]
  }
}
```

---

## 💬 Endpoints de Mensagens

### 1. Enviar Mensagem
**POST** `/api/messages/send`

**Headers:** `Authorization: Bearer <token>`

**Body:**
```json
{
  "receiver_id": 2,
  "content": "Olá, tudo bem?"
}
```

**Response 201:**
```json
{
  "success": true,
  "message": "Mensagem enviada com sucesso",
  "data": {
    "message": {
      "id": 1,
      "sender_id": 1,
      "receiver_id": 2,
      "content": "Olá, tudo bem?",
      "is_read": false,
      "created_at": "2026-01-10T14:30:00"
    }
  }
}
```

### 2. Obter Conversa
**GET** `/api/messages/conversation/{contact_user_id}?limit=50`

**Headers:** `Authorization: Bearer <token>`

**Query Params:**
- `limit`: número máximo de mensagens (padrão: 50, máximo: 200)

**Response 200:**
```json
{
  "success": true,
  "data": {
    "messages": [
      {
        "id": 1,
        "sender_id": 1,
        "receiver_id": 2,
        "content": "Olá!",
        "is_read": true,
        "created_at": "2026-01-10T14:30:00",
        "sender_name": "João Silva",
        "receiver_name": "Maria Santos"
      }
    ]
  }
}
```

### 3. Marcar Mensagens como Lidas
**PUT** `/api/messages/mark-read/{sender_id}`

**Headers:** `Authorization: Bearer <token>`

**Response 200:**
```json
{
  "success": true,
  "message": "Mensagens marcadas como lidas",
  "data": {
    "count": 5
  }
}
```

### 4. Obter Contagem de Não Lidas
**GET** `/api/messages/unread`

**Headers:** `Authorization: Bearer <token>`

**Response 200:**
```json
{
  "success": true,
  "data": {
    "total": 10,
    "by_contact": {
      "2": 5,
      "3": 5
    }
  }
}
```

### 5. Deletar Mensagem
**DELETE** `/api/messages/{message_id}`

**Headers:** `Authorization: Bearer <token>`

**Response 200:**
```json
{
  "success": true,
  "message": "Mensagem deletada com sucesso"
}
```

### 6. Deletar Conversa Inteira
**DELETE** `/api/messages/conversation/{contact_user_id}`

**Headers:** `Authorization: Bearer <token>`

**Response 200:**
```json
{
  "success": true,
  "message": "15 mensagens deletadas com sucesso",
  "data": {
    "deleted_count": 15
  }
}
```

---

## 🔧 Health Check

### Verificar Status da API
**GET** `/health`

**Response 200:**
```json
{
  "status": "ok",
  "message": "MyChat API is running"
}
```

### Informações da API
**GET** `/`

**Response 200:**
```json
{
  "name": "MyChat API",
  "version": "1.0.0",
  "status": "running",
  "endpoints": {
    "auth": "/api/auth",
    "contacts": "/api/contacts",
    "messages": "/api/messages"
  }
}
```

---

## ❌ Códigos de Erro

- **200** - Sucesso
- **201** - Criado com sucesso
- **400** - Requisição inválida
- **401** - Não autenticado (token ausente ou inválido)
- **403** - Sem permissão
- **404** - Não encontrado
- **500** - Erro interno do servidor

**Formato de erro:**
```json
{
  "success": false,
  "message": "Descrição do erro"
}
```

---

## 🔐 Segurança

- Senhas são criptografadas com **bcrypt**
- Autenticação via **JWT** com expiração de 24 horas
- Token deve ser enviado no header `Authorization: Bearer <token>`
- CORS configurado para aceitar requisições do frontend

---

## 📝 Notas Importantes

1. Todos os endpoints (exceto `/api/auth/register` e `/api/auth/login`) requerem autenticação
2. As mensagens são automaticamente marcadas como lidas quando a conversa é aberta
3. Apenas o remetente pode deletar suas próprias mensagens
4. O limite máximo de mensagens por conversa é 200
5. Mensagens podem ter no máximo 5000 caracteres