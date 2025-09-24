import os
import sys
from dotenv import load_dotenv

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Load environment variables
load_dotenv()

def test_database_connection():
    print("=== Database Connection Test ===\n")
    
    # Get database URL from environment or use default
    db_url = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost/unicare')
    print(f"Using database URL: {db_url}")
    
    try:
        from sqlalchemy import create_engine
        from sqlalchemy.exc import SQLAlchemyError
        
        print("\nAttempting to connect to the database...")
        engine = create_engine(db_url)
        
        # Test connection
        with engine.connect() as connection:
            print("✅ Successfully connected to the database!")
            
            # Get database version
            result = connection.execute("SELECT version();")
            db_version = result.scalar()
            print(f"\nDatabase version: {db_version}")
            
            # List tables in the database
            print("\nListing tables in the database:")
            result = connection.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public';
            """)
            tables = [row[0] for row in result.fetchall()]
            
            if tables:
                print("\nFound tables:")
                for table in tables:
                    print(f"- {table}")
            else:
                print("\nNo tables found in the database.")
                
    except ImportError as e:
        print(f"❌ Error: {e}")
        print("Make sure SQLAlchemy is installed: pip install sqlalchemy")
    except SQLAlchemyError as e:
        print(f"❌ Database error: {e}")
        print("\nTroubleshooting steps:")
        print("1. Verify your DATABASE_URL in the .env file is correct")
        print("2. Check if the database server is running")
        print("3. Verify your database credentials")
        print("4. Make sure the database exists and is accessible")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    test_database_connection()
