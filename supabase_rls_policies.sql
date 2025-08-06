-- Enable Row Level Security on all tables
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE game_scores ENABLE ROW LEVEL SECURITY;

-- Users Table Policies
-- Allow public signups (anon can insert new users)
CREATE POLICY "Enable insert for anon users only on users" 
ON public.users 
FOR INSERT 
TO anon 
WITH CHECK (true);

-- Users can read their own profile
drop policy if exists "Users can view their own profile" on users;
CREATE POLICY "Users can view their own profile" 
ON public.users 
FOR SELECT 
USING (auth.uid() = id);

-- Users can update their own profile
CREATE POLICY "Users can update own profile" 
ON public.users 
FOR UPDATE 
USING (auth.uid() = id);

-- Game Scores Table Policies
-- Users can insert their own scores
CREATE POLICY "Enable insert for authenticated users" 
ON public.game_scores 
FOR INSERT 
TO authenticated 
WITH CHECK (auth.uid() = user_id);

-- Users can read their own scores
CREATE POLICY "Enable read access for own scores" 
ON public.game_scores 
FOR SELECT 
USING (auth.uid() = user_id);

-- Users can update their own scores
CREATE POLICY "Enable update for own scores" 
ON public.game_scores 
FOR UPDATE 
USING (auth.uid() = user_id);

-- Users can delete their own scores
CREATE POLICY "Enable delete for own scores" 
ON public.game_scores 
FOR DELETE 
USING (auth.uid() = user_id);
