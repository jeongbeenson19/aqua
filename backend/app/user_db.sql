CREATE DATABASE user_db;

USE user_db;

CREATE TABLE user_progress (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    subject VARCHAR(255) NOT NULL,
    last_set_id INT DEFAULT 0,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

INSERT INTO user_progress (user_id, subject, last_set_id)
VALUES ('user_123', 'edu', 0);
