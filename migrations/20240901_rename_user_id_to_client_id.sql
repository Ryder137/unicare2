-- Rename user_id to client_id in game_scores table
ALTER TABLE game_scores RENAME COLUMN user_id TO client_id;

-- Update foreign key constraint for game_scores
ALTER TABLE game_scores 
    DROP CONSTRAINT IF EXISTS game_scores_user_id_fkey,
    ADD CONSTRAINT game_scores_client_id_fkey 
    FOREIGN KEY (client_id) REFERENCES clients(id) ON DELETE CASCADE;

-- Rename user_id to client_id in personality_tests table
ALTER TABLE personality_tests RENAME COLUMN user_id TO client_id;

-- Update foreign key constraint for personality_tests
ALTER TABLE personality_tests 
    DROP CONSTRAINT IF EXISTS personality_tests_user_id_fkey,
    ADD CONSTRAINT personality_tests_client_id_fkey 
    FOREIGN KEY (client_id) REFERENCES clients(id) ON DELETE CASCADE;

-- Update RLS policies to use client_id instead of user_id
-- Drop existing policies
DROP POLICY IF EXISTS "Enable insert for authenticated users" ON public.game_scores;
DROP POLICY IF EXISTS "Enable read access for own scores" ON public.game_scores;
DROP POLICY IF EXISTS "Enable update for own scores" ON public.game_scores;
DROP POLICY IF EXISTS "Enable delete for own scores" ON public.game_scores;

-- Recreate policies with client_id
CREATE POLICY "Enable insert for authenticated users" 
ON public.game_scores 
FOR INSERT 
TO authenticated 
WITH CHECK (auth.uid() = client_id);

CREATE POLICY "Enable read access for own scores" 
ON public.game_scores 
FOR SELECT 
USING (auth.uid() = client_id);

CREATE POLICY "Enable update for own scores" 
ON public.game_scores 
FOR UPDATE 
USING (auth.uid() = client_id);

CREATE POLICY "Enable delete for own scores" 
ON public.game_scores 
FOR DELETE 
USING (auth.uid() = client_id);

-- Update RLS policies for personality_tests
-- Drop existing policies
DROP POLICY IF EXISTS "Enable insert for authenticated users" ON public.personality_tests;
DROP POLICY IF EXISTS "Enable read access for own tests" ON public.personality_tests;
DROP POLICY IF EXISTS "Enable update for own tests" ON public.personality_tests;
DROP POLICY IF EXISTS "Enable delete for own tests" ON public.personality_tests;

-- Recreate policies with client_id
CREATE POLICY "Enable insert for authenticated users" 
ON public.personality_tests
FOR INSERT 
TO authenticated 
WITH CHECK (auth.uid() = client_id);

CREATE POLICY "Enable read access for own tests" 
ON public.personality_tests
FOR SELECT 
USING (auth.uid() = client_id);

CREATE POLICY "Enable update for own tests" 
ON public.personality_tests
FOR UPDATE 
USING (auth.uid() = client_id);

CREATE POLICY "Enable delete for own tests" 
ON public.personality_tests
FOR DELETE 
USING (auth.uid() = client_id);
