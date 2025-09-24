import sqlite3
import os
from tabulate import tabulate

def check_sqlite_db(db_path='instance/unicare.db'):
    """Check the SQLite database and print its contents."""
    if not os.path.exists(db_path):
        print(f"Error: Database file not found at {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get list of tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        if not tables:
            print("No tables found in the database.")
            return False
            
        print(f"\nFound {len(tables)} tables in the database:")
        for i, (table_name,) in enumerate(tables, 1):
            print(f"{i}. {table_name}")
            
            # Get table info
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = cursor.fetchall()
            
            print(f"\n  Table structure for '{table_name}':")
            print(tabulate(columns, headers=["CID", "Name", "Type", "Not Null", "Default", "PK"], tablefmt="grid"))
            
            # Get row count
            cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
            count = cursor.fetchone()[0]
            print(f"  Rows: {count}")
            
            # Show sample data if table is not empty
            if count > 0:
                cursor.execute(f"SELECT * FROM {table_name} LIMIT 3;")
                rows = cursor.fetchall()
                
                # Get column names
                col_names = [desc[0] for desc in cursor.description]
                
                print(f"  Sample data (first {min(3, count)} rows):")
                print(tabulate(rows, headers=col_names, tablefmt="grid"))
                
                if count > 3:
                    print(f"  ... and {count - 3} more rows")
            
            print("\n" + "-"*50)
            
        conn.close()
        return True
        
    except Exception as e:
        print(f"Error checking database: {str(e)}")
        if 'conn' in locals():
            conn.close()
        return False

if __name__ == "__main__":
    print("="*50)
    print("SQLite Database Check")
    print("="*50)
    
    # Check in multiple possible locations
    db_paths = [
        'instance/unicare.db',
        'unicare.db',
        'app/instance/unicare.db'
    ]
    
    found = False
    for db_path in db_paths:
        if os.path.exists(db_path):
            print(f"\nFound database at: {db_path}")
            if check_sqlite_db(db_path):
                found = True
                break
    
    if not found:
        print("\nCould not find the SQLite database in any of these locations:")
        for path in db_paths:
            print(f"- {path}")
        print("\nPlease make sure the database file exists and is accessible.")
        print("You may need to run the setup script first.")
