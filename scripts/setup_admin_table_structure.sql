-- Create admin_users table if it doesn't exist
DO $$
BEGIN
    -- Create the table if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM pg_tables WHERE schemaname = 'public' AND tablename = 'admin_users') THEN
        CREATE TABLE public.admin_users (
            id UUID PRIMARY KEY REFERENCES auth.users ON DELETE CASCADE,
            email TEXT NOT NULL,
            full_name TEXT,
            is_active BOOLEAN DEFAULT true,
            is_super_admin BOOLEAN DEFAULT false,
            failed_login_attempts INTEGER DEFAULT 0,
            last_login_at TIMESTAMPTZ,
            created_at TIMESTAMPTZ DEFAULT NOW(),
            updated_at TIMESTAMPTZ DEFAULT NOW(),
            CONSTRAINT admin_users_email_key UNIQUE (email)
        );
    ELSE
        -- Add any missing columns if the table already exists
        ALTER TABLE public.admin_users 
            ADD COLUMN IF NOT EXISTS full_name TEXT,
            ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT true,
            ADD COLUMN IF NOT EXISTS is_super_admin BOOLEAN DEFAULT false,
            ADD COLUMN IF NOT EXISTS failed_login_attempts INTEGER DEFAULT 0,
            ADD COLUMN IF NOT EXISTS last_login_at TIMESTAMPTZ,
            ADD COLUMN IF NOT EXISTS created_at TIMESTAMPTZ DEFAULT NOW(),
            ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ DEFAULT NOW();
            
        -- Add unique constraint if it doesn't exist
        IF NOT EXISTS (
            SELECT 1 FROM pg_constraint 
            WHERE conname = 'admin_users_email_key' AND conrelid = 'public.admin_users'::regclass
        ) THEN
            ALTER TABLE public.admin_users ADD CONSTRAINT admin_users_email_key UNIQUE (email);
        END IF;
    END IF;
END $$;

-- Enable RLS
ALTER TABLE public.admin_users ENABLE ROW LEVEL SECURITY;

-- Drop existing policies if they exist
DO $$
BEGIN
    DROP POLICY IF EXISTS "Enable service role access" ON public.admin_users;
    DROP POLICY IF EXISTS "Allow service role to manage admin_users" ON public.admin_users;
    DROP POLICY IF EXISTS "Allow admins to read all admin users" ON public.admin_users;
    DROP POLICY IF EXISTS "Allow users to update their own admin profile" ON public.admin_users;
    DROP POLICY IF EXISTS "Allow users to view their own profile" ON public.admin_users;
EXCEPTION WHEN OTHERS THEN
    RAISE NOTICE 'Error dropping policies: %', SQLERRM;
END $$;

-- Service role can do anything (for backend operations)
CREATE POLICY "Allow service role to manage admin_users" 
ON public.admin_users
FOR ALL
USING (auth.role() = 'service_role')
WITH CHECK (auth.role() = 'service_role');

-- Allow admin users to read all admin users
CREATE POLICY "Allow admins to read all admin users"
ON public.admin_users
FOR SELECT
USING (EXISTS (
    SELECT 1 FROM admin_users 
    WHERE id = auth.uid() AND is_active = true AND is_super_admin = true
));

-- Allow users to update their own profile
CREATE POLICY "Allow users to update their own admin profile"
ON public.admin_users
FOR UPDATE
USING (id = auth.uid())
WITH CHECK (id = auth.uid());

-- Allow authenticated users to see their own profile
CREATE POLICY "Allow users to view their own profile"
ON public.admin_users
FOR SELECT
USING (id = auth.uid() OR 
      (SELECT is_super_admin FROM admin_users WHERE id = auth.uid()));

-- Create or replace the update_updated_at_column function
CREATE OR REPLACE FUNCTION public.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create the trigger if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_trigger 
        WHERE tgname = 'update_admin_users_updated_at' 
        AND tgrelid = 'public.admin_users'::regclass
    ) THEN
        CREATE TRIGGER update_admin_users_updated_at
        BEFORE UPDATE ON public.admin_users
        FOR EACH ROW
        EXECUTE FUNCTION public.update_updated_at_column();
    END IF;
EXCEPTION WHEN OTHERS THEN
    RAISE NOTICE 'Error creating trigger: %', SQLERRM;
END $$;
