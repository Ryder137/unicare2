-- Reset and recreate auth tables
-- This will delete all data in users and admin_users tables

-- Disable RLS temporarily to allow the operations
ALTER TABLE IF EXISTS users DISABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS admin_users DISABLE ROW LEVEL SECURITY;

-- Clear existing data (be careful! this is destructive)
TRUNCATE TABLE users CASCADE;
TRUNCATE TABLE admin_users CASCADE;

-- Re-enable RLS
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE admin_users ENABLE ROW LEVEL SECURITY;

-- Create a default admin user
INSERT INTO admin_users (
    id,
    email,
    username,
    password_hash,
    first_name,
    last_name,
    is_active,
    is_super_admin,
    created_at,
    updated_at
) VALUES (
    gen_random_uuid(),
    'admin@example.com',
    'admin',
    -- Default password is 'admin123' (bcrypt hash)
    '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW',
    'Admin',
    'User',
    true,
    true,
    NOW(),
    NOW()
);

-- Create a test regular user
INSERT INTO users (
    id,
    email,
    username,
    password_hash,
    first_name,
    last_name,
    is_active,
    created_at,
    updated_at
) VALUES (
    gen_random_uuid(),
    'user@example.com',
    'testuser',
    -- Default password is 'user123' (bcrypt hash)
    '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW',
    'Test',
    'User',
    true,
    NOW(),
    NOW()
);

-- Output the created users for reference
SELECT 'Admin User:' as user_type, id, email, username, is_active, is_super_admin FROM admin_users
UNION ALL
SELECT 'Regular User:' as user_type, id, email, username, is_active, false as is_super_admin FROM users;
