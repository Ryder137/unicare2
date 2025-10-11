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
               is_verified: bool = False,
               image: str = None):
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
    self.image = image

class AccountsModelDto():
  def __init__(self, id: str,
               user_id: str,
               first_name: str, 
               middle_name: str, 
               last_name: str, 
               email: str,
               role: str = 'client',
               password: str = None,
               is_deleted: bool = False,
               is_active: bool = True,
               is_verified: bool = False,
               image: str = None,
               created_at: str = None,
               failed_attempt: int = 0,
               last_login_at: str = None,
               is_authenticated: bool = False,
               username: str = None):
    self.id = id
    self.user_id = user_id
    self.first_name = first_name
    self.middle_name = middle_name
    self.last_name = last_name
    self.email = email
    self.role = role
    self.password = password
    self.is_deleted = is_deleted
    self.is_active = is_active
    self.is_verified = is_verified
    self.created_at = created_at
    self.image = image
    self.failed_attempt = failed_attempt
    self.last_login_at = last_login_at
    self.is_authenticated = is_authenticated
    self.username = username

class PsychologistDetailModel(): 
    def __init__(self, id: str,
                 user_id: str,
                 license_number: str,
                 specialization: str,
                 bio: str,
                 years_of_experience: int,
                 education: str,
                 languages_spoken: list,
                 consultation_fee: float,
                 is_available: bool,
                 created_at: str,
                 updated_at: str):
        self.id = id
        self.user_id = user_id
        self.license_number = license_number
        self.specialization = specialization
        self.bio = bio
        self.years_of_experience = years_of_experience
        self.education = education
        self.languages_spoken = languages_spoken
        self.consultation_fee = consultation_fee
        self.is_available = is_available
        self.created_at = created_at
        self.updated_at = updated_at

