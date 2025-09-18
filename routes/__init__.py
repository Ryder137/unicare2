from .admin_routes import admin_bp
from .auth_routes import auth_bp
from .appointment_routes import appointment_bp
from .guidance_routes import guidance_bp
from .psychologist_routes import psychologist_bp

__all__ = ['admin_bp', 'auth_bp', 'appointment_bp', 'guidance_bp', 'psychologist_bp']
