import os
from config import init_supabase
from supabase import Client
from models.accounts import AccountsModel
from datetime import datetime, timezone

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
    
    result = self.supabase.table('user_accounts').insert(accounts_data).execute()
    inserted_id = result.data[0]['id'] if result.data else None
    return inserted_id
  
  def create_psychologist_detail(self, psychologist_detail):
    psychologist_data = {
      "user_id": psychologist_detail.user_id,
      "license_number": psychologist_detail.license_number,
      "specialization": psychologist_detail.specialization,
      "bio": psychologist_detail.bio,
      "years_of_experience": psychologist_detail.years_of_experience,
      "education": psychologist_detail.education,
      "languages_spoken": psychologist_detail.languages_spoken,
      "consultation_fee": psychologist_detail.consultation_fee,
      "is_available": psychologist_detail.is_available,
      "created_at": psychologist_detail.created_at,
      "updated_at": psychologist_detail.updated_at
    }
    return self.supabase.table('psychologists').insert(psychologist_data).execute()

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
    return self.supabase.table('user_accounts').update(accounts_data).eq('id', id).execute()
  
  def delete_account(self, id: str):
    return (self.supabase.table('user_accounts')
                .update({'is_deleted': True})
                .eq('id', id)
                .execute()
    )
  
  def get_all_accounts(self):
    result = (self.supabase
                .table('user_accounts')
                .select("*")
                .eq('is_deleted', False)
                .execute())
    return result
  
  def get_account_by_id(self, id: str):
    return self.supabase.table('user_accounts').select('*').eq('id', id).execute()
  
  def get_account_by_role(self, role: str):
    return self.supabase.table('user_accounts').select("*").eq('role', role).execute()
  
  def get_account_by_email(self, email: str):
    return self.supabase.table('user_accounts').select('*').eq('email', email.lower().strip()).execute()
  
  def update_attempts(self, email: str, role: str, attempts: int):
    return (self.supabase.table('user_accounts')
                .update({'failed_attempt': attempts})
                .eq('email', email)
                .eq('role', role)
                .execute()
    )
  
  def reset_attempts(self, email: str, role: str):
    print(f"[DEBUG] Reset attempts update Email: {email} Role: {role}")
    now = datetime.now(timezone.utc).isoformat()
    print(f"[DEBUG] Resetting attempts at: {now}")
    results = (self.supabase.table('user_accounts')
                .update({'failed_attempt': 0,
                         'last_login_at': now})
                .eq('email', email)
                .eq('role', role)
                .execute()
    )
    
    print(f"[DEBUG] Reset attempts for {email} with role {role}: {results}")
    
    return results
    
    

# Singleton instance
account_repo_service = AccountRepoService()