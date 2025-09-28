class AccountsModel():
  def __init__(self, id: str,
               first_name: str, 
               middle_name: str, 
               last_name: str, 
               email: str,
               role: str = 'client',
               password: str = None,
               is_deleted: bool = False,
               is_active: bool = True,
               is_verified: bool = False):
    self.id = id
    self.first_name = first_name
    self.middle_name = middle_name
    self.last_name = last_name
    self.email = email
    self.role = role
    self.password = password
    self.is_deleted = is_deleted
    self.is_active = is_active
    self.is_verified = is_verified
    
    
    
    