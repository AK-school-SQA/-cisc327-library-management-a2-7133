import database
import sqlite3

def clear_database():
    """Completely clear all data from the library database"""
    print("Starting database cleanup...")
    
    conn = database.get_db_connection()
    try:
        # Turn off foreign key checks temporarily to ensure clean deletion
        conn.execute('PRAGMA foreign_keys = OFF')
        
        # Get all tables in the database
        tables = conn.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name NOT LIKE 'sqlite_%'
        """).fetchall()
        
        # Delete all data from each table
        for table in tables:
            table_name = table[0]
            print(f"Clearing table: {table_name}")
            conn.execute(f'DELETE FROM {table_name}')
            # Reset the auto-increment counter
            conn.execute(f'DELETE FROM sqlite_sequence WHERE name="{table_name}"')
        
        # Turn foreign key checks back on
        conn.execute('PRAGMA foreign_keys = ON')
        
        # Commit all changes
        conn.commit()
        print("Database cleared successfully!")
        
    except sqlite3.Error as e:
        print(f"Error while clearing database: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    clear_database()