import time
import sqlite3
import functools

def with_db_connection(func):

    """
    Decorator that automatically handles database connections.
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
            print(f"Database connection error: {e}")
            raise
        finally:
            conn.close()
    return wrapper

def retry_on_failure(retries=3, delay=2):

    """
    Decorator that retries a function if it fails due to transient errors.
    
    Args:
        retries (int): Number of retry attempts
        delay (float): Delay between retries in seconds
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(retries + 1):  # +1 for the initial attempt
                try:
                    return func(*args, **kwargs)
                    
                except (sqlite3.OperationalError, sqlite3.DatabaseError) as e:
                    last_exception = e
                    
                    # Checking if this is the last attempt
                    if attempt < retries:
                        wait_time = delay * (2 ** attempt)  # Exponential backoff
                        print(f"! Attempt {attempt + 1} failed: {e}")
                        print(f"🔄 Retrying in {wait_time} seconds... (Attempt {attempt + 2}/{retries + 1})")
                        time.sleep(wait_time)
                    else:
                        print(f"❌ All {retries + 1} attempts failed. Last error: {e}")
                        raise
                        
                except Exception as e:
                    # For non-database errors, don't retry
                    print(f"❌ Non-retryable error: {e}")
                    raise
                    
            # This may possibly never be reached, but just in case
            raise last_exception
            
        return wrapper
    return decorator

@with_db_connection
@retry_on_failure(retries=3, delay=1)
def fetch_users_with_retry(conn):
    """
    Fetch all users from the database with automatic retry on failure.
    """
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    return cursor.fetchall()

# Attempting to fetch users with automatic retry on failure
if __name__ == "__main__":
    try:
        users = fetch_users_with_retry()
        print(f"✅ Successfully fetched {len(users)} users")
        print(users)
    except Exception as e:
        print(f"❌ Final failure: {e}")
