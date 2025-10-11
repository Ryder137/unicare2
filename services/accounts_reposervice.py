import os
from config import init_supabase
from supabase import Client
from models.accounts import AccountsModel
from datetime import datetime, timezone
import time
class AccountRepoService:
  def __init__(self):
    try:
      self.supabase: Client = init_supabase(False)
      self.supabase_role: Client = init_supabase(True)
      print("[Supabase] Connection initialized in DatabaseService")
    except Exception as e:
      print(f"[Supabase] ❌ Failed to initialize in DatabaseService: {str(e)}")
      self.supabase = None
      self.supabase_role = None
  
  def create_account(self, account: AccountsModel): 
    print(f"[DEBUG] Creating user with email: {account.email}")
    
    if not self.supabase_role:
        print("[ERROR] Failed to initialize service role client")
        return None
    
    response = self.supabase_role.auth.admin.create_user({
      "email": account.email,
      "password": account.password,
      "email_confirm": False
    })
        
    print(f"[DEBUG] Supabase Auth Create Response: {response}")
    
    if response.user:
        user_id = response.user.id
        accounts_data = {
            "user_id": user_id,
            "first_name": account.first_name,
            "middle_name": account.middle_name,
            "last_name": account.last_name,
            "email": account.email,
            "role": account.role,
            "is_deleted": False,
            "is_active": True,
            "is_verified": False,
            "image": account.image
        }
        
        print(f"[DEBUG] Inserting Account Data: {accounts_data}")
        print(f"[DEBUG] Inserting Account Image URL: {accounts_data['image']}")
      
        result = self.supabase.table('user_accounts').insert(accounts_data).execute()
        
        # Send verification email via Supabase
        time.sleep(2)  # Wait for 2 seconds to ensure user creation is fully processed
        from services.auth_service import auth_service
        response = auth_service.send_verification_email(account.email)
        print(f"[DEBUG] Supabase email verification response: {response}")
        
        return user_id
    else:
        print(f"[ERROR] User creation failed: {response}")
        return None
      
            
  
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
  
  def update_auth_password(self, user_id: str, new_password: str):
    response = self.supabase.auth.admin.update_user_by_id(
        user_id,
        {
            "password": new_password
        }
    )
    return response

  def update_account(self, id: str, account):
    return (self.supabase.table('user_accounts')
                .update(account)
                .eq('user_id', id)
                .execute())
    
  def update_psychologist_detail(self, user_id: str, details):
    return (self.supabase.table('psychologists')
                .update(details)
                .eq('user_id', user_id)
                .execute())

  def delete_account(self, id: str):
    return (self.supabase.table('user_accounts')
                .update({'is_deleted': True})
                .eq('user_id', id)
                .execute())
  
  def get_all_accounts(self):
    result = (self.supabase
                .table('user_accounts')
                .select("*")
                .eq('is_deleted', False)
                .execute())
    return result
  
  def get_account_by_user_id(self, user_id: str):
    return (self.supabase.table('user_accounts')
                .select('*')
                .eq('user_id', user_id)
                .execute())

  def get_account_by_role(self, role: str):
    return (self.supabase.table('user_accounts')
                .select("*")
                .eq('role', role)
                .execute())

  def get_account_by_email(self, email: str):
    return (self.supabase.table('user_accounts')
                .select('*')
                .eq('email', email.lower().strip())
                .execute())

  def update_attempts(self, email: str, role: str, attempts: int):
    return (self.supabase.table('user_accounts')
                .update({'failed_attempt': attempts})
                .eq('email', email)
                .eq('role', role)
                .execute()
    )
  
  def reset_attempts(self, email: str, role: str):
    now = datetime.now(timezone.utc).isoformat()
    results = (self.supabase.table('user_accounts')
                .update({'failed_attempt': 0,
                         'last_login_at': now})
                .eq('email', email)
                .eq('role', role)
                .execute()
    )
    return results
    
  def get_psychologist_details(self, user_id: str):
    return (self.supabase.from_('psychologists')
                .select('*')
                .eq('user_id', user_id)
                .execute()
    )  

# Singleton instance
account_repo_service = AccountRepoService()