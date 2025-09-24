-- Drop the existing function if it exists
DROP FUNCTION IF EXISTS public.get_guidance_counselors_with_users();

-- Recreate the function with correct return types
CREATE OR REPLACE FUNCTION public.get_guidance_counselors_with_users()
RETURNS TABLE (
    id UUID,
    email TEXT,
    name TEXT,
    license_number VARCHAR(100),
    specialization VARCHAR(100),
    bio TEXT,
    years_of_experience INTEGER,
    education TEXT,
    languages_spoken TEXT[],
    is_available BOOLEAN,
    created_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ
)
LANGUAGE sql
SECURITY DEFINER
AS $$
    SELECT 
        gc.id,
        u.email::TEXT,
        (u.raw_user_meta_data->>'full_name')::TEXT as name,
        gc.license_number,
        gc.specialization,
        gc.bio,
        gc.years_of_experience,
        gc.education,
        gc.languages_spoken,
        gc.is_available,
        gc.created_at,
        gc.updated_at
    FROM 
        public.guidance_counselors gc
    JOIN 
        auth.users u ON gc.user_id = u.id
    WHERE 
        gc.is_available = true;
$$;

-- Grant execute permission to authenticated users
GRANT EXECUTE ON FUNCTION public.get_guidance_counselors_with_users() TO authenticated;

-- Update the view to use the function
CREATE OR REPLACE VIEW public.guidance_counselor_profiles AS
SELECT * FROM public.get_guidance_counselors_with_users();

-- Grant necessary permissions
GRANT SELECT ON public.guidance_counselor_profiles TO anon, authenticated;
