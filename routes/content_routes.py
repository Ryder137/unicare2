import logging
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import current_user, login_required
from services.content_reposervice import content_repo_service


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create a Blueprint for content routes
content_bp = Blueprint(
  'content', 
  __name__, 
  template_folder='../templates/admin/content-list',
  url_prefix='/content'
)

@content_bp.route('management')
@login_required
def management():
  print(f"[DEBUG] content_management. is_authenticated: {current_user.is_authenticated}")
  if not current_user.is_authenticated or current_user.role not in ['admin','staff']:
    flash('Access denied. Admins only.', 'danger')
    return redirect(url_for('main.index'))
  return render_template('content_management.html')

@content_bp.route('/list')
@login_required
def list_contents():
  
  print(f"[DEBUG] AJAX request received for content list. is_authenticated: {current_user.is_authenticated}")
  
  if not current_user.is_authenticated or current_user.role not in ['admin','staff']:
    return jsonify({'error': 'Access denied. Your role does not have permission to view this content.'}), 403

  results = content_repo_service.get_all_contents()
  print(f"[DEBUG] Retrieved contents results: {results}")
  
  contents = results.data if results and hasattr(results, "data") else []
  print(f"[DEBUG] Processed contents data: {contents}")

  # Render table rows as HTML using Jinja2
  table_rows = render_template('content_table_list.html', contents=contents)
  
  return jsonify({'html': table_rows})