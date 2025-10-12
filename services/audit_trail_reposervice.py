from config import init_supabase
from models.audit_trail import AuditTrailModel
from datetime import datetime, timezone
import json

class AuditTrailService:
    def __init__(self):
        try:
            self.supabase = init_supabase()
            print("[DEBUG] AuditTrailService initialized successfully")
        except Exception as e:
            print(f"[ERROR] Failed to initialize AuditTrailService: {str(e)}")
            self.supabase = None
    
    def log_action(self, audit_data: AuditTrailModel):
        """Log an action to the audit trail"""
        try:
            print(f"[DEBUG-REPOSERVICE] Logging audit action: {audit_data.action} by user {audit_data.user_id}")
            if not self.supabase:
                print("[ERROR] Supabase client not initialized")
                return False
            
            # Convert audit data to dictionary
            audit_dict = {
                'user_id': audit_data.user_id,
                'action': audit_data.action,
                'resource_type': audit_data.resource_type,
                'resource_id': audit_data.resource_id,
                'details': json.dumps(audit_data.details) if audit_data.details else None,
                'ip_address': audit_data.ip_address,
                'user_agent': audit_data.user_agent,
                'timestamp': audit_data.timestamp.isoformat(),
                'session_id': audit_data.session_id,
                'email_name': audit_data.username
            }
            
            print(f"[DEBUG-REPOSERVICE] Audit data to insert: {audit_dict}")
            
            # Insert into audit_trail table
            result = self.supabase.table('audit_trail').insert(audit_dict).execute()
            
            print(f"[DEBUG-REPOSERVICE] Supabase insert result: {result}")
            
            if result.data:
                print(f"[DEBUG] Audit trail logged: {audit_data.action} by {audit_data.user_id}")
                return True
            else:
                print(f"[ERROR] Failed to log audit trail")
                return False
                
        except Exception as e:
            print(f"[ERROR] Error logging audit trail: {str(e)}")
            return False
    
    def get_user_audit_trail(self, user_id: str, limit: int = 50):
        """Get audit trail for a specific user"""
        try:
            result = (self.supabase.table('audit_trail')
                     .select('*')
                     .eq('user_id', user_id)
                     .order('timestamp', desc=True)
                     .limit(limit)
                     .execute())
            
            return result.data if result.data else []
            
        except Exception as e:
            print(f"[ERROR] Error getting user audit trail: {str(e)}")
            return []
    
    def get_resource_audit_trail(self, resource_type: str, resource_id: str):
        """Get audit trail for a specific resource"""
        try:
            result = (self.supabase.table('audit_trail')
                     .select('*')
                     .eq('resource_type', resource_type)
                     .eq('resource_id', resource_id)
                     .order('timestamp', desc=True)
                     .execute())
            
            return result.data if result.data else []
            
        except Exception as e:
            print(f"[ERROR] Error getting resource audit trail: {str(e)}")
            return []
    
    def get_all_audit_trails(self, limit: int = 25, offset: int = 0):
        """Get all audit trails with pagination"""
        try:
            print(f"[DEBUG] Getting audit trails - Limit: {limit}, Offset: {offset}")
            
            if not self.supabase:
                print("[ERROR] Supabase service client not initialized")
                return []
            
            # Use service role for admin operations
            result = (self.supabase.table('audit_trail')
                     .select('*')
                     .order('timestamp', desc=True)
                     .range(offset, offset + limit - 1)
                     .execute())
            
            print(f"[DEBUG] Query result: {len(result.data) if result.data else 0} items")
            return result.data if result.data else []
            
        except Exception as e:
            print(f"[ERROR] Error getting all audit trails: {str(e)}")
            return []
    
    def get_audit_trails_count(self):
        """Get total count of audit trails"""
        try:
            if not self.supabase:
                print("[ERROR] Supabase service client not initialized")
                return 0
            
            # Get count of all audit trails
            result = (self.supabase.table('audit_trail')
                     .select('id', count='exact')
                     .execute())
            
            total_count = result.count if hasattr(result, 'count') and result.count is not None else 0
            print(f"[DEBUG] Total audit trails count: {total_count}")
            return total_count
            
        except Exception as e:
            print(f"[ERROR] Error getting audit trails count: {str(e)}")
            return 0

# Singleton instance
audit_trail_service = AuditTrailService()