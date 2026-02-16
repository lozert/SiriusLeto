import psycopg2
from psycopg2.extras import RealDictCursor

# Настройки подключения
PG_HOST = 'localhost'
PG_PORT = '5433'
PG_DB = 'scopus'
PG_USER = 'postgres'
PG_PASSWORD = 'root'

# Подключение к PostgreSQL
def connect_postgres():
    connection = psycopg2.connect(
        host=PG_HOST,
        port=PG_PORT,
        database=PG_DB,
        user=PG_USER,
        password=PG_PASSWORD,
        client_encoding='UTF-8'  # Явно указываем кодировку
    )
    return connection

# Пример выполнения запроса
def execute_query(query: str, params=None):
    connection = connect_postgres()
    try:
        with connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(query, params)
            if query.strip().upper().startswith('SELECT'):
                result = cursor.fetchall()
            else:
                connection.commit()
                result = cursor.rowcount
        return result
    finally:
        connection.close()

# Пример использования
if __name__ == "__main__":
    # Пример запроса
    query = "SELECT * FROM publication LIMIT 5;"
    
    results = execute_query(query)
    for row in results:
        print(row)