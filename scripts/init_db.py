from services.database_service import db_service

def create_tables():
    # This is a one-time setup script to create tables
    # Run this only once after setting up your Supabase project
    
    # Users table
    db_service.supabase.rpc('create_users_table', {}).execute()
    
    # Game scores table
    db_service.supabase.rpc('create_game_scores_table', {}).execute()
    
    # Personality tests table
    db_service.supabase.rpc('create_personality_tests_table', {}).execute()
    
    print("Database tables created successfully!")

if __name__ == "__main__":
    create_tables()
