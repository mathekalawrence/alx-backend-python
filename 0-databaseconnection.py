import sqlite3

class DatabaseConnection:
    def __init__(self, db_path):
        self.db_path = db_path
        self.connection = None
        self.cursor = None
    
    def __enter__(self):
        #Enter the runtime context and return the database connection

        self.connection = sqlite3.connect(self.db_path)
        self.cursor = self.connection.cursor()
        print(f"Connected to database: {self.db_path}")
        return self.cursor
    
    def __exit__(self, exc_type, exc_val, exc_tb):

        #Exit the runtime context and close the database connection
        if self.cursor:
            self.cursor.close()
            print("Cursor closed")
        
        if self.connection:
            if exc_type is not None:
                # If there was an exception, rollback any changes
                self.connection.rollback()
                print("Transaction rolled back due to exception")
            else:
                # If no exception, commit any changes
                self.connection.commit()
                print("Transaction committed")
            
            self.connection.close()
            print("Database connection closed")


# Example usage with the context manager
if __name__ == "__main__":
    # Creates a sample database and table for demonstration
    def setup_sample_database():
        conn = sqlite3.connect('muia.db')
        cursor = conn.cursor()
        
        # Create users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL
            )
        ''')
        
        # Inserting sample data
        cursor.execute("DELETE FROM users")  # Clears existing data
        sample_users = [
            ('Lawrence Muia', 'muial@gmail.com'),
            ('Softect Horizon', 'softect@yahoo.com'),
            ('larry Muia', 'larry@sample.com')
        ]

        cursor.executemany('INSERT INTO users (name, email) VALUES (?, ?)', sample_users)
        
        conn.commit()
        conn.close()
        print("Sample database setup complete")
    
    # Setup the sample database
    setup_sample_database()
    
    # Using the context manager to perform the query
    print("\n--- Using DatabaseConnection context manager ---")
    with DatabaseConnection('muia.db') as cursor:
        cursor.execute("SELECT * FROM users")
        results = cursor.fetchall()
        
        print("\nQuery Results:")
        print("ID | Name        | Email")
        print("-" * 30)
        for row in results:
            print(f"{row[0]:2} | {row[1]:10} | {row[2]}")