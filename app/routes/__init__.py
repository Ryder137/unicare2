"""
Package containing all the application routes.
"""

# Import blueprints from their respective modules
from .auth import bp as auth_bp
from .admin import bp as admin_bp
from .main import bp as main_bp

# Import other blueprints if they exist
try:
    from .games import bp as games_bp
except ImportError:
    games_bp = None

try:
    from .assessments import bp as assessments_bp
except ImportError:
    assessments_bp = None
