-- Add status column to assessments table
ALTER TABLE assessments 
ADD COLUMN IF NOT EXISTS status VARCHAR(20) DEFAULT 'pending';

-- Update existing records to have a default status if needed
UPDATE assessments 
SET status = 'completed' 
WHERE status IS NULL;
