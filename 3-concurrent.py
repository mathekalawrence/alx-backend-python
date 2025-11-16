import asyncio
import aiosqlite

async def async_fetch_users():
    """
    Asynchronously fetching all users from the database
    """
    try:
        async with aiosqlite.connect('users.db') as db:
            async with db.execute("SELECT * FROM users") as cursor:
                results = await cursor.fetchall()
                print("All users fetched successfully")
                return results
    except Exception as e:
        print(f"Error fetching all users: {e}")
        return []

async def async_fetch_older_users():
    """
    Asynchronously fetches users older than 40 from the database
    """
    try:
        async with aiosqlite.connect('users.db') as db:
            async with db.execute("SELECT * FROM users WHERE age > ?", (40,)) as cursor:
                results = await cursor.fetchall()
                print("Older users fetched successfully")
                return results
    except Exception as e:
        print(f"Error fetching older users: {e}")
        return []

async def fetch_concurrently():
    """
    Execute both queries concurrently using asyncio.gather
    """
    print("Starting concurrent database queries...")
    
    # Execute both queries concurrently
    results = await asyncio.gather(
        async_fetch_users(),
        async_fetch_older_users(),
        return_exceptions=True
    )
    
    return results

def setup_sample_database():
    """
    Setting up a sample database with users table and sample data
    """
    import sqlite3
    
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    # Creates users table with age column
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            age INTEGER NOT NULL
        )
    ''')
    
    # Inserting sample data with ages
    cursor.execute("DELETE FROM users")  # Clears existing data
    sample_users = [
        ('mm', 'mm@example.com', 30),
        ('aa', 'aa@example.com', 22),
        ('dd J', 'dd@example.com', 45),
        ('ee', 'ee@example.com', 28),
        ('ff', 'ff@example.com', 19),
        ('gg', 'gg@example.com', 42),
        ('kk', 'kk@example.com', 55),
        ('jj', 'jj@example.com', 33)
    ]
    cursor.executemany('INSERT INTO users (name, email, age) VALUES (?, ?, ?)', sample_users)
    
    conn.commit()
    conn.close()
    print("Sample database setup complete")

def display_results(all_users, older_users):
    """
    Display the results in a formatted way
    """
    print("\n" + "="*60)
    print("CONCURRENT QUERY RESULTS")
    print("="*60)
    
    print(f"\nALL USERS ({len(all_users)} users):")
    print("ID | Name           | Email              | Age")
    print("-" * 50)
    for row in all_users:
        print(f"{row[0]:2} | {row[1]:13} | {row[2]:18} | {row[3]:3}")
    
    print(f"\nUSERS OLDER THAN 40 ({len(older_users)} users):")
    print("ID | Name           | Email              | Age")
    print("-" * 50)
    for row in older_users:
        print(f"{row[0]:2} | {row[1]:13} | {row[2]:18} | {row[3]:3}")

async def main():
    """
    Main function to run the concurrent database operations
    """
    # Setup the database first
    setup_sample_database()
    
    print("\n" + "="*60)
    print("RUNNING CONCURRENT ASYNCHRONOUS DATABASE QUERIES")
    print("="*60)
    
    # Running the concurrent queries
    start_time = asyncio.get_event_loop().time()
    
    all_users, older_users = await fetch_concurrently()
    
    end_time = asyncio.get_event_loop().time()
    execution_time = end_time - start_time
    
    # Display results
    display_results(all_users, older_users)
    
    print(f"\nExecution time: {execution_time:.4f} seconds")
    print("Both queries executed concurrently!")

if __name__ == "__main__":
    # Run the main async function
    asyncio.run(main())