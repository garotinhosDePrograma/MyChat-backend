from app.utils.database import Database
from app.models.contact import Contact

class ContactRepository:
    @staticmethod
    def create(contact):
        query = """
            INSERT INTO contacts (user_id, contact_user_id, contact_name)
            VALUES (%s,%s,%s)
        """
        params = (contact.user_id, contact.contact_user_id, contact.contact_name)
        contact_id = Database.execute_query(query, params)
        contact.id = contact_id
        return contact
    
    @staticmethod
    def find_by_id(contact_id):
        query = "SELECT * FROM contacts WHERE id = %s"
        result = Database.execute_query(query, (contact_id,), fetch=True, fetch_one=True)
        return Contact.from_dict(result) if result else None
    
    @staticmethod
    def find_all_by_user(user_id):
        try:
            results = Database.call_procedure('get_contacts_with_last_message', (user_id,))
            return results if results else []
        except Exception as e:
            print(f"Erro ao usar procedure, usando fallback: {e}")
            query = """
                SELECT
                    c.id as contact_id,
                    c.contact_user_id,
                    c.contact_name,
                    u.name as user_name,
                    u.email as user_email,
                    c.created_at
                FROM contacts c
                JOIN users u ON c.contact_user_id = u.id
                WHERE c.user_id = %s
                ORDER BY c.created_at DESC
            """
            results = Database.execute_query(query, (user_id,), fetch=True)
            return results if results else []
    
    @staticmethod
    def contact_exists(user_id, contact_user_id):
        query = """
            SELECT COUNT(*) as count
            FROM contacts
            WHERE user_id = %s AND contact_user_id = %s
        """
        result = Database.execute_query(query, (user_id, contact_user_id), fetch=True, fetch_one=True)
        return result['count'] > 0 if result else False
    
    @staticmethod
    def update_contact_name(contact_id, new_name):
        query = """
            UPDATE contacts
            SET contact_name = %s
            WHERE id = %s
        """
        rows_affected = Database.execute_query(query, (new_name, contact_id))
        return rows_affected > 0
    
    @staticmethod
    def delete(contact_id):
        query = "DELETE FROM contacts WHERE id = %s"
        rows_affected = Database.execute_query(query, (contact_id,))
        return rows_affected > 0
    
    @staticmethod
    def delete_by_users(user_id, contact_user_id):
        query = "DELETE FROM contacts WHERE user_id = %s AND contact_user_id = %s"
        rows_affected = Database.execute_query(query, (user_id, contact_user_id))
        return rows_affected > 0