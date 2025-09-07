-- Drop existing triggers if they exist
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'update_admin_users_modtime') THEN
        DROP TRIGGER update_admin_users_modtime ON public.admin_users;
    END IF;
    
    IF EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'update_admin_users_updated_at') THEN
        DROP TRIGGER update_admin_users_updated_at ON public.admin_users;
    END IF;
END $$;

-- Drop the function if it exists
DROP FUNCTION IF EXISTS public.update_updated_at_column() CASCADE;

-- Create or replace the function
CREATE OR REPLACE FUNCTION public.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;   
END;
$$ LANGUAGE plpgsql;

-- Create admin_users table if it doesn't exist
CREATE TABLE IF NOT EXISTS public.admin_users (
  id UUID NOT NULL DEFAULT gen_random_uuid(),
  email VARCHAR(255) NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  full_name VARCHAR(100) NULL,
  is_active BOOLEAN DEFAULT TRUE,
  is_super_admin BOOLEAN DEFAULT FALSE,
  last_login_at TIMESTAMPTZ NULL,
  failed_login_attempts INTEGER DEFAULT 0,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  CONSTRAINT admin_users_pkey PRIMARY KEY (id),
  CONSTRAINT admin_users_email_key UNIQUE (email)
) TABLESPACE pg_default;

-- Create index on email for faster lookups if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_indexes 
        WHERE indexname = 'idx_admin_users_email' 
        AND tablename = 'admin_users'
    ) THEN
        CREATE INDEX idx_admin_users_email 
        ON public.admin_users USING btree (email) 
        TABLESPACE pg_default;
    END IF;
END $$;

-- Create triggers if they don't exist
DO $$
BEGIN
    -- Create the main update trigger
    IF NOT EXISTS (
        SELECT 1 FROM pg_trigger 
        WHERE tgname = 'update_admin_users_modtime'
    ) THEN
        CREATE TRIGGER update_admin_users_modtime 
        BEFORE UPDATE ON public.admin_users 
        FOR EACH ROW 
        EXECUTE FUNCTION public.update_updated_at_column();
    END IF;
    
    -- Create the updated_at trigger (duplicate for backward compatibility)
    IF NOT EXISTS (
        SELECT 1 FROM pg_trigger 
        WHERE tgname = 'update_admin_users_updated_at'
    ) THEN
        CREATE TRIGGER update_admin_users_updated_at
        BEFORE UPDATE ON public.admin_users
        FOR EACH ROW
        EXECUTE FUNCTION public.update_updated_at_column();
    END IF;
END $$;

-- Add or update table comment
COMMENT ON TABLE public.admin_users IS 'Stores administrator user accounts with authentication details';

-- Add or update column comments
COMMENT ON COLUMN public.admin_users.id IS 'Primary key, auto-generated UUID';
COMMENT ON COLUMN public.admin_users.email IS 'Unique email address used for login';
COMMENT ON COLUMN public.admin_users.password_hash IS 'Hashed password using bcrypt';
COMMENT ON COLUMN public.admin_users.full_name IS 'Full name of the administrator';
COMMENT ON COLUMN public.admin_users.is_active IS 'Indicates if the account is active';
COMMENT ON COLUMN public.admin_users.is_super_admin IS 'Indicates if the user has super admin privileges';
COMMENT ON COLUMN public.admin_users.last_login_at IS 'Timestamp of last successful login';
COMMENT ON COLUMN public.admin_users.failed_login_attempts IS 'Count of consecutive failed login attempts';
COMMENT ON COLUMN public.admin_users.created_at IS 'Timestamp when the record was created';
COMMENT ON COLUMN public.admin_users.updated_at IS 'Timestamp when the record was last updated';
