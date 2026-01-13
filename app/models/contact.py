from datetime import datetime

class Contact:
    def __init__(self, id=None, user_id=None, contact_user_id=None,
                 contact_name=None, created_at=None):
        self.id = id
        self.user_id = user_id
        self.contact_user_id = contact_user_id
        self.contact_name = contact_name
        self.created_at = created_at or datetime.now()
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'contact_user_id': self.contact_user_id,
            'contact_name': self.contact_name,
            'created_at': self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at
        }
    
    @staticmethod
    def from_dict(data):
        return Contact(
            id=data.get('id'),
            user_id=data.get('user_id'),
            contact_user_id=data.get('contact_user_id'),
            contact_name=data.get('contact_name'),
            created_at=data.get('created_at')
        )
    
    def __repr__(self):
        return f"<Contact id={self.id} user_id={self.user_id} contact_user_id={self.contact_user_id}>"