"""
Context processors for the application.
"""
from flask import current_app, session
from flask_login import current_user
from datetime import datetime

def inject_now():
    """Inject current datetime into all templates as 'now'."""
    return {'now': datetime.utcnow()}

def inject_user():
    """Inject current user into all templates as 'current_user'."""
    return {'current_user': current_user}

def inject_config():
    """Inject selected config values into all templates."""
    return {
        'app_name': current_app.config.get('APP_NAME', 'UNICARE'),
        'debug': current_app.debug
    }

def init_app(app):
    """Register context processors with the Flask app."""
    app.context_processor(inject_now)
    app.context_processor(inject_user)
    app.context_processor(inject_config)
