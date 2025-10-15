import logging
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import current_user, login_required
from services.content_reposervice import content_repo_service
from forms.content_forms import ContentForm, ContentSearchForm
import uuid
from datetime import datetime

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

@content_bp.route('/management')
@login_required
def management():
  """Display the content management page."""
  logger.info(f"Content management accessed by user: {current_user.email if current_user.is_authenticated else 'Anonymous'}")
  
  if not current_user.is_authenticated or current_user.role not in ['admin','staff']:
    flash('Access denied. Admins and staff only.', 'danger')
    return redirect(url_for('main.index'))
  
  form = ContentForm()
  search_form = ContentSearchForm()
  return render_template('content_management.html', form=form, search_form=search_form)

@content_bp.route('/list')
@login_required
def list_contents():
  """Get all contents as JSON for DataTable."""
  logger.info(f"Content list requested by user: {current_user.email if current_user.is_authenticated else 'Anonymous'}")
  
  if not current_user.is_authenticated or current_user.role not in ['admin','staff']:
    return jsonify({'error': 'Access denied. Your role does not have permission to view this content.'}), 403

  try:
    # Get filter parameters from request
    status_filter = request.args.get('status')
    category_filter = request.args.get('category')
    content_type_filter = request.args.get('content_type')
    
    filters = {}
    if status_filter == 'active':
      filters['is_active'] = True
    elif status_filter == 'inactive':
      filters['is_active'] = False
    
    if category_filter:
      filters['category'] = category_filter
    if content_type_filter:
      filters['content_type'] = content_type_filter
    
    results = content_repo_service.get_all_contents(filters)
    logger.info(f"Retrieved content results: {len(results.data) if results and results.data else 0} records")
    logger.info(f"Applied filters: {filters}")  # Debug log
    
    contents = results.data if results and hasattr(results, "data") else []
    
    # Render table rows as HTML using Jinja2
    table_rows = render_template('admin/content-list/content_table_list.html', contents=contents)
    
    return jsonify({'html': table_rows})
  except Exception as e:
    logger.error(f"Error retrieving content list: {str(e)}")
    return jsonify({'error': 'Failed to retrieve content list'}), 500

@content_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_content():
  """Add new content."""
  print("Add content route accessed")
  if not current_user.is_authenticated or current_user.role not in ['admin','staff']:
    return jsonify({'error': 'Access denied'}), 403

  if request.method == 'POST':
    try:
      form_data = request.get_json() if request.is_json else request.form
      
      # Validate required fields
      if not form_data.get('author') or not form_data.get('messages'):
        return jsonify({'error': 'Author and message are required'}), 400
      
      # Prepare content data
      content_data = {
        'id': str(uuid.uuid4()),
        'author': form_data.get('author'),
        'messages': form_data.get('messages'),
        'content_type': form_data.get('content_type', 'general'),
        'is_active': form_data.get('is_active', True),
        'created_by': current_user.email,
        'updated_by': current_user.email
      }
      
      # Create content
      result = content_repo_service.create_content(content_data)
      
      if result and result.data:
        logger.info(f"Content created successfully by {current_user.email}")
        if request.is_json:
          return jsonify({'success': True, 'message': 'Content created successfully', 'data': result.data[0]})
        else:
          flash('Content created successfully!', 'success')
          return redirect(url_for('content.management'))
      else:
        logger.error("Failed to create content - no data returned")
        if request.is_json:
          return jsonify({'error': 'Failed to create content'}), 500
        else:
          flash('Failed to create content', 'error')
          return redirect(url_for('content.management'))
          
    except Exception as e:
      logger.error(f"Error creating content: {str(e)}")
      if request.is_json:
        return jsonify({'error': str(e)}), 500
      else:
        flash(f'Error creating content: {str(e)}', 'error')
        return redirect(url_for('content.management'))

  # GET request - return form
  form = ContentForm()
  return render_template('content_form.html', form=form, action='add')

@content_bp.route('/<content_id>')
@login_required
def view_content(content_id):
  """View a single content record."""
  if not current_user.is_authenticated or current_user.role not in ['admin','staff']:
    return jsonify({'error': 'Access denied'}), 403

  try:
    result = content_repo_service.get_content_by_id(content_id)
    
    if result and result.data:
      content = result.data[0]
      if request.headers.get('Content-Type') == 'application/json' or request.args.get('format') == 'json':
        return jsonify({'success': True, 'data': content})
      else:
        return render_template('content_view.html', content=content)
    else:
      if request.headers.get('Content-Type') == 'application/json':
        return jsonify({'error': 'Content not found'}), 404
      else:
        flash('Content not found', 'error')
        return redirect(url_for('content.management'))
        
  except Exception as e:
    logger.error(f"Error retrieving content {content_id}: {str(e)}")
    if request.headers.get('Content-Type') == 'application/json':
      return jsonify({'error': str(e)}), 500
    else:
      flash(f'Error retrieving content: {str(e)}', 'error')
      return redirect(url_for('content.management'))

@content_bp.route('/edit/<content_id>', methods=['GET', 'POST'])
@login_required
def edit_content(content_id):
  """Edit existing content."""
  if not current_user.is_authenticated or current_user.role not in ['admin','staff']:
    return jsonify({'error': 'Access denied'}), 403

  if request.method == 'POST':
    try:
      form_data = request.get_json() if request.is_json else request.form
      
      # Validate required fields
      if not form_data.get('author') or not form_data.get('messages'):
        return jsonify({'error': 'Author and message are required'}), 400
      
      # Prepare update data
      update_data = {
        'author': form_data.get('author'),
        'messages': form_data.get('messages'),
        'content_type': form_data.get('content_type', 'general'),
        'is_active': form_data.get('is_active', True),
        'updated_by': current_user.email
      }
      
      # Update content
      result = content_repo_service.update_content(content_id, update_data)
      
      if result and result.data:
        logger.info(f"Content {content_id} updated successfully by {current_user.email}")
        if request.is_json:
          return jsonify({'success': True, 'message': 'Content updated successfully', 'data': result.data[0]})
        else:
          flash('Content updated successfully!', 'success')
          return redirect(url_for('content.management'))
      else:
        if request.is_json:
          return jsonify({'error': 'Failed to update content'}), 500
        else:
          flash('Failed to update content', 'error')
          return redirect(url_for('content.management'))
          
    except Exception as e:
      logger.error(f"Error updating content {content_id}: {str(e)}")
      if request.is_json:
        return jsonify({'error': str(e)}), 500
      else:
        flash(f'Error updating content: {str(e)}', 'error')
        return redirect(url_for('content.management'))

  # GET request - return form with current data
  try:
    result = content_repo_service.get_content_by_id(content_id)
    if result and result.data:
      content = result.data[0]
      form = ContentForm(data=content)
      return render_template('content_form.html', form=form, content=content, action='edit')
    else:
      flash('Content not found', 'error')
      return redirect(url_for('content.management'))
  except Exception as e:
    logger.error(f"Error retrieving content for edit {content_id}: {str(e)}")
    flash(f'Error retrieving content: {str(e)}', 'error')
    return redirect(url_for('content.management'))

@content_bp.route('/delete/<content_id>', methods=['POST', 'DELETE'])
@login_required
def delete_content(content_id):
  """Delete content permanently."""
  if not current_user.is_authenticated or current_user.role not in ['admin','staff']:
    return jsonify({'error': 'Access denied'}), 403

  try:
    result = content_repo_service.delete_content(content_id)
    
    if result:
      logger.info(f"Content {content_id} deleted by {current_user.email}")
      if request.is_json or request.method == 'DELETE':
        return jsonify({'success': True, 'message': 'Content deleted successfully'})
      else:
        flash('Content deleted successfully!', 'success')
        return redirect(url_for('content.management'))
    else:
      if request.is_json or request.method == 'DELETE':
        return jsonify({'error': 'Failed to delete content'}), 500
      else:
        flash('Failed to delete content', 'error')
        return redirect(url_for('content.management'))
        
  except Exception as e:
    logger.error(f"Error deleting content {content_id}: {str(e)}")
    if request.is_json or request.method == 'DELETE':
      return jsonify({'error': str(e)}), 500
    else:
      flash(f'Error deleting content: {str(e)}', 'error')
      return redirect(url_for('content.management'))

@content_bp.route('/toggle-status/<content_id>', methods=['POST'])
@login_required
def toggle_status(content_id):
  """Toggle content active/inactive status."""
  if not current_user.is_authenticated or current_user.role not in ['admin','staff']:
    return jsonify({'error': 'Access denied'}), 403

  try:
    # Get current status
    result = content_repo_service.get_content_by_id(content_id)
    if not result or not result.data:
      return jsonify({'error': 'Content not found'}), 404
    
    current_status = result.data[0].get('is_active', True)
    new_status = not current_status
    
    # Update status
    if new_status:
      update_result = content_repo_service.activate_content(content_id)
    else:
      update_result = content_repo_service.inactive_content(content_id)
    
    if update_result:
      logger.info(f"Content {content_id} status changed to {'active' if new_status else 'inactive'} by {current_user.email}")
      return jsonify({
        'success': True, 
        'message': f'Content {"activated" if new_status else "deactivated"} successfully',
        'new_status': new_status
      })
    else:
      return jsonify({'error': 'Failed to update content status'}), 500
      
  except Exception as e:
    logger.error(f"Error toggling content status {content_id}: {str(e)}")
    return jsonify({'error': str(e)}), 500

@content_bp.route('/search')
@login_required
def search_content():
  """Search content based on query and filters."""
  if not current_user.is_authenticated or current_user.role not in ['admin','staff']:
    return jsonify({'error': 'Access denied'}), 403

  try:
    search_query = request.args.get('q', '')
    filters = {
      'category': request.args.get('category'),
      'content_type': request.args.get('content_type')
    }
    
    # Remove None values
    filters = {k: v for k, v in filters.items() if v}
    
    if search_query:
      result = content_repo_service.search_contents(search_query, filters)
    else:
      result = content_repo_service.get_all_contents(filters)
    
    contents = result.data if result and result.data else []
    
    # Render table rows as HTML
    table_rows = render_template('content_table_list.html', contents=contents)
    
    return jsonify({'html': table_rows, 'count': len(contents)})
    
  except Exception as e:
    logger.error(f"Error searching content: {str(e)}")
    return jsonify({'error': str(e)}), 500

@content_bp.route('/bulk-activate', methods=['POST'])
@login_required
def bulk_activate():
  """Bulk activate content items."""
  if not current_user.is_authenticated or current_user.role not in ['admin','staff']:
    return jsonify({'error': 'Access denied'}), 403

  try:
    data = request.get_json()
    content_ids = data.get('content_ids', [])
    
    if not content_ids:
      return jsonify({'error': 'No content IDs provided'}), 400
    
    success_count = 0
    failed_count = 0
    
    for content_id in content_ids:
      try:
        result = content_repo_service.activate_content(content_id)
        if result:
          success_count += 1
        else:
          failed_count += 1
      except Exception as e:
        logger.error(f"Error activating content {content_id}: {str(e)}")
        failed_count += 1
    
    message = f"Successfully activated {success_count} items"
    if failed_count > 0:
      message += f", {failed_count} failed"
    
    logger.info(f"Bulk activation completed by {current_user.email}: {success_count} success, {failed_count} failed")
    return jsonify({'success': True, 'message': message, 'success_count': success_count, 'failed_count': failed_count})
    
  except Exception as e:
    logger.error(f"Error in bulk activation: {str(e)}")
    return jsonify({'error': str(e)}), 500

@content_bp.route('/bulk-deactivate', methods=['POST'])
@login_required
def bulk_deactivate():
  """Bulk deactivate content items."""
  if not current_user.is_authenticated or current_user.role not in ['admin','staff']:
    return jsonify({'error': 'Access denied'}), 403

  try:
    data = request.get_json()
    content_ids = data.get('content_ids', [])
    
    if not content_ids:
      return jsonify({'error': 'No content IDs provided'}), 400
    
    success_count = 0
    failed_count = 0
    
    for content_id in content_ids:
      try:
        result = content_repo_service.inactive_content(content_id)
        if result:
          success_count += 1
        else:
          failed_count += 1
      except Exception as e:
        logger.error(f"Error deactivating content {content_id}: {str(e)}")
        failed_count += 1
    
    message = f"Successfully deactivated {success_count} items"
    if failed_count > 0:
      message += f", {failed_count} failed"
    
    logger.info(f"Bulk deactivation completed by {current_user.email}: {success_count} success, {failed_count} failed")
    return jsonify({'success': True, 'message': message, 'success_count': success_count, 'failed_count': failed_count})
    
  except Exception as e:
    logger.error(f"Error in bulk deactivation: {str(e)}")
    return jsonify({'error': str(e)}), 500

@content_bp.route('/bulk-delete', methods=['DELETE'])
@login_required
def bulk_delete():
  """Bulk delete content items."""
  if not current_user.is_authenticated or current_user.role not in ['admin','staff']:
    return jsonify({'error': 'Access denied'}), 403

  try:
    data = request.get_json()
    content_ids = data.get('content_ids', [])
    
    if not content_ids:
      return jsonify({'error': 'No content IDs provided'}), 400
    
    success_count = 0
    failed_count = 0
    
    for content_id in content_ids:
      try:
        result = content_repo_service.delete_content(content_id)
        if result:
          success_count += 1
        else:
          failed_count += 1
      except Exception as e:
        logger.error(f"Error deleting content {content_id}: {str(e)}")
        failed_count += 1
    
    message = f"Successfully deleted {success_count} items"
    if failed_count > 0:
      message += f", {failed_count} failed"
    
    logger.info(f"Bulk deletion completed by {current_user.email}: {success_count} success, {failed_count} failed")
    return jsonify({'success': True, 'message': message, 'success_count': success_count, 'failed_count': failed_count})
    
  except Exception as e:
    logger.error(f"Error in bulk deletion: {str(e)}")
    return jsonify({'error': str(e)}), 500
