import sqlite3

class ExecuteQuery:
    def __init__(self, db_path, query, params=None):
        self.db_path = db_path
        self.query = query
        self.params = params if params is not None else ()
        self.connection = None
        self.cursor = None
        self.results = None
    
    def __enter__(self):
        """Enter the runtime context and execute the query"""
        self.connection = sqlite3.connect(self.db_path)
        self.cursor = self.connection.cursor()
        
        print(f"Executing query: {self.query}")
        if self.params:
            print(f"With parameters: {self.params}")
        
        self.cursor.execute(self.query, self.params)
        self.results = self.cursor.fetchall()
        
        return self.results
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the runtime context and clean up resources"""
        if self.cursor:
            self.cursor.close()
        
        if self.connection:
            if exc_type is not None:
                # Rollback if there was an exception
                self.connection.rollback()
                print(f"Error occurred: {exc_val}")
                print("Transaction rolled back")
            else:
                # Commit if no exception
                self.connection.commit()
                print("Transaction completed successfully")
            
            self.connection.close()
            print("Database connection closed")
        
        # Return False to propagate exceptions, True to suppress them
        return False


# Example usage with the context manager
if __name__ == "__main__":

    # Creates a sample database and table for demonstration
    def setup_sample_database():
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        
        # Create users table with age column
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                age INTEGER NOT NULL
            )
        ''')
        
        # Insert sample data with ages
        cursor.execute("DELETE FROM users")  # Clear existing data
        sample_users = [
            ('Harison M', 'harri@gmil.com', 30),
            ('Juliet Muema', 'juliet@yahoo.com', 22),
            ('Bobi Laura', 'bobi@gmail.com', 35),
            ('Alice Kariuki', 'alicek@kk.com', 28),
            ('Charles Mutinda', 'charlesm@yahoo.com', 19),
            ('Laura Otieno', 'laura@yahoo.com', 42)
        ]
        cursor.executemany('INSERT INTO users (name, email, age) VALUES (?, ?, ?)', sample_users)
        
        conn.commit()
        conn.close()
        print("Sample database setup complete")
    
    # Setup the sample database
    setup_sample_database()
    
    # Using the ExecuteQuery context manager with the specified query and parameter
    print("\n--- Using ExecuteQuery context manager ---")
    
    query = "SELECT * FROM users WHERE age > ?"
    parameter = (25,)
    
    with ExecuteQuery('users.db', query, parameter) as results:
        print(f"\nQuery Results (users with age > 25):")
        print("ID | Name           | Email              | Age")
        print("-" * 50)
        for row in results:
            print(f"{row[0]:2} | {row[1]:13} | {row[2]:18} | {row[3]:3}")
    
    # Demonstrating reusability with different queries
    print("\n--- Reusing with different query ---")
    
    # Querying for users with specific age
    query2 = "SELECT * FROM users WHERE age = ?"
    with ExecuteQuery('users.db', query2, (35,)) as results:
        print(f"\nQuery Results (users with age = 35):")
        print("ID | Name        | Email            | Age")
        print("-" * 45)
        for row in results:
            print(f"{row[0]:2} | {row[1]:10} | {row[2]:16} | {row[3]:3}")
    
    # Query without parameters
    print("\n--- Reusing with query without parameters ---")
    query3 = "SELECT COUNT(*) as total_users FROM users"
    with ExecuteQuery('users.db', query3) as results:
        print(f"\nQuery Results (total users):")
        print(f"Total users: {results[0][0]}")