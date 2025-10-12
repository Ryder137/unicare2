from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from services.audit_trail_reposervice import audit_trail_service
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify 
from flask_login import current_user, login_required 
audit_bp = Blueprint('audit', __name__, template_folder='../templates/audit')

@audit_bp.route('/audit-trail')
@login_required
def audit_trail():
    """View all audit trails (admin only)"""
    if not getattr(current_user, 'role') == 'admin':
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('admin.dashboard'))
    
    return render_template('audit/audit_trail.html')

@audit_bp.route('/audit-trail/data')
@login_required
def audit_trail_data():
    """Get audit trail data via AJAX with pagination"""
    print(f"[DEBUG] audit_trail_data route accessed")
    
    if not getattr(current_user, 'role') == 'admin':
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        # Get pagination parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 25, type=int)  # Default 25 items per page
        
        # Calculate offset
        offset = (page - 1) * per_page
        
        print(f"[DEBUG] Pagination - Page: {page}, Per page: {per_page}, Offset: {offset}")
        
        # Get audit trails with pagination
        audit_trails = audit_trail_service.get_all_audit_trails(limit=per_page, offset=offset)
        
        # Get total count for pagination info
        total_count = audit_trail_service.get_audit_trails_count()
        total_pages = (total_count + per_page - 1) // per_page  # Ceiling division
        
        print(f"[DEBUG] Retrieved {len(audit_trails)} audit trails, Total: {total_count}, Pages: {total_pages}")
        
        return jsonify({
            'audit_trails': audit_trails,
            'pagination': {
                'current_page': page,
                'per_page': per_page,
                'total_items': total_count,
                'total_pages': total_pages,
                'has_prev': page > 1,
                'has_next': page < total_pages,
                'prev_page': page - 1 if page > 1 else None,
                'next_page': page + 1 if page < total_pages else None
            }
        })
        
    except Exception as e:
        print(f"[ERROR] Error in audit_trail_data: {str(e)}")
        return jsonify({'error': str(e)}), 500

@audit_bp.route('/audit-trail/user/<user_id>')
@login_required
def user_audit_trail(user_id):
    """View audit trail for specific user"""
    if not getattr(current_user, 'role') == 'admin':
        return jsonify({'error': 'Access denied'}), 403
    
    audit_trails = audit_trail_service.get_user_audit_trail(user_id)
    
    return render_template('audit/user_audit_trail.html', 
                         audit_trails=audit_trails, 
                         user_id=user_id)