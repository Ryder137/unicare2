import os
from sqlalchemy import create_engine, inspect
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_database_connection():
    # Get database URL from environment variables
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("❌ Error: DATABASE_URL not found in environment variables")
        return False
    
    print(f"🔗 Database URL: {database_url}")
    
    try:
        # Create engine
        engine = create_engine(database_url)
        
        # Test connection
        with engine.connect() as conn:
            print("✅ Successfully connected to the database")
            
            # Get database version
            db_version = conn.execute("SELECT version()").scalar()
            print(f"📊 Database version: {db_version}")
            
            # List all schemas
            inspector = inspect(engine)
            schemas = inspector.get_schema_names()
            print("\n📂 Available schemas:")
            for schema in schemas:
                print(f"  - {schema}")
                
            # List all tables in public schema
            print("\n📋 Tables in 'public' schema:")
            tables = inspector.get_table_names(schema='public')
            for table in tables:
                print(f"  - {table}")
                # List columns for each table
                columns = inspector.get_columns(table, schema='public')
                print(f"    Columns: {', '.join([col['name'] for col in columns])}")
            
            return True
            
    except Exception as e:
        print(f"❌ Error connecting to database: {str(e)}")
        print("\nTroubleshooting steps:")
        print("1. Check if the database server is running")
        print("2. Verify DATABASE_URL is correct in your .env file")
        print("3. Check if the database name, username, and password are correct")
        print("4. Ensure the database user has proper permissions")
        print("5. Check if your IP is whitelisted if using a cloud database")
        return False

if __name__ == "__main__":
    test_database_connection()
