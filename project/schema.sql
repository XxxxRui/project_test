-- Drop tables if they exist
DROP TABLE IF EXISTS shared_content;
DROP TABLE IF EXISTS health_data;
DROP TABLE IF EXISTS user;

-- Create users table
CREATE TABLE user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    date_created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Create health_data table for storing wellness metrics
CREATE TABLE health_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    date TEXT NOT NULL,  -- Store as 'YYYY-MM-DD'
    steps INTEGER NOT NULL,
    calories_burnt INTEGER NOT NULL,
    sleep_hours REAL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user (id),
    UNIQUE(user_id, date)
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
CREATE INDEX idx_health_data_user_date ON health_data (user_id, date);
CREATE INDEX idx_shared_content_shared_with ON shared_content (shared_with_id);

-- Insert test data
INSERT INTO user (username, password_hash) VALUES 
('user1', 'pbkdf2:sha256:150000$nt9djsA5$24d1e15d8a3aee9b33eb588ea445f244cb4ad521f88a797f39398c11bc5ac065'),
('user2', 'pbkdf2:sha256:150000$aLTf7IOk$10a06e0ca8753968d847f37d8cc6d110d33fcc257dfe3b71cfc4167e8efbd006'),
('user3', 'pbkdf2:sha256:150000$pGnVi8r3$c396838f25a2d7afe01b5b9eb769d5af488dcf2a1c1b69725e79b3f1a7a3b92e'),
('user4', 'pbkdf2:sha256:150000$nGQpshR7$6ad8e06c0cefc4ea8eb97afb1eb11dc9d61d88c4255e0f6ed8fb9e51fa661d01'),
('user5', 'pbkdf2:sha256:150000$hjUqW0Aw$e3a7fc66c56581e2e0f29cfe43c4742f638c115333d0cc13c4a09b4739dc67de');

-- Sample health data for user1
INSERT INTO health_data (user_id, date, steps, calories_burnt, sleep_hours) VALUES
(1, '2025-04-01', 6500, 320, 6.5),
(1, '2025-04-02', 8200, 380, 7.2),
(1, '2025-04-03', 7800, 350, 6.8),
(1, '2025-04-04', 9100, 420, 7.5),
(1, '2025-04-05', 9500, 430, 6.9),
(1, '2025-04-06', 10200, 490, 8.1),
(1, '2025-04-07', 8800, 410, 7.8),
(1, '2025-04-08', 9300, 440, 7.0),
(1, '2025-04-09', 7600, 360, 6.7),
(1, '2025-04-10', 8400, 390, 7.3),
(1, '2025-04-11', 9200, 425, 7.6),
(1, '2025-04-12', 10500, 510, 8.2),
(1, '2025-04-13', 9700, 450, 7.8),
(1, '2025-04-14', 8900, 415, 7.4);

-- Sample health data for user2
INSERT INTO health_data (user_id, date, steps, calories_burnt, sleep_hours) VALUES
(2, '2025-04-01', 7200, 340, 7.0),
(2, '2025-04-02', 8500, 400, 7.5),
(2, '2025-04-03', 8100, 370, 7.2),
(2, '2025-04-04', 9400, 440, 7.8),
(2, '2025-04-05', 9800, 450, 7.3),
(2, '2025-04-06', 10500, 510, 8.3),
(2, '2025-04-07', 9100, 430, 8.0);

-- Sample shared content
INSERT INTO shared_content (user_id, shared_with_id, content_type, content_id, message, share_date) VALUES
(2, 1, 'activity', '1', 'Great weekend hike', '2025-04-06'),
(3, 1, 'achievement', '2', 'Finally reached this milestone!', '2025-04-05'),
(1, 2, 'stats', 'weekly', 'My progress this week', '2025-04-07'),
(4, 1, 'activity', '3', 'Morning workout session', '2025-04-08');