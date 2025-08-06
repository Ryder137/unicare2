import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Supabase Configuration
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

# Initialize Supabase client
def init_supabase():
    if not all([SUPABASE_URL, SUPABASE_KEY]):
        raise ValueError("Missing Supabase credentials. Please check your .env file.")
    
    from supabase import create_client, Client
    return create_client(SUPABASE_URL, SUPABASE_KEY)
