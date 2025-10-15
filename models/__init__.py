"""
Package containing all the application models.
"""
from flask_sqlalchemy import SQLAlchemy

# Initialize SQLAlchemy
db = SQLAlchemy()

# Import models after db initialization to avoid circular imports
from .user import User
from .game_score import GameScore
from .personality_test import PersonalityTestResult
from .admin import Admin
from .psychologist import Psychologist
from .guidance_counselor import GuidanceCounselor
from .admin_user import AdminUser
from .client import Client
from .appointment import Appointment
from .accounts import AccountsModel,PsychologistDetailModel
from .audit_trail import AuditTrailModel
from .content import Content

# Make models available at package level
__all__ = [
    'db',
    'User',
    'GameScore',
    'PersonalityTestResult',
    'Admin',
    'Psychologist',
    'GuidanceCounselor',
    'AdminUser',
    'Client',
    'Appointment',
    'AccountsModel',
    'PsychologistDetailModel',
    'AuditTrailModel',
    'Content',
]
