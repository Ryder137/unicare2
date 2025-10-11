import os
from config import init_supabase

class ContentRepoService:
  def __init__(self):
    
    try:
      self.supabase = init_supabase()
      print("[Supabase] Connection initialized in ContentRepoService")
    except Exception as e:
      print(f"[Supabase] ❌ Failed to initialize in ContentRepoService: {str(e)}")
      self.supabase = None
    
  def create_content(self, content_data: dict):
    return (self.supabase.table('content_management')
                .insert(content_data)
                .execute())

  def update_content(self, content_id: str, update_data: dict):
    return (self.supabase.table('content_management')
                .update(update_data)
                .eq('id', content_id)
                .execute())
    
  def inactive_content(self, content_id: str):
    return (self.supabase.table('content_management')
                .update({"is_active": False})
                .eq('id', content_id)
                .execute())
    
  def get_all_contents(self):
    return (self.supabase.table('content_management')
                .select('*')
                .execute())

  #get a random content from the content_management table
  def get_random_content(self):
    return (self.supabase.table('content_management')
                .select('*')
                .eq('is_active', True)
                .order('random()')
                .limit(1)
                .execute())
      
#singleton instance
content_repo_service = ContentRepoService()