-- -- Drop tables if they exist
-- DROP TABLE IF EXISTS shared_content;
-- DROP TABLE IF EXISTS activity_data;
-- DROP TABLE IF EXISTS exercise_types;
-- DROP TABLE IF EXISTS user;

-- Create users table
CREATE TABLE user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    date_created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Create exercise_types table
CREATE TABLE exercise_types (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    calories_per_minute REAL NOT NULL
);

-- Create activity_data table for storing wellness metrics
CREATE TABLE activity_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    exercise_type_id INTEGER NOT NULL,
    date TEXT NOT NULL,  -- Store as 'YYYY-MM-DD'
    duration_minutes INTEGER NOT NULL,
    calories_burnt INTEGER NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user (id),
    FOREIGN KEY (exercise_type_id) REFERENCES exercise_types (id)
);

-- Create shared_content table
CREATE TABLE shared_content (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    shared_with_id INTEGER NOT NULL,
    content_type TEXT NOT NULL,  -- 'activity', 'achievement', 'stats'
    content_id TEXT NOT NULL,    -- Identifies the specific content being shared
    message TEXT,
    share_date TEXT NOT NULL,    -- Store as 'YYYY-MM-DD'
    FOREIGN KEY (user_id) REFERENCES user (id),
    FOREIGN KEY (shared_with_id) REFERENCES user (id)
);

-- Create index for faster queries
CREATE INDEX idx_activity_data_user_date ON activity_data (user_id, date);
CREATE INDEX idx_shared_content_shared_with ON shared_content (shared_with_id);

-- Insert common exercise types with calories per minute
INSERT INTO exercise_types (name, calories_per_minute) VALUES 
('Running', 11.5),
('Walking', 5.0),
('Cycling', 8.5),
('Swimming', 10.0),
('Hiking', 7.0),
('Weight Training', 6.0),
('Yoga', 3.5),
('Dancing', 7.5),
('Basketball', 9.0),
('Soccer', 10.0);

-- Insert test users
INSERT INTO user (username, password_hash) VALUES 
('user1', 'pbkdf2:sha256:150000$nt9djsA5$24d1e15d8a3aee9b33eb588ea445f244cb4ad521f88a797f39398c11bc5ac065'),
('user2', 'pbkdf2:sha256:150000$aLTf7IOk$10a06e0ca8753968d847f37d8cc6d110d33fcc257dfe3b71cfc4167e8efbd006'),
('user3', 'pbkdf2:sha256:150000$pGnVi8r3$c396838f25a2d7afe01b5b9eb769d5af488dcf2a1c1b69725e79b3f1a7a3b92e');

-- Sample activity data for user1
INSERT INTO activity_data (user_id, exercise_type_id, date, duration_minutes, calories_burnt) VALUES
(1, 1, '2025-04-01', 30, 345),  -- Running
(1, 2, '2025-04-02', 45, 225),  -- Walking
(1, 3, '2025-04-03', 40, 340),  -- Cycling
(1, 4, '2025-04-04', 35, 350),  -- Swimming
(1, 1, '2025-04-05', 25, 288),  -- Running
(1, 5, '2025-04-06', 60, 420),  -- Hiking
(1, 6, '2025-04-07', 50, 300);  -- Weight Training