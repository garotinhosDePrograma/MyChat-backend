from app.utils.database import Database
from app.models.user import User

class UserRepository:
    @staticmethod
    def create(user):
        query = """
            INSERT INTO users (name, email, password_hash)
            VALUES (%s,%s,%s)
        """
        params = (user.name, user.email, user.password_hash)
        user_id = Database.execute_query(query, params)
        user.id = user_id
        return user

    @staticmethod
    def find_by_id(user_id):
        query = "SELECT * FROM users WHERE id = %s"
        result = Database.execute_query(query, (user_id,), fetch=True, fetch_one=True)
        return User.from_dict(result) if result else None
    
    @staticmethod
    def find_by_email(email):
        query = "SELECT * FROM users WHERE email = %s"
        result = Database.execute_query(query, (email,), fetch=True, fetch_one=True)
        return User.from_dict(result) if result else None
    
    @staticmethod
    def email_exists(email):
        query = "SELECT COUNT(*) as count FROM users WHERE email = %s"
        result = Database.execute_query(query, (email,), fetch=True, fetch_one=True)
        return result['count'] > 0 if result else False
    
    @staticmethod
    def update(user):
        query = """
            UPDATE users
            SET name = %s, email = %s
            WHERE id = %s
        """
        params = (user.name, user.email, user.id)
        Database.execute_query(query, params)
        return user
    
    @staticmethod
    def delete(user_id):
        query = "DELETE FROM users WHERE id = %s"
        rows_affected = Database.execute_query(query, (user_id,))
        return rows_affected > 0
    
    @staticmethod
    def search_by_email_or_name(search_term, exclude_user_id=None):
        if exclude_user_id:
            query = """
                SELECT id, name, email, created_at
                FROM users
                WHERE (email LIKE %s OR name LIKE %s) AND id != %s
                LIMIT 20
            """
            params = (f"%{search_term}%", f"%{search_term}%", exclude_user_id)
        else:
            query = """
                SELECT id, name, email, created_at
                FROM users
                WHERE email LIKE %s OR name LIKE %s
                LIMIT 20
            """
            params = (f"%{search_term}%", f"%{search_term}%")
        
        results = Database.execute_query(query, params, fetch=True)
        return [User.from_dict(row) for row in results] if results else []