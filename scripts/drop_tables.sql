-- Disable foreign key checks for the session to ensure a smooth drop
SET session_replication_role = 'replica';

-- Drop tables in reverse order of dependency, or use CASCADE for safety
DROP TABLE IF EXISTS Attends CASCADE;
DROP TABLE IF EXISTS Belongs CASCADE;
DROP TABLE IF EXISTS Displays CASCADE;
DROP TABLE IF EXISTS Category CASCADE;
DROP TABLE IF EXISTS Exhibition CASCADE;
DROP TABLE IF EXISTS Artwork CASCADE;
DROP TABLE IF EXISTS Customer CASCADE;
DROP TABLE IF EXISTS Artist CASCADE;
DROP TABLE IF EXISTS published_images CASCADE;

-- Re-enable standard replication role
SET session_replication_role = 'origin';

-- Confirmation message
DO $$ BEGIN RAISE NOTICE 'All gallery tables have been dropped.'; END $$;