-- Drop existing triggers if they exist
DO $$
BEGIN
    EXECUTE 'DROP TRIGGER IF EXISTS update_clirnts_modtime ON public.clirnts';
    EXECUTE 'DROP TRIGGER IF EXISTS update_clirnts_updated_at ON public.clirnts';
EXCEPTION WHEN OTHERS THEN
    RAISE NOTICE 'Error dropping triggers: %', SQLERRM;
END $$;

-- Drop the function if it exists
DO $$
BEGIN
    EXECUTE 'DROP FUNCTION IF EXISTS public.update_updated_at_column() CASCADE';
EXCEPTION WHEN OTHERS THEN
    RAISE NOTICE 'Error dropping function: %', SQLERRM;
END $$;

-- Create the function
CREATE OR REPLACE FUNCTION public.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create the table (drop if exists first)
DROP TABLE IF EXISTS public.clirnts CASCADE;

CREATE TABLE public.clirnts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    is_admin BOOLEAN DEFAULT FALSE,
    is_super_admin BOOLEAN DEFAULT FALSE,
    last_login_at TIMESTAMPTZ,
    failed_login_attempts INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create index
CREATE INDEX IF NOT EXISTS idx_clirnts_email ON public.clirnts (email);

-- Create the triggers
CREATE TRIGGER update_clirnts_modtime
BEFORE UPDATE ON public.clirnts
FOR EACH ROW
EXECUTE FUNCTION public.update_updated_at_column();

-- Add comments
COMMENT ON TABLE public.admin_users IS 'Stores administrator user accounts with authentication details';
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
