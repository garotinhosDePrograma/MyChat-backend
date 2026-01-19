# app/repositories/push_repository.py

from app.utils.database import Database

class PushRepository:
    """
    Repositório para gerenciar subscriptions de push notifications
    """
    
    @staticmethod
    def create_subscription(user_id, endpoint, p256dh, auth):
        """
        Cria uma nova subscription
        """
        query = """
            INSERT INTO push_subscriptions (user_id, endpoint, p256dh, auth)
            VALUES (%s, %s, %s, %s)
        """
        try:
            Database.execute_query(query, (user_id, endpoint, p256dh, auth))
            return True
        except Exception as e:
            print(f"Erro ao criar subscription: {e}")
            return False
    
    @staticmethod
    def find_by_user_id(user_id):
        """
        Busca todas as subscriptions de um usuário
        """
        query = """
            SELECT * FROM push_subscriptions
            WHERE user_id = %s
        """
        return Database.execute_query(query, (user_id,), fetch=True)
    
    @staticmethod
    def find_by_endpoint(endpoint):
        """
        Busca subscription por endpoint
        """
        query = """
            SELECT * FROM push_subscriptions
            WHERE endpoint = %s
        """
        return Database.execute_query(query, (endpoint,), fetch=True, fetch_one=True)
    
    @staticmethod
    def update_subscription(user_id, endpoint, p256dh, auth):
        """
        Atualiza uma subscription existente
        """
        query = """
            UPDATE push_subscriptions
            SET p256dh = %s, auth = %s, updated_at = NOW()
            WHERE user_id = %s AND endpoint = %s
        """
        try:
            rows = Database.execute_query(query, (p256dh, auth, user_id, endpoint))
            return rows > 0
        except Exception as e:
            print(f"Erro ao atualizar subscription: {e}")
            return False
    
    @staticmethod
    def delete_subscription(user_id, endpoint):
        """
        Remove uma subscription
        """
        query = """
            DELETE FROM push_subscriptions
            WHERE user_id = %s AND endpoint = %s
        """
        try:
            rows = Database.execute_query(query, (user_id, endpoint))
            return rows > 0
        except Exception as e:
            print(f"Erro ao deletar subscription: {e}")
            return False
    
    @staticmethod
    def delete_all_by_user(user_id):
        """
        Remove todas as subscriptions de um usuário
        """
        query = """
            DELETE FROM push_subscriptions
            WHERE user_id = %s
        """
        try:
            return Database.execute_query(query, (user_id,))
        except Exception as e:
            print(f"Erro ao deletar subscriptions: {e}")
            return 0
