-- Admin Tables for UniCare2
-- Created: 2024-08-28

-- 1. Admin Users
CREATE TABLE IF NOT EXISTS admin_users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    is_super_admin BOOLEAN DEFAULT FALSE,
    last_login_at TIMESTAMPTZ,
    failed_login_attempts INT DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. Admin Roles
CREATE TABLE IF NOT EXISTS admin_roles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. User Roles
CREATE TABLE IF NOT EXISTS admin_user_roles (
    user_id UUID REFERENCES admin_users(id) ON DELETE CASCADE,
    role_id UUID REFERENCES admin_roles(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (user_id, role_id)
);

-- 4. Admin Permissions
CREATE TABLE IF NOT EXISTS admin_permissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 5. Role Permissions
CREATE TABLE IF NOT EXISTS admin_role_permissions (
    role_id UUID REFERENCES admin_roles(id) ON DELETE CASCADE,
    permission_id UUID REFERENCES admin_permissions(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (role_id, permission_id)
);

-- 6. Admin Audit Logs
CREATE TABLE IF NOT EXISTS admin_audit_logs (
    id BIGSERIAL PRIMARY KEY,
    admin_id UUID REFERENCES admin_users(id) ON DELETE SET NULL,
    action VARCHAR(50) NOT NULL,
    entity_type VARCHAR(50),
    entity_id UUID,
    old_values JSONB,
    new_values JSONB,
    ip_address INET,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 7. Admin Settings
CREATE TABLE IF NOT EXISTS admin_settings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    setting_key VARCHAR(100) UNIQUE NOT NULL,
    setting_value JSONB NOT NULL,
    description TEXT,
    is_public BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_admin_users_email ON admin_users(email);
CREATE INDEX IF NOT EXISTS idx_admin_audit_logs_admin_id ON admin_audit_logs(admin_id);
CREATE INDEX IF NOT EXISTS idx_admin_audit_logs_created_at ON admin_audit_logs(created_at);

-- Add sample data
INSERT INTO admin_roles (name, description) VALUES 
    ('super_admin', 'Full access to all features')
ON CONFLICT (name) DO NOTHING;

INSERT INTO admin_permissions (name, description) VALUES 
    ('manage_users', 'Can manage admin users'),
    ('manage_roles', 'Can manage roles and permissions'),
    ('view_dashboard', 'Can view admin dashboard')
ON CONFLICT (name) DO NOTHING;

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_modified_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Drop existing triggers if they exist
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'update_admin_users_modtime') THEN
        DROP TRIGGER update_admin_users_modtime ON admin_users;
    END IF;
    
    IF EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'update_admin_settings_modtime') THEN
        DROP TRIGGER update_admin_settings_modtime ON admin_settings;
    END IF;
    
    IF EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'update_admin_audit_logs_modtime') THEN
        DROP TRIGGER update_admin_audit_logs_modtime ON admin_audit_logs;
    END IF;
END $$;

-- Create triggers
CREATE TRIGGER update_admin_users_modtime
BEFORE UPDATE ON admin_users
FOR EACH ROW EXECUTE FUNCTION update_modified_column();

-- Note: Uncomment these when the tables are created
-- CREATE TRIGGER update_admin_settings_modtime
-- BEFORE UPDATE ON admin_settings
-- FOR EACH ROW EXECUTE FUNCTION update_modified_column();

-- CREATE TRIGGER update_admin_audit_logs_modtime
-- BEFORE UPDATE ON admin_audit_logs
-- FOR EACH ROW EXECUTE FUNCTION update_modified_column();
