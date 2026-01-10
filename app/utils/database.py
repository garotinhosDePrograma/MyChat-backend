import mysql.connector
from mysql.connector import pooling, Error
from urllib.parse import urlparse
from contextlib import contextmanager
from app.config import Config

# Variável global para o pool de conexões
connection_pool = None

def init_connection_pool():
    """Inicializa o pool de conexões com o banco de dados"""
    global connection_pool
    
    try:
        # Se houver CONN_URL (Railway), usar ela
        connection_url = Config.DB_CONNECTION_URL if hasattr(Config, 'DB_CONNECTION_URL') else None
        
        if connection_url:
            # Parse da URL de conexão
            parsed_url = urlparse(connection_url)
            config = {
                'host': parsed_url.hostname,
                'port': parsed_url.port or 3306,
                'user': parsed_url.username,
                'password': parsed_url.password,
                'database': parsed_url.path.decode('utf-8').lstrip('/') if isinstance(parsed_url.path, bytes) else parsed_url.path.lstrip('/'),
                'ssl_disabled': False,
            }
        else:
            # Usar configurações individuais do .env
            config = {
                'host': Config.DB_HOST,
                'port': Config.DB_PORT,
                'user': Config.DB_USER,
                'password': Config.DB_PASSWORD,
                'database': Config.DB_NAME,
                'ssl_disabled': False,
            }
        
        connection_pool = pooling.MySQLConnectionPool(
            pool_name="mychat_pool",
            pool_size=5,
            pool_reset_session=True,
            **config
        )
        print("✅ Connection pool criado com sucesso.")
        
    except Error as e:
        print(f"❌ Erro ao criar pool de conexões: {e}")
        connection_pool = None

def get_db():
    """
    Obtém uma conexão do pool ou cria uma nova conexão
    
    Returns:
        Connection: Objeto de conexão MySQL
    """
    if connection_pool:
        try:
            return connection_pool.get_connection()
        except Error as e:
            print(f"Erro ao obter conexão do pool: {e}")
    
    # Fallback: criar conexão direta
    try:
        connection_url = Config.DB_CONNECTION_URL if hasattr(Config, 'DB_CONNECTION_URL') else None
        
        if connection_url:
            parsed_url = urlparse(connection_url)
            return mysql.connector.connect(
                host=parsed_url.hostname,
                port=parsed_url.port or 3306,
                user=parsed_url.username,
                password=parsed_url.password,
                database=parsed_url.path.decode('utf-8').lstrip('/') if isinstance(parsed_url.path, bytes) else parsed_url.path.lstrip('/'),
                ssl_disabled=False
            )
        else:
            return mysql.connector.connect(
                host=Config.DB_HOST,
                port=Config.DB_PORT,
                user=Config.DB_USER,
                password=Config.DB_PASSWORD,
                database=Config.DB_NAME,
                ssl_disabled=False
            )
    except Error as e:
        print(f"Erro ao criar conexão direta: {e}")
        raise

@contextmanager
def get_db_cursor(dictionary=True):
    """
    Context manager para gerenciar cursor do banco de dados
    
    Args:
        dictionary (bool): Se True, retorna resultados como dicionário
    
    Usage:
        with get_db_cursor() as cursor:
            cursor.execute("SELECT * FROM users")
            results = cursor.fetchall()
    """
    conn = get_db()
    cursor = conn.cursor(dictionary=dictionary)
    try:
        yield cursor
        conn.commit()
    except Error as e:
        conn.rollback()
        print(f"Erro no cursor: {e}")
        raise e
    finally:
        cursor.close()
        conn.close()

class Database:
    """Classe para gerenciar operações com o banco de dados"""
    
    @staticmethod
    def execute_query(query, params=None, fetch=False, fetch_one=False):
        """
        Executa uma query no banco de dados usando context manager
        
        Args:
            query (str): Query SQL a ser executada
            params (tuple): Parâmetros da query
            fetch (bool): Se deve retornar resultados (SELECT)
            fetch_one (bool): Se deve retornar apenas um resultado
            
        Returns:
            Para INSERT/UPDATE/DELETE: ID do último registro ou número de linhas afetadas
            Para SELECT: Lista de resultados ou um resultado
        """
        try:
            with get_db_cursor() as cursor:
                cursor.execute(query, params or ())
                
                if fetch:
                    result = cursor.fetchone() if fetch_one else cursor.fetchall()
                    return result
                else:
                    return cursor.lastrowid if cursor.lastrowid else cursor.rowcount
                    
        except Error as e:
            print(f"Erro ao executar query: {e}")
            raise
    
    @staticmethod
    def execute_many(query, data):
        """
        Executa múltiplas inserções/atualizações de uma vez
        
        Args:
            query (str): Query SQL com placeholders
            data (list): Lista de tuplas com os dados
            
        Returns:
            int: Número de linhas afetadas
        """
        try:
            with get_db_cursor() as cursor:
                cursor.executemany(query, data)
                return cursor.rowcount
        except Error as e:
            print(f"Erro ao executar execute_many: {e}")
            raise
    
    @staticmethod
    def call_procedure(procedure_name, params=None):
        """
        Executa uma stored procedure
        
        Args:
            procedure_name (str): Nome da procedure
            params (tuple): Parâmetros da procedure
            
        Returns:
            list: Resultados da procedure
        """
        try:
            with get_db_cursor() as cursor:
                cursor.callproc(procedure_name, params or ())
                
                # Obter todos os result sets
                results = []
                for result in cursor.stored_results():
                    results.extend(result.fetchall())
                
                return results
        except Error as e:
            print(f"Erro ao executar procedure: {e}")
            raise

# Inicializar pool ao importar o módulo
init_connection_pool()