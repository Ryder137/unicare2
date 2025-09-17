"""
Admin routes for the application.
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from bson import ObjectId
from datetime import datetime

from ..models.user import User
from ..forms import CreateAdminForm
from ..extensions import mongo

bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    """Decorator to require admin access."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

@bp.route('/')
@login_required
@admin_required
def dashboard():
    """Render the admin dashboard."""
    # Get user statistics
    total_users = mongo.db.users.count_documents({})
    active_users = mongo.db.users.count_documents({'is_active': True})
    total_admins = mongo.db.users.count_documents({'is_admin': True})
    
    # Get recent users
    recent_users = list(mongo.db.users.find(
        {},
        {'password': 0, 'last_login': 0}
    ).sort('created_at', -1).limit(5))
    
    return render_template(
        'admin/dashboard.html',
        total_users=total_users,
        active_users=active_users,
        total_admins=total_admins,
        recent_users=recent_users
    )

@bp.route('/users')
@login_required
@admin_required
def manage_users():
    """Render the user management page."""
    # Get all users (excluding passwords)
    users = list(mongo.db.users.find(
        {},
        {'password': 0}
    ).sort('created_at', -1))
    
    return render_template('admin/users_clean.html', users=users)

@bp.route('/users/<user_id>')
@login_required
@admin_required
def view_user(user_id):
    """View a user's details."""
    try:
        user = mongo.db.users.find_one(
            {'_id': ObjectId(user_id)},
            {'password': 0}
        )
        
        if not user:
            flash('User not found', 'danger')
            return redirect(url_for('admin.manage_users'))
        
        return render_template('admin/view_user.html', user=user)
    except:
        flash('Invalid user ID', 'danger')
        return redirect(url_for('admin.manage_users'))

@bp.route('/users/<user_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(user_id):
    """Edit a user's details."""
    try:
        user = mongo.db.users.find_one({'_id': ObjectId(user_id)})
        
        if not user:
            flash('User not found', 'danger')
            return redirect(url_for('admin.manage_users'))
        
        if request.method == 'POST':
            # Update user details
            update_data = {
                'first_name': request.form.get('first_name', user.get('first_name', '')),
                'last_name': request.form.get('last_name', user.get('last_name', '')),
                'email': request.form.get('email', user.get('email')),
                'is_admin': 'is_admin' in request.form,
                'is_active': 'is_active' in request.form,
                'updated_at': datetime.utcnow()
            }
            
            # Update password if provided
            new_password = request.form.get('new_password')
            if new_password:
                from werkzeug.security import generate_password_hash
                update_data['password'] = generate_password_hash(new_password)
            
            mongo.db.users.update_one(
                {'_id': ObjectId(user_id)},
                {'$set': update_data}
            )
            
            flash('User updated successfully', 'success')
            return redirect(url_for('admin.view_user', user_id=user_id))
        
        return render_template('admin/edit_user.html', user=user)
    except Exception as e:
        flash(f'Error updating user: {str(e)}', 'danger')
        return redirect(url_for('admin.manage_users'))

@bp.route('/users/<user_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    """Delete a user."""
    try:
        # Prevent deleting yourself
        if str(current_user.id) == user_id:
            flash('You cannot delete your own account', 'danger')
            return redirect(url_for('admin.manage_users'))
        
        result = mongo.db.users.delete_one({'_id': ObjectId(user_id)})
        
        if result.deleted_count > 0:
            flash('User deleted successfully', 'success')
        else:
            flash('User not found', 'danger')
    except:
        flash('Error deleting user', 'danger')
    
    return redirect(url_for('admin.manage_users'))

@bp.route('/users/create-admin', methods=['GET', 'POST'])
@login_required
@admin_required
def create_admin():
    """Create a new admin user."""
    form = CreateAdminForm()
    
    if form.validate_on_submit():
        # Check if user already exists
        existing_user = mongo.db.users.find_one({'email': form.email.data.lower()})
        
        if existing_user:
            flash('A user with this email already exists', 'danger')
            return redirect(url_for('admin.create_admin'))
        
        # Create new admin user
        from werkzeug.security import generate_password_hash
        
        user_data = {
            'email': form.email.data.lower(),
            'password': generate_password_hash(form.password.data),
            'first_name': form.first_name.data,
            'last_name': form.last_name.data,
            'is_admin': True,
            'is_active': True,
            'created_at': datetime.utcnow(),
            'last_login': None
        }
        
        mongo.db.users.insert_one(user_data)
        
        flash('Admin user created successfully', 'success')
        return redirect(url_for('admin.manage_users'))
    
    return render_template('admin/create_admin.html', form=form)

@bp.route('/api/users')
@login_required
@admin_required
def api_users():
    """API endpoint to get all users (for DataTables)."""
    # Get request parameters
    draw = request.args.get('draw', type=int)
    start = request.args.get('start', type=int)
    length = request.args.get('length', type=int)
    search = request.args.get('search[value]', '')
    
    # Build query
    query = {}
    if search:
        query = {
            '$or': [
                {'email': {'$regex': search, '$options': 'i'}},
                {'first_name': {'$regex': search, '$options': 'i'}},
                {'last_name': {'$regex': search, '$options': 'i'}}
            ]
        }
    
    # Get total records
    total_records = mongo.db.users.count_documents({})
    
    # Get filtered records
    filtered_records = mongo.db.users.count_documents(query)
    
    # Get paginated data
    users = list(mongo.db.users.find(
        query,
        {'password': 0}
    ).sort('created_at', -1).skip(start).limit(length))
    
    # Format data for DataTables
    data = []
    for user in users:
        data.append({
            'id': str(user['_id']),
            'email': user.get('email', ''),
            'name': f"{user.get('first_name', '')} {user.get('last_name', '')}".strip(),
            'is_admin': 'Yes' if user.get('is_admin') else 'No',
            'is_active': 'Yes' if user.get('is_active') else 'No',
            'created_at': user.get('created_at', '').strftime('%Y-%m-%d %H:%M:%S'),
            'actions': f"""
                <a href="{url_for('admin.view_user', user_id=str(user['_id']))}" class="btn btn-sm btn-info">
                    <i class="fas fa-eye"></i> View
                </a>
                <a href="{url_for('admin.edit_user', user_id=str(user['_id']))}" class="btn btn-sm btn-primary">
                    <i class="fas fa-edit"></i> Edit
                </a>
                <button class="btn btn-sm btn-danger delete-user" data-user-id="{str(user['_id'])}">
                    <i class="fas fa-trash"></i> Delete
                </button>
            """
        })
    
    return jsonify({
        'draw': draw,
        'recordsTotal': total_records,
        'recordsFiltered': filtered_records,
        'data': data
    })
