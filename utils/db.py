from supabase import Client
from config import init_supabase

# Initialize Supabase client with connection check
try:
    supabase: Client = init_supabase()
    print("[Supabase] Connection initialized in utils/db.py")
except Exception as e:
    print(f"[Supabase] ❌ Failed to initialize: {str(e)}")
    supabase = None

# Fetch a single user by UUID from Supabase
def fetch_user_by_id(user_id: str):
    if not supabase:
        print("[Supabase] Not connected. Cannot fetch user.")
        return None
    try:
        response = supabase.table("users").select("*").eq("id", user_id).limit(1).execute()
        data = response.data
        return data[0] if data else None
    except Exception as e:
        print(f"Error fetching user by id: {str(e)}")
        return None

# Example function to fetch data
def fetch_all(table_name: str):
    if not supabase:
        print(f"[Supabase] Not connected. Cannot fetch data from {table_name}.")
        return []
    try:
        response = supabase.table(table_name).select("*").execute()
        return response.data
    except Exception as e:
        print(f"Error fetching data from {table_name}: {str(e)}")
        return []

# Example function to insert data
def insert_data(table_name: str, data: dict):
    if not supabase:
        print(f"[Supabase] Not connected. Cannot insert data into {table_name}.")
        return None
    try:
        response = supabase.table(table_name).insert(data).execute()
        return response.data
    except Exception as e:
        print(f"Error inserting data into {table_name}: {str(e)}")
        return None

# Example function to update data
def update_data(table_name: str, data: dict, column: str, value: str):
    if not supabase:
        print(f"[Supabase] Not connected. Cannot update data in {table_name}.")
        return None
    try:
        response = supabase.table(table_name).update(data).eq(column, value).execute()
        return response.data
    except Exception as e:
        print(f"Error updating data in {table_name}: {str(e)}")
        return None

# Example function to delete data
def delete_data(table_name: str, column: str, value: str):
    if not supabase:
        print(f"[Supabase] Not connected. Cannot delete data from {table_name}.")
        return None
    try:
        response = supabase.table(table_name).delete().eq(column, value).execute()
        return response.data
    except Exception as e:
        print(f"Error deleting data from {table_name}: {str(e)}")
        return None
