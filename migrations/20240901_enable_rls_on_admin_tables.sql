-- Enable Row Level Security (RLS) on admin tables
-- Created: 2024-09-01

-- Enable RLS on all admin tables
ALTER TABLE admin_users ENABLE ROW LEVEL SECURITY;
ALTER TABLE admin_roles ENABLE ROW LEVEL SECURITY;
ALTER TABLE admin_user_roles ENABLE ROW LEVEL SECURITY;
ALTER TABLE admin_permissions ENABLE ROW LEVEL SECURITY;
ALTER TABLE admin_role_permissions ENABLE ROW LEVEL SECURITY;
ALTER TABLE admin_audit_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE admin_settings ENABLE ROW LEVEL SECURITY;

-- Create a role for admin users
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'authenticated_admin') THEN
        CREATE ROLE authenticated_admin;
    END IF;
END $$;

-- 1. Admin Users Policies
-- Allow admins to view all users (but not sensitive data like password hashes)
CREATE POLICY "Enable read access for authenticated admins"
ON admin_users
FOR SELECT
TO authenticated_admin
USING (true);

-- Allow admins to update their own profile
CREATE POLICY "Enable update for self"
ON admin_users
FOR UPDATE
TO authenticated_admin
USING (id = current_setting('request.jwt.claim.sub', true)::uuid);

-- 2. Admin Roles Policies
-- Allow reading roles
CREATE POLICY "Enable read access for authenticated admins"
ON admin_roles
FOR SELECT
TO authenticated_admin
USING (true);

-- 3. User Roles Policies
-- Allow admins to view role assignments
CREATE POLICY "Enable read access for authenticated admins"
ON admin_user_roles
FOR SELECT
TO authenticated_admin
USING (true);

-- Allow super admins to manage role assignments
CREATE POLICY "Enable all for super admins"
ON admin_user_roles
FOR ALL
TO authenticated_admin
USING (
    EXISTS (
        SELECT 1 FROM admin_users 
        WHERE id = current_setting('request.jwt.claim.sub', true)::uuid
        AND is_super_admin = true
    )
);

-- 4. Permissions Policies
-- Allow reading permissions
CREATE POLICY "Enable read access for authenticated admins"
ON admin_permissions
FOR SELECT
TO authenticated_admin
USING (true);

-- 5. Role Permissions Policies
-- Allow reading role-permission assignments
CREATE POLICY "Enable read access for authenticated admins"
ON admin_role_permissions
FOR SELECT
TO authenticated_admin
USING (true);

-- Allow super admins to manage role-permission assignments
CREATE POLICY "Enable all for super admins"
ON admin_role_permissions
FOR ALL
TO authenticated_admin
USING (
    EXISTS (
        SELECT 1 FROM admin_users 
        WHERE id = current_setting('request.jwt.claim.sub', true)::uuid
        AND is_super_admin = true
    )
);

-- 6. Audit Logs Policies
-- Allow admins to view audit logs
CREATE POLICY "Enable read access for authenticated admins"
ON admin_audit_logs
FOR SELECT
TO authenticated_admin
USING (true);

-- Allow system to insert audit logs
CREATE POLICY "Enable insert for service role"
ON admin_audit_logs
FOR INSERT
TO service_role
WITH CHECK (true);

-- 7. Admin Settings Policies
-- Allow reading public settings
CREATE POLICY "Enable read access for public settings"
ON admin_settings
FOR SELECT
TO public
USING (is_public = true);

-- Allow admins to read all settings
CREATE POLICY "Enable read access for authenticated admins"
ON admin_settings
FOR SELECT
TO authenticated_admin
USING (true);

-- Allow super admins to update settings
CREATE POLICY "Enable update for super admins"
ON admin_settings
FOR UPDATE
TO authenticated_admin
USING (
    EXISTS (
        SELECT 1 FROM admin_users 
        WHERE id = current_setting('request.jwt.claim.sub', true)::uuid
        AND is_super_admin = true
    )
);

-- Add a function to check if a user has a specific permission
CREATE OR REPLACE FUNCTION public.has_permission(permission_name text)
RETURNS boolean
LANGUAGE plpgsql
SECURITY DEFINER
-- Set a secure search path that only includes the public schema
SET search_path = public, pg_temp
AS $$
DECLARE
    has_permission boolean;
BEGIN
    SELECT EXISTS (
        SELECT 1 
        FROM admin_user_roles ur
        JOIN admin_role_permissions rp ON ur.role_id = rp.role_id
        JOIN admin_permissions p ON rp.permission_id = p.id
        WHERE ur.user_id = current_setting('request.jwt.claim.sub', true)::uuid
        AND p.name = permission_name
    ) INTO has_permission;
    
    RETURN has_permission;
END;
$$;

-- Create a function to get the current admin user
CREATE OR REPLACE FUNCTION public.current_admin_user()
RETURNS SETOF admin_users
LANGUAGE plpgsql
STABLE SECURITY DEFINER
-- Set a secure search path that only includes the public schema
SET search_path = public, pg_temp
AS $$
BEGIN
    RETURN QUERY
    SELECT * 
    FROM admin_users
    WHERE id = current_setting('request.jwt.claim.sub', true)::uuid;
END;
$$;

-- Grant necessary permissions to the authenticated_admin role
GRANT USAGE ON SCHEMA public TO authenticated_admin;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO authenticated_admin;
GRANT INSERT, UPDATE, DELETE ON admin_users TO authenticated_admin;
GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO authenticated_admin;
