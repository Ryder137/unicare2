-- Create guidance_counselors table
CREATE TABLE IF NOT EXISTS public.guidance_counselors (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    license_number VARCHAR(50) NOT NULL,
    specialization VARCHAR(100) NOT NULL,
    bio TEXT,
    years_of_experience INTEGER CHECK (years_of_experience >= 0 AND years_of_experience <= 60),
    education TEXT NOT NULL,
    languages_spoken TEXT[] NOT NULL DEFAULT '{}'::TEXT[],
    is_available BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT fk_guidance_counselor_user 
        FOREIGN KEY (user_id) 
        REFERENCES auth.users(id) 
        ON DELETE CASCADE,
        
    CONSTRAINT uq_guidance_counselor_license 
        UNIQUE (license_number),
        
    CONSTRAINT ck_license_number_format 
        CHECK (license_number ~ '^[A-Z0-9-]+$')
);

-- Add table comment
COMMENT ON TABLE public.guidance_counselors IS 'Stores information about guidance counselors in the system';

-- Add column comments
COMMENT ON COLUMN public.guidance_counselors.license_number IS 'Professional license number (alphanumeric and hyphens only)';
COMMENT ON COLUMN public.guidance_counselors.specialization IS 'Primary area of specialization';
COMMENT ON COLUMN public.guidance_counselors.years_of_experience IS 'Total years of professional experience (0-60)';
COMMENT ON COLUMN public.guidance_counselors.languages_spoken IS 'Array of languages the counselor is proficient in';

-- Enable Row Level Security
ALTER TABLE public.guidance_counselors ENABLE ROW LEVEL SECURITY;

-- Create policies for Row Level Security
CREATE POLICY "Enable read access for authenticated users" 
ON public.guidance_counselors 
FOR SELECT 
TO authenticated 
USING (true);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_guidance_counselors_user_id 
    ON public.guidance_counselors(user_id);

CREATE INDEX IF NOT EXISTS idx_guidance_counselors_specialization 
    ON public.guidance_counselors(specialization);

CREATE INDEX IF NOT EXISTS idx_guidance_counselors_languages 
    ON public.guidance_counselors USING GIN(languages_spoken);

-- Create trigger function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_guidance_counselor_modified()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger
CREATE TRIGGER trigger_update_guidance_counselor_modified
BEFORE UPDATE ON public.guidance_counselors
FOR EACH ROW
EXECUTE FUNCTION update_guidance_counselor_modified();
CREATE INDEX IF NOT EXISTS idx_guidance_counselors_license ON public.guidance_counselors(license_number);

-- Create RLS policies
CREATE POLICY "Enable read access for all users" 
ON public.guidance_counselors 
FOR SELECT 
TO authenticated 
USING (true);

CREATE POLICY "Enable insert for authenticated users with guidance_counselor role"
ON public.guidance_counselors
FOR INSERT
TO authenticated
WITH CHECK (
    EXISTS (
        SELECT 1 FROM auth.users
        WHERE id = auth.uid()
        AND raw_user_meta_data->>'role' = 'guidance_counselor'
    )
);

-- Create a trigger to update the updated_at column
CREATE OR REPLACE FUNCTION update_guidance_counselors_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER set_guidance_counselors_updated_at
BEFORE UPDATE ON public.guidance_counselors
FOR EACH ROW
EXECUTE FUNCTION update_guidance_counselors_updated_at();

-- Add comments for documentation
COMMENT ON TABLE public.guidance_counselors IS 'Stores information about guidance counselors in the system';
COMMENT ON COLUMN public.guidance_counselors.license_number IS 'Professional license number of the guidance counselor';
COMMENT ON COLUMN public.guidance_counselors.specialization IS 'Area of specialization (e.g., Career Counseling, Academic Advising)';
COMMENT ON COLUMN public.guidance_counselors.bio IS 'Professional biography or description';
COMMENT ON COLUMN public.guidance_counselors.years_of_experience IS 'Total years of professional experience';
COMMENT ON COLUMN public.guidance_counselors.education IS 'Educational background and qualifications';
COMMENT ON COLUMN public.guidance_counselors.languages_spoken IS 'Array of languages the counselor is fluent in';
COMMENT ON COLUMN public.guidance_counselors.is_available IS 'Flag indicating if the counselor is currently available for appointments';

-- Create a view for public guidance counselor profiles
CREATE OR REPLACE VIEW public.guidance_counselor_profiles AS
SELECT 
    gc.id,
    u.email,
    u.raw_user_meta_data->>'full_name' as name,
    gc.license_number,
    gc.specialization,
    gc.bio,
    gc.years_of_experience,
    gc.education,
    gc.languages_spoken,
    gc.is_available,
    gc.created_at,
    gc.updated_at
FROM public.guidance_counselors gc
JOIN auth.users u ON gc.user_id = u.id
WHERE gc.is_available = true;

-- Grant necessary permissions
GRANT SELECT ON public.guidance_counselors TO anon, authenticated;
GRANT SELECT ON public.guidance_counselor_profiles TO anon, authenticated;
GRANT INSERT, UPDATE, DELETE ON public.guidance_counselors TO authenticated;
