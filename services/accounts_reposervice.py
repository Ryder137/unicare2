import os
from config import init_supabase
from supabase import Client
from models.accounts import AccountsModel

class AccountRepoService:
  def __init__(self):
    
    try:
      self.supabase: Client = init_supabase()
      print("[Supabase] Connection initialized in DatabaseService")
    except Exception as e:
      print(f"[Supabase] ❌ Failed to initialize in DatabaseService: {str(e)}")
      self.supabase = None
  
  def create_account(self, account: AccountsModel):
    accounts_data = {
      "first_name": account.first_name,
      "middle_name": account.middle_name,
      "last_name": account.last_name,
      "email": account.email,
      "role": account.role,
      "password": account.password,
      "is_deleted": False,
      "is_active": True,
      "is_verified": False
    }
    return self.supabase.table('accounts').insert(accounts_data).execute()
  
  def update_account(self, id: str, account: AccountsModel):
    accounts_data = {
      "first_name": account.first_name,
      "middle_name": account.middle_name,
      "last_name": account.last_name,
      "email": account.email,
      "role": account.role,
      "password": account.password,
      "is_deleted": account.is_deleted,
      "is_active": account.is_active,
      "is_verified": account.is_verified
    }
    return self.supabase.table('accounts').update(accounts_data).eq('id', id).execute()
  
  def delete_account(self, id: str):
    return self.supabase.table('accounts').update({'is_deleted': True}).eq('id', id).execute()
  
  def get_all_accounts(self):
    return self.supabase.table('accounts').select("*").eq('is_deleted',False).execute()
  
  def get_account_by_id(self, id: str):
    return self.supabase.table('accounts').select('*').eq('id', id).execute()
  
  def get_account_by_role(self, role: str):
    return self.supabase.table('accounts').select("*").eq('role', role).execute()

# Singleton instance
db_service = AccountRepoService()