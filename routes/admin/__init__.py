from flask import Blueprint

# Create the admin blueprint
admin_bp = Blueprint('admin', __name__)

# Import routes after creating the blueprint to avoid circular imports
from . import admin_routes  # noqa
