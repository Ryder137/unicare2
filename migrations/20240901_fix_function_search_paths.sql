-- Fix function search paths for security
-- Created: 2024-09-01

-- 1. Update the update_modified_column function
CREATE OR REPLACE FUNCTION public.update_modified_column()
RETURNS TRIGGER
LANGUAGE plpgsql
-- Set a secure search path that only includes the public schema
SET search_path = public, pg_temp
AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$;

-- 2. Update the create_user_profile function (if it exists)
DO $$
BEGIN
    -- Check if the function exists
    IF EXISTS (
        SELECT 1 
        FROM pg_proc p 
        JOIN pg_namespace n ON p.pronamespace = n.oid 
        WHERE n.nspname = 'public' 
        AND p.proname = 'create_user_profile'
    ) THEN
        EXECUTE '
        CREATE OR REPLACE FUNCTION public.create_user_profile()
        RETURNS TRIGGER
        LANGUAGE plpgsql
        SECURITY DEFINER
        SET search_path = public, pg_temp
        AS $func$
        BEGIN
            INSERT INTO public.profiles (id, username, full_name, avatar_url)
            VALUES (
                NEW.id,
                COALESCE(NEW.raw_user_meta_data->>''username'', NEW.raw_user_meta_data->>''name'', NEW.email),
                COALESCE(NEW.raw_user_meta_data->>''full_name'', NEW.raw_user_meta_data->>''name''),
                NEW.raw_user_meta_data->>''avatar_url''
            )
            ON CONFLICT (id) DO NOTHING;
            RETURN NEW;
        END;
        $func$;';
    END IF;
END $$;

-- 3. Update the handle_new_user function (if it exists)
DO $$
BEGIN
    -- Check if the function exists
    IF EXISTS (
        SELECT 1 
        FROM pg_proc p 
        JOIN pg_namespace n ON p.pronamespace = n.oid 
        WHERE n.nspname = 'public' 
        AND p.proname = 'handle_new_user'
    ) THEN
        EXECUTE '
        CREATE OR REPLACE FUNCTION public.handle_new_user()
        RETURNS TRIGGER
        LANGUAGE plpgsql
        SECURITY DEFINER
        SET search_path = public, pg_temp
        AS $func$
        BEGIN
            -- Your existing handle_new_user logic here
            -- This is a placeholder - adjust according to your actual function
            RETURN NEW;
        END;
        $func$;';
    END IF;
END $$;

-- 4. Update the update_updated_at_column function (if it exists)
DO $$
BEGIN
    -- Check if the function exists
    IF EXISTS (
        SELECT 1 
        FROM pg_proc p 
        JOIN pg_namespace n ON p.pronamespace = n.oid 
        WHERE n.nspname = 'public' 
        AND p.proname = 'update_updated_at_column'
    ) THEN
        EXECUTE '
        CREATE OR REPLACE FUNCTION public.update_updated_at_column()
        RETURNS TRIGGER
        LANGUAGE plpgsql
        SET search_path = public, pg_temp
        AS $func$
        BEGIN
            NEW.updated_at = NOW();
            RETURN NEW;
        END;
        $func$;';
    END IF;
END $$;

-- Update triggers to use the updated functions
-- Note: You may need to drop and recreate triggers that use these functions
-- Example for update_modified_column trigger (adjust as needed):
DO $$
BEGIN
    -- Drop the trigger if it exists
    IF EXISTS (
        SELECT 1 
        FROM pg_trigger 
        WHERE tgname = 'update_admin_users_modtime'
    ) THEN
        DROP TRIGGER update_admin_users_modtime ON admin_users;
    END IF;
    
    -- Recreate the trigger
    CREATE TRIGGER update_admin_users_modtime
    BEFORE UPDATE ON admin_users
    FOR EACH ROW EXECUTE FUNCTION public.update_modified_column();
    
    -- Repeat for other tables that use this function
    -- Example:
    -- IF EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'update_admin_settings_modtime') THEN
    --     DROP TRIGGER update_admin_settings_modtime ON admin_settings;
    -- END IF;
    -- CREATE TRIGGER update_admin_settings_modtime
    -- BEFORE UPDATE ON admin_settings
    -- FOR EACH ROW EXECUTE FUNCTION public.update_modified_column();
END $$;

-- Note: For the auth-related warnings (leaked password protection and MFA options),
-- these need to be configured in your Supabase dashboard under Authentication -> Settings
-- Go to https://supabase.com/dashboard/project/_/auth/settings to enable these features
