-- Enable RLS
ALTER TABLE admin_users ENABLE ROW LEVEL SECURITY;

-- Drop existing policies
DROP POLICY IF EXISTS "Enable service role access" ON public.admin_users;
DROP POLICY IF EXISTS "Allow service role to manage admin_users" ON public.admin_users;
DROP POLICY IF EXISTS "Allow admins to read all admin users" ON public.admin_users;
DROP POLICY IF EXISTS "Allow users to update their own admin profile" ON public.admin_users;

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
USING (auth.role() = 'authenticated' AND 
       EXISTS (
         SELECT 1 FROM admin_users 
         WHERE id = auth.uid() AND is_active = true
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
USING (id = auth.uid());
