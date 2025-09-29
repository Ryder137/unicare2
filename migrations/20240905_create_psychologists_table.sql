-- Create psychologists table
CREATE TABLE IF NOT EXISTS public.psychologists (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    license_number VARCHAR(50) UNIQUE,
    specialization VARCHAR(100),
    bio TEXT,
    years_of_experience INTEGER,
    education TEXT,
    languages_spoken TEXT[],
    consultation_fee DECIMAL(10, 2),
    is_available BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT fk_user FOREIGN KEY (user_id) REFERENCES auth.users(id) ON DELETE CASCADE
);

-- Enable Row Level Security
ALTER TABLE public.psychologists ENABLE ROW LEVEL SECURITY;

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_psychologists_user_id ON public.psychologists(user_id);
CREATE INDEX IF NOT EXISTS idx_psychologists_license_number ON public.psychologists(license_number);
CREATE INDEX IF NOT EXISTS idx_psychologists_specialization ON public.psychologists(specialization);

-- Create RLS policies
CREATE POLICY "Enable read access for authenticated users" 
ON public.psychologists 
FOR SELECT 
TO authenticated 
USING (true);

CREATE POLICY "Enable insert for authenticated users with psychologist role"
ON public.psychologists
FOR INSERT
TO authenticated
WITH CHECK (
    EXISTS (
        SELECT 1 FROM auth.users
        WHERE id = auth.uid()
        AND raw_user_meta_data->>'role' = 'psychologist'
    )
);

-- Create a trigger to update the updated_at column
CREATE OR REPLACE FUNCTION update_psychologists_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER set_psychologists_updated_at
BEFORE UPDATE ON public.psychologists
FOR EACH ROW
EXECUTE FUNCTION update_psychologists_updated_at();

-- Add comments for documentation
COMMENT ON TABLE public.psychologists IS 'Stores information about psychologists/doctors in the system';
COMMENT ON COLUMN public.psychologists.license_number IS 'Professional license number of the psychologist';
COMMENT ON COLUMN public.psychologists.specialization IS 'Area of specialization (e.g., Clinical, Counseling, Child Psychology)';
COMMENT ON COLUMN public.psychologists.bio IS 'Professional biography or description';
COMMENT ON COLUMN public.psychologists.years_of_experience IS 'Total years of professional experience';
COMMENT ON COLUMN public.psychologists.education IS 'Educational background and qualifications';
COMMENT ON COLUMN public.psychologists.languages_spoken IS 'Array of languages the psychologist is fluent in';
COMMENT ON COLUMN public.psychologists.consultation_fee IS 'Standard consultation fee per session';
COMMENT ON COLUMN public.psychologists.is_available IS 'Flag indicating if the psychologist is currently accepting new patients';



-- Drop and Create a view for public psychologist profiles
DROP VIEW IF EXISTS public.psychologist_profiles;
CREATE VIEW public.psychologist_profiles AS
select
  p.id,
  u.email,
  u.first_name || ' ' || u.last_name  as name,
  p.license_number,
  p.specialization,
  p.bio,
  p.years_of_experience,
  p.education,
  p.languages_spoken,
  p.consultation_fee,
  p.is_available,
  p.created_at,
  p.updated_at
from
  psychologists p
inner join user_accounts u on p.user_id = u.id
where 1=1
  AND p.is_available = true;

-- Grant necessary permissions
GRANT SELECT ON public.psychologists TO anon, authenticated;
GRANT SELECT ON public.psychologist_profiles TO anon, authenticated;
GRANT INSERT, UPDATE, DELETE ON public.psychologists TO authenticated;

-- If you're using Supabase, you might also want to create a function to handle new psychologist signups
CREATE OR REPLACE FUNCTION public.handle_new_psychologist()
RETURNS TRIGGER AS $$
BEGIN
    -- This function would be called by a trigger when a new user signs up as a psychologist
    -- You can customize this based on your authentication flow
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create a trigger to call the function when a new psychologist is added to auth.users
-- Note: This is a placeholder - you'll need to adjust this based on your auth flow
-- CREATE TRIGGER on_auth_user_created
-- AFTER INSERT ON auth.users
-- FOR EACH ROW
-- WHEN (NEW.raw_user_meta_data->>'role' = 'psychologist')
-- EXECUTE FUNCTION public.handle_new_psychologist();
