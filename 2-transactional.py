import sqlite3
import functools

# Copy of the 'with_db_connection' decorator from previous task
def with_db_connection(func):

    """
    Decorator that automatically handles database connections.
    
    Opens a database connection, passes it to the function,
    and closes it afterward.
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        conn = sqlite3.connect('users.db')
        try:
            result = func(conn, *args, **kwargs)
            conn.commit()
            return result
        except Exception as e:
            conn.rollback()
            print(f"Database error: {e}")
            raise
        finally:
            conn.close()
    return wrapper

def transactional(func):

    """
    Decorator that manages database transactions.
    
    Ensures the function is wrapped inside a transaction:
    - Commits if the function completes successfully
    - Rolls back if the function raises an exception
    """

    @functools.wraps(func)
    def wrapper(conn, *args, **kwargs):
        try:
            # Executes the function within transaction context
            result = func(conn, *args, **kwargs)
            # If no exception was raised, the transaction is committed
            conn.commit()
            print(" Transaction committed successfully")
            return result
        except Exception as e:
            # If any exception occurred, the transaction is rolledback
            conn.rollback()
            print(f" Transaction rolled back due to error: {e}")
            raise
    return wrapper

@with_db_connection
@transactional
def update_user_email(conn, user_id, new_email):
    """
    Update user's email with automatic transaction handling.
    
    The decorators ensure:
    1. Database connection is automatically managed
    2. Transaction is automatically committed or rolled back
    """
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET email = ? WHERE id = ?", (new_email, user_id))
    
    # Checking if any row was affected
    if cursor.rowcount == 0:
        raise ValueError(f"No user found with ID: {user_id}")
    
    print(f" Updated email for user {user_id} to: {new_email}")
    return cursor.rowcount

# Updating user's email with automatic transaction handling
if __name__ == "__main__":
    try:
        result = update_user_email(user_id=1, new_email='Crawford_Cartwright@hotmail.com')
        print(f"Update successful: {result} row(s) affected")
    except Exception as e:
        print(f"Update failed: {e}")