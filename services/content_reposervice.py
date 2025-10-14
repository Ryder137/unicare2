import os
import logging
from datetime import datetime
from config import init_supabase

# Configure logging
logger = logging.getLogger(__name__)

class ContentRepoService:
  def __init__(self):
    
    try:
      # Use service role for admin operations like delete
      self.supabase = init_supabase(service_role=True)
      print("[Supabase] Connection initialized in ContentRepoService")
    except Exception as e:
      print(f"[Supabase] ❌ Failed to initialize in ContentRepoService: {str(e)}")
      self.supabase = None
    
  def create_content(self, content_data: dict):
    """Create a new content record."""
    try:
      # Add timestamps
      content_data['created_at'] = datetime.utcnow().isoformat()
      content_data['updated_at'] = datetime.utcnow().isoformat()
      
      result = (self.supabase.table('content_management')
                    .insert(content_data)
                    .execute())
      logger.info(f"Content created successfully: {result}")
      return result
    except Exception as e:
      logger.error(f"Error creating content: {str(e)}")
      raise e

  def update_content(self, content_id: str, update_data: dict):
    """Update an existing content record."""
    try:
      # Add updated timestamp
      update_data['updated_at'] = datetime.utcnow().isoformat()
      
      result = (self.supabase.table('content_management')
                    .update(update_data)
                    .eq('id', content_id)
                    .execute())
      logger.info(f"Content updated successfully: {content_id}")
      return result
    except Exception as e:
      logger.error(f"Error updating content {content_id}: {str(e)}")
      raise e
    
  def get_content_by_id(self, content_id: str):
    """Get a single content record by ID."""
    try:
      result = (self.supabase.table('content_management')
                    .select('*')
                    .eq('id', content_id)
                    .execute())
      logger.info(f"Content retrieved: {content_id}")
      return result
    except Exception as e:
      logger.error(f"Error retrieving content {content_id}: {str(e)}")
      raise e
    
  def delete_content(self, content_id: str):
    """Permanently delete a content record."""
    try:
      # First check if the content exists
      check_result = (self.supabase.table('content_management')
                      .select('id')
                      .eq('id', content_id)
                      .execute())
      
      if not check_result.data:
        logger.warning(f"Content with ID {content_id} not found for deletion")
        return None
      
      logger.info(f"Content found for deletion: {content_id}")
      
      # For delete operations, ensure we're using service role if needed
      try:
        # Use service role client for delete to bypass RLS
        service_client = init_supabase(service_role=True)
        result = (service_client.table('content_management')
                      .delete()
                      .eq('id', content_id)
                      .execute())
      except Exception as service_error:
        logger.warning(f"Service role delete failed, trying with regular client: {service_error}")
        # Fallback to regular client
        result = (self.supabase.table('content_management')
                      .delete()
                      .eq('id', content_id)
                      .execute())
      
      # Log the full result for debugging
      logger.info(f"Delete operation result: {result}")
      logger.info(f"Delete data: {result.data if hasattr(result, 'data') else 'No data attribute'}")
      logger.info(f"Delete count: {result.count if hasattr(result, 'count') else 'No count attribute'}")
      
      # Verify deletion was successful
      verify_result = (self.supabase.table('content_management')
                       .select('id')
                       .eq('id', content_id)
                       .execute())
      
      if verify_result.data:
        logger.error(f"Content {content_id} still exists after delete operation!")
        raise Exception(f"Failed to delete content {content_id} - record still exists")
      else:
        logger.info(f"Content successfully deleted and verified: {content_id}")
      
      return result
    except Exception as e:
      logger.error(f"Error deleting content {content_id}: {str(e)}")
      raise e
    
  def inactive_content(self, content_id: str):
    """Set content as inactive (soft delete)."""
    try:
      result = (self.supabase.table('content_management')
                    .update({
                        "is_active": False,
                        "updated_at": datetime.utcnow().isoformat()
                    })
                    .eq('id', content_id)
                    .execute())
      logger.info(f"Content set to inactive: {content_id}")
      return result
    except Exception as e:
      logger.error(f"Error setting content inactive {content_id}: {str(e)}")
      raise e
      
  def activate_content(self, content_id: str):
    """Set content as active."""
    try:
      result = (self.supabase.table('content_management')
                    .update({
                        "is_active": True,
                        "updated_at": datetime.utcnow().isoformat()
                    })
                    .eq('id', content_id)
                    .execute())
      logger.info(f"Content activated: {content_id}")
      return result
    except Exception as e:
      logger.error(f"Error activating content {content_id}: {str(e)}")
      raise e
    
  def get_all_contents(self, filters=None):
    """Get all content records with optional filtering."""
    try:
      query = self.supabase.table('content_management').select('*')
      
      # Apply filters if provided
      if filters:
        if filters.get('is_active') is not None:
          query = query.eq('is_active', filters['is_active'])
        if filters.get('category'):
          query = query.eq('category', filters['category'])
        if filters.get('content_type'):
          query = query.eq('content_type', filters['content_type'])
        if filters.get('target_audience'):
          query = query.eq('target_audience', filters['target_audience'])
      
      # Order by created_at descending
      result = query.order('created_at', desc=True).execute()
      
      # Enhanced logging for debugging
      record_count = len(result.data) if result.data else 0
      logger.info(f"Retrieved {record_count} content records")
      
      if result.data:
        # Log the IDs of all records for debugging
        record_ids = [record.get('id', 'NO_ID') for record in result.data]
        logger.info(f"Content IDs retrieved: {record_ids}")
      
      return result
    except Exception as e:
      logger.error(f"Error retrieving contents: {str(e)}")
      raise e

  def search_contents(self, search_query: str, filters=None):
    """Search content by author or messages."""
    try:
      query = self.supabase.table('content_management').select('*')
      
      # Apply search to author and messages
      if search_query:
        query = query.or_(f'author.ilike.%{search_query}%,messages.ilike.%{search_query}%')
      
      # Apply additional filters
      if filters:
        if filters.get('is_active') is not None:
          query = query.eq('is_active', filters['is_active'])
        if filters.get('category'):
          query = query.eq('category', filters['category'])
        if filters.get('content_type'):
          query = query.eq('content_type', filters['content_type'])
      
      result = query.order('created_at', desc=True).execute()
      logger.info(f"Search returned {len(result.data) if result.data else 0} results")
      return result
    except Exception as e:
      logger.error(f"Error searching contents: {str(e)}")
      raise e

  def get_random_content(self):
    """Get a random content from the content_management table."""
    try:
      result = (self.supabase.table('content_management')
                    .select('*')
                    .eq('is_active', True)
                    .order('random()')
                    .limit(1)
                    .execute())
      logger.info("Random content retrieved")
      return result
    except Exception as e:
      logger.error(f"Error retrieving random content: {str(e)}")
      raise e
      
  def get_content_stats(self):
    """Get content statistics."""
    try:
      # Get total counts
      total_result = self.supabase.table('content_management').select('id', count='exact').execute()
      active_result = self.supabase.table('content_management').select('id', count='exact').eq('is_active', True).execute()
      inactive_result = self.supabase.table('content_management').select('id', count='exact').eq('is_active', False).execute()
      
      stats = {
        'total': total_result.count if total_result else 0,
        'active': active_result.count if active_result else 0,
        'inactive': inactive_result.count if inactive_result else 0
      }
      
      logger.info(f"Content stats retrieved: {stats}")
      return stats
    except Exception as e:
      logger.error(f"Error retrieving content stats: {str(e)}")
      return {'total': 0, 'active': 0, 'inactive': 0}
      
#singleton instance
content_repo_service = ContentRepoService()