from datetime import datetime

class Message:
    def __init__(self, id=None, sender_id=None, receiver_id=None,
                 content=None, is_read=False, created_at=None):
        self.id = id
        self.sender_id = sender_id
        self.receiver_id = receiver_id
        self.content = content
        self.is_read = is_read
        self.created_at = created_at or datetime.now()
    
    def to_dict(self):
        return {
            'id': self.id,
            'sender_id': self.sender_id,
            'receiver_id': self.receiver_id,
            'content': self.content,
            'is_read': self.is_read,
            'created_at': self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at
        }
    
    @staticmethod
    def from_dict(data):
        return Message(
            id=data.get('id'),
            sender_id=data.get('sender_id'),
            receiver_id=data.get('receiver_id'),
            content=data.get('content'),
            is_read=data.get('is_read', False),
            created_at=data.get('created_at')
        )
    
    def __repr__(self):
        return f"<Message id={self.id} sender_id={self.sender_id} receiver_id={self.receiver_id}>"