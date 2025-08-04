-- MySQL initialization script for Ally Platform
-- This script runs when the MySQL container is first created

USE ally_db;

-- Create tables for the application
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_email (email),
    INDEX idx_username (username)
);

-- Create a sample configuration table
CREATE TABLE IF NOT EXISTS app_config (
    id INT AUTO_INCREMENT PRIMARY KEY,
    config_key VARCHAR(100) UNIQUE NOT NULL,
    config_value TEXT,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Insert default configuration
INSERT INTO app_config (config_key, config_value, description) VALUES
('app_name', 'Ally Platform', 'Application name'),
('app_version', '1.0.0', 'Application version'),
('maintenance_mode', 'false', 'Maintenance mode flag');

-- Create a test table for development
CREATE TABLE IF NOT EXISTS test_data (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    data JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert sample test data
INSERT INTO test_data (name, data) VALUES
('sample_1', '{"type": "test", "value": 100}'),
('sample_2', '{"type": "demo", "value": 200}');

-- Grant permissions (additional safety measure)
GRANT ALL PRIVILEGES ON ally_db.* TO 'ally_user'@'%';
FLUSH PRIVILEGES;

-- Log initialization completion
SELECT 'Ally Platform database initialized successfully!' as message;
