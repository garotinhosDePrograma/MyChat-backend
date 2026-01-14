from app.models.message import Message
from app.utils.database import Database

class MessageRepository:
    @staticmethod
    def create(message):
        query = """
            INSERT INTO messages (sender_id, receiver_id, content, is_read)
            VALUES (%s,%s,%s,%s)
        """
        params = (message.sender_id, message.receiver_id, message.content, message.is_read)
        message_id = Database.execute_query(query, params)
        message.id = message_id
        return message
    
    @staticmethod
    def find_by_id(message_id):
        query = "SELECT * FROM messages WHERE id = %s"
        result = Database.execute_query(query, (message_id,), fetch=True, fetch_one=True)
        return Message.from_dict(result) if result else None
    
    @staticmethod
    def get_conversation(user1_id, user2_id, limit=50):
        try:
            results = Database.call_procedure('get_conversation_messages', (user1_id, user2_id, limit))
            return results if results else []
        except Exception as e:
            print(f"Erro ao usar procedure, usando fallback: {e}")
            query = """
                SELECT
                    m.*,
                    u1.name as sender_name,
                    u2.name as receiver_name
                FROM messages
                JOIN users u1 ON m.sender_id = u1.id
                JOIN users u2 ON m.receiver_id = u2.id
                WHERE
                    (m.sender_id = %s AND m.receiver_id = %s)
                    OR
                    (m.sender_id = %s AND m.receiver_id = %s)
                ORDER BY m.created_at DESC
                LIMIT %s
            """
            results = Database.execute_query(
                query,
                (user1_id, user2_id, user2_id, user1_id, limit),
                fetch=True
            )
            return results if results else []
    
    @staticmethod
    def mark_as_read(receiver_id, sender_id):
        query = """
            UPDATE messages
            SET is_read = TRUE
            WHERE receiver_id = %s AND sender_id = %s AND is_read = FALSE
        """
        rows_affected = Database.execute_query(query, (receiver_id, sender_id))
        return rows_affected
    
    @staticmethod
    def get_unread_count(user_id):
        query = """
            SELECT COUNT(*) as count
            FROM messages
            WHERE receiver_id = %s AND is_read = FALSE
        """
        result = Database.execute_query(query, (user_id,), fetch=True, fetch_one=True)
        return result['count'] if result else 0

    @staticmethod
    def get_unread_by_sender(user_id):
        query = """
        SELECT sender_id, COUNT(*) as count
        FROM messages
        WHERE receiver_id = %s AND is_read = FALSE
        GROUP BY sender_id
        """
        results = Database.execute_query(query, (user_id,), fetch=True)

        if not results:
            return {}
        
        return {row['sender_id']: row['count'] for row in results}
    
    @staticmethod
    def delete(message_id):
        query = "DELETE FROM messages WHERE id = %s"
        rows_affected = Database.execute_query(query, (message_id,))
        return rows_affected > 0
    
    @staticmethod
    def delete_conversation(user1_id, user2_id):
        query = """
        DELETE FROM messages
        WHERE
            (sender_id = %s AND receiver_id = %s)
            OR
            (sender_id = %s AND receiver_id = %s)
        """
        rows_affected = Database.execute_query(query, (user1_id, user2_id, user2_id, user1_id))
        return rows_affected