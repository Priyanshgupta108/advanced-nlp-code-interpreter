-- NLP Code Interpreter v3.0 — Complete Supabase Setup
-- Run this ENTIRE script in Supabase SQL Editor

-- Step 1: Enable email auth (already on by default in Supabase)
-- Go to: Authentication → Providers → Email → Make sure it's enabled

-- Step 2: Create code_history table
CREATE TABLE IF NOT EXISTS code_history (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    code_hash TEXT NOT NULL,
    language TEXT,
    code TEXT,
    explanation TEXT,
    translation TEXT,
    complexity TEXT,
    bugs TEXT,
    test_cases TEXT,
    pseudocode TEXT,
    algorithm TEXT,
    approaches TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Step 3: Add columns if upgrading from v2
ALTER TABLE code_history ADD COLUMN IF NOT EXISTS user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE;
ALTER TABLE code_history ADD COLUMN IF NOT EXISTS algorithm TEXT;

-- Step 4: Enable RLS
ALTER TABLE code_history ENABLE ROW LEVEL SECURITY;

-- Step 5: Policies
DROP POLICY IF EXISTS "User owns their history" ON code_history;
DROP POLICY IF EXISTS "Anonymous access" ON code_history;
DROP POLICY IF EXISTS "Allow all operations" ON code_history;

-- Authenticated users see only their own data
CREATE POLICY "User owns their history" ON code_history
FOR ALL TO authenticated
USING (user_id = auth.uid())
WITH CHECK (user_id = auth.uid());

-- Anonymous users access records with no user_id
CREATE POLICY "Anonymous access" ON code_history
FOR ALL TO anon
USING (user_id IS NULL)
WITH CHECK (user_id IS NULL);

-- Step 6: Disable email confirmation (optional - for easier testing)
-- Go to: Authentication → Settings → Disable "Enable email confirmations"

SELECT 'v3.0 Setup complete!' as status;
