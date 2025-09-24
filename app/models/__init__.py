"""
Package containing all the application models.
"""
# Import models using absolute imports
from app.models.user import User  # noqa
from app.models.admin_user import AdminUser  # noqa
from app.models.client import Client  # noqa
from app.models.appointment import Appointment  # noqa
from app.models.guidance_counselor import GuidanceCounselor  # noqa
from app.models.psychologist import Psychologist  # noqa

# Import db from extensions
from app.extensions import db  # noqa

# For backward compatibility
__all__ = [
    'User',
    'AdminUser',
    'Client',
    'Appointment',
    'GuidanceCounselor',
    'Psychologist',
    'db'
]
