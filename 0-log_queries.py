import sqlite3
import functools

def log_queries(func):

    """ The Decorator to log SQL queries before execution."""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        query = kwargs.get('query', args[0] if args else 'Unknown query')
        print(f"LOG: Executing SQL - {query}")
        return func(*args, **kwargs)
    return wrapper

@log_queries
def fetch_all_users(query):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()
    return results

# Fetching users while logging the query
users = fetch_all_users(query="SELECT * FROM users")