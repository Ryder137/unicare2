import os
from dotenv import load_dotenv
from supabase import create_client, Client
# Load environment variables from .env file
load_dotenv()

# Supabase Configuration
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')
SUPABASE_SERVICE_ROLE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

# Initialize Supabase client
def init_supabase(service_role=False) -> Client:
    if not all([SUPABASE_URL, SUPABASE_KEY,SUPABASE_SERVICE_ROLE_KEY]):
        raise ValueError("Missing Supabase credentials. Please check your .env file.")
    
    key = SUPABASE_SERVICE_ROLE_KEY if service_role else SUPABASE_KEY

    print(f"[Supabase] Initializing client. Service Role: {service_role} key:{key}")
    
    return create_client(SUPABASE_URL, key)

