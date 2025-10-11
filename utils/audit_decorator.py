from functools import wraps
from flask import request, session
from flask_login import current_user
from services.audit_trail_reposervice import audit_trail_service
from models.audit_trail import AuditTrailModel
import json

def audit_action(action: str, resource_type: str):
    """Decorator to automatically log user actions"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Execute the original function first
            result = func(*args, **kwargs)
            
            try:
                # Get user info
                user_id = getattr(current_user, 'user_id', None) if current_user.is_authenticated else None
                print(f"[DEBUG] AuditTrail Current user ID: {user_id}")
                if user_id:
                    # Get resource ID from kwargs or args
                    resource_id = kwargs.get('id') or kwargs.get('user_id') or (args[0] if args else None)
                    
                    # Get request details
                    ip_address = request.environ.get('HTTP_X_FORWARDED_FOR') or request.environ.get('REMOTE_ADDR')
                    user_agent = request.environ.get('HTTP_USER_AGENT')
                    session_id = session.get('session_id')
                    
                    # Get request data for details
                    details = {}
                    if request.method in ['POST', 'PUT', 'PATCH']:
                        if request.is_json:
                            details = request.get_json() or {}
                        else:
                            details = dict(request.form)
                    
                    # Create audit trail entry
                    audit_data = AuditTrailModel(
                        user_id=user_id,
                        action=action,
                        resource_type=resource_type,
                        resource_id=str(resource_id) if resource_id else None,
                        details=details,
                        ip_address=ip_address,
                        user_agent=user_agent,
                        session_id=session_id
                    )
                    
                    # Log the action
                    audit_trail_service.log_action(audit_data)
                print(f"[DEBUG] AuditTrail Current user ID: {user_id}")
            except Exception as e:
                print(f"[ERROR] Failed to log audit trail: {str(e)}")
                # Don't fail the original request if audit logging fails
                pass
            
            return result
        return wrapper
    return decorator