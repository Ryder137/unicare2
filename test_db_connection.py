import os
from dotenv import load_dotenv
from supabase import create_client

# Load environment variables
load_dotenv()

# Get Supabase credentials
supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_KEY')

if not all([supabase_url, supabase_key]):
    print("Error: Missing Supabase credentials in .env file")
    print("Please make sure you have the following in your .env file:")
    print("SUPABASE_URL=your_supabase_project_url")
    print("SUPABASE_KEY=your_supabase_anon_key")
else:
    try:
        print(f"Connecting to Supabase at {supabase_url}...")
        supabase = create_client(supabase_url, supabase_key)
        
        # Test connection by making a simple query
        response = supabase.table('users').select("*").limit(1).execute()
        
        if hasattr(response, 'data'):
            print("✅ Successfully connected to Supabase!")
            print(f"Found {len(response.data)} users in the database.")
        else:
            print("⚠️ Connected to Supabase but couldn't fetch data.")
            print("Response:", response)
            
    except Exception as e:
        print("❌ Error connecting to Supabase:")
        print(str(e))
