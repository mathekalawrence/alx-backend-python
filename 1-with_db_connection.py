import sqlite3
import functools

def with_db_connection(func):
    """
    Decorator that automatically handles database connections.
    
    The decorator does the following:
    1. Opens a database connection
    2. Passes the connection to the decorated function
    3. Closes the connection after function execution
    4. Handles any exceptions that occur

    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Creating database connection
        conn = sqlite3.connect('users.db')
        try:
            # Calling the original function with connection as first argument
            result = func(conn, *args, **kwargs)
            # Committing transaction if everything went well
            conn.commit()
            return result
        except Exception as e:
            # Rollback in case of error
            conn.rollback()
            print(f"Database error: {e}")
            raise
        finally:
            # closing the connection
            conn.close()
    return wrapper

@with_db_connection
def get_user_by_id(conn, user_id):
    
    """
    Function to get a user by ID.
    The decorator automatically provides the database connection.
    """
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    return cursor.fetchone()

# Fetching user by ID with automatic connection handling
user = get_user_by_id(user_id=1)
print(user)