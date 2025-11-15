import time
import sqlite3
import functools
import hashlib
import pickle

# Global cache dictionary
query_cache = {}

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
            print(f"Database error: {e}")
            raise
        finally:
            conn.close()
    return wrapper

def cache_query(func):

    """
    Decorator that caches database query results to avoid redundant calls.
    
    Features:
    - Caches results based on SQL query and parameters
    - Uses hash for efficient cache key generation
    - Includes cache statistics
    - Handles cache invalidation for write operations
    """
    @functools.wraps(func)
    def wrapper(conn, *args, **kwargs):
        # Generating cache key from function name, query, and parameters
        cache_key = _generate_cache_key(func.__name__, *args, **kwargs)
        
        # Checking if result is in cache
        if cache_key in query_cache:
            print(f" Cache HIT for: {args[0] if args else 'query'}")
            return query_cache[cache_key]['result']
        
        # If not in cache, execute query and cache result
        print(f" Cache MISS for: {args[0] if args else 'query'}")
        start_time = time.time()
        result = func(conn, *args, **kwargs)
        execution_time = time.time() - start_time
        
        # Store result in cache with metadata
        query_cache[cache_key] = {
            'result': result,
            'timestamp': time.time(),
            'execution_time': execution_time,
            'query': args[0] if args else 'Unknown'
        }
        
        print(f" Cached result for future use (took {execution_time:.4f}s)")
        return result
    
    return wrapper

def _generate_cache_key(func_name, *args, **kwargs):

    """
    Generate a unique cache key based on function name and arguments.
    
    Uses hashing to create consistent keys regardless of argument order.
    """
    # Create a string representation of the arguments
    key_parts = [func_name]
    
    # Adding positional arguments -typically the SQL query
    for arg in args:
        key_parts.append(str(arg))
    
    # Adding keyword arguments
    for key, value in sorted(kwargs.items()):
        key_parts.append(f"{key}={value}")
    
    # Creating hash of the combined string
    key_string = "|".join(key_parts)
    return hashlib.md5(key_string.encode()).hexdigest()

def get_cache_stats():
    """
    Get statistics about the current cache state.
    """
    total_entries = len(query_cache)
    if total_entries == 0:
        return "Cache is empty"
    
    total_size = sum(len(str(entry['result'])) for entry in query_cache.values())
    avg_execution_time = sum(entry['execution_time'] for entry in query_cache.values()) / total_entries
    
    return {
        'total_entries': total_entries,
        'total_size_bytes': total_size,
        'average_execution_time': avg_execution_time,
        'cache_keys': list(query_cache.keys())
    }

def clear_cache():
    """
    Clear the entire query cache.
    """
    global query_cache
    cleared_count = len(query_cache)
    query_cache = {}
    print(f" Cleared {cleared_count} entries from cache")
    return cleared_count

def invalidate_cache_pattern(pattern):
    """
    Invalidate cache entries where query contains a specific pattern.
    Useful for invalidating cached results after updates.
    """
    global query_cache
    invalidated_count = 0
    
    keys_to_remove = []
    for key, value in query_cache.items():
        if pattern.lower() in value['query'].lower():
            keys_to_remove.append(key)
            invalidated_count += 1
    
    for key in keys_to_remove:
        del query_cache[key]
    
    print(f"🔄 Invalidated {invalidated_count} cache entries matching '{pattern}'")
    return invalidated_count

@with_db_connection
@cache_query
def fetch_users_with_cache(conn, query):
    """
    Fetch users with query result caching.
    """
    cursor = conn.cursor()
    cursor.execute(query)
    return cursor.fetchall()

@with_db_connection
@cache_query
def get_user_by_id(conn, user_id):
    """
    Get specific user by ID with caching.
    """
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    return cursor.fetchone()

@with_db_connection
def update_user_email(conn, user_id, new_email):
    
   # Update user email and invalidate relevant cache entries.
    
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET email = ? WHERE id = ?", (new_email, user_id))
    
    # Invalidate cache entries related to users table
    invalidate_cache_pattern("SELECT * FROM users")
    invalidate_cache_pattern(f"WHERE id = {user_id}")
    
    print(f" Updated user {user_id} and invalidated related cache")
    return cursor.rowcount

# Sample testing
if __name__ == "__main__":
    print("=== Database Query Caching Demo ===\n")
    
    # First call - will execute query and cache result
    print("1. First call (will cache):")
    users = fetch_users_with_cache(query="SELECT * FROM users")
    print(f"   Retrieved {len(users)} users\n")
    
    # Second call - will use cached result
    print("2. Second call (will use cache):")
    users_again = fetch_users_with_cache(query="SELECT * FROM users")
    print(f"   Retrieved {len(users_again)} users (from cache)\n")
    
    # Different query - will execute and cache separately
    print("3. Different query (will cache separately):")
    active_users = fetch_users_with_cache(query="SELECT * FROM users WHERE active = 1")
    print(f"   Retrieved {len(active_users)} active users\n")
    
    # Same query as first - will use cache
    print("4. Same as first query (will use cache):")
    users_cached = fetch_users_with_cache(query="SELECT * FROM users")
    print(f"   Retrieved {len(users_cached)} users (from cache)\n")
    
    # Get user by ID with caching
    print("5. Get user by ID (will cache):")
    user1 = get_user_by_id(user_id=1)
    print(f"   User 1: {user1}\n")
    
    # Same user ID - will use cache
    print("6. Get same user by ID (will use cache):")
    user1_cached = get_user_by_id(user_id=1)
    print(f"   User 1: {user1_cached} (from cache)\n")
    
    # Show cache statistics
    print("7. Cache Statistics:")
    stats = get_cache_stats()
    for key, value in stats.items():
        if key != 'cache_keys':
            print(f"   {key}: {value}")
    
    print(f"\n   Cached queries: {len(stats.get('cache_keys', []))}")
    
    # Demonstrating cache invalidation
    print("\n8. Cache invalidation demo:")
    clear_cache()
    print("   Cache cleared - next call will execute query again")
    
    # This will execute the query again since cache was cleared
    print("\n9. Call after cache clear (will execute):")
    users_fresh = fetch_users_with_cache(query="SELECT * FROM users")
    print(f"   Retrieved {len(users_fresh)} users")