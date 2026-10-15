-- Database Schema for AI-Powered Extempore & Current Affairs Practice App

CREATE TABLE IF NOT EXISTS categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    slug VARCHAR(50) NOT NULL UNIQUE,
    icon VARCHAR(20) DEFAULT '📌',
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) NOT NULL UNIQUE,
    email VARCHAR(150) UNIQUE,
    password_hash VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS headlines_cache (
    id INT AUTO_INCREMENT PRIMARY KEY,
    category_id INT,
    headline TEXT NOT NULL,
    source_name VARCHAR(100),
    source_url TEXT,
    published_date VARCHAR(100),
    fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS practice_sessions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NULL,
    category_name VARCHAR(100) NOT NULL,
    headline TEXT NOT NULL,
    source_name VARCHAR(100),
    question TEXT NOT NULL,
    prep_time_seconds INT NOT NULL DEFAULT 60,
    answer_time_seconds INT NOT NULL DEFAULT 300,
    time_taken_seconds INT NOT NULL DEFAULT 0,
    user_answer TEXT NOT NULL,
    word_count INT DEFAULT 0,
    input_mode VARCHAR(20) DEFAULT 'text',
    scratchpad_notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS evaluations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    session_id INT NOT NULL,
    score_factual INT NOT NULL,
    score_relevance INT NOT NULL,
    score_structure INT NOT NULL,
    score_depth INT NOT NULL,
    score_time INT NOT NULL,
    total_score INT NOT NULL,
    factual_feedback TEXT,
    relevance_feedback TEXT,
    structure_feedback TEXT,
    depth_feedback TEXT,
    time_feedback TEXT,
    overall_feedback TEXT,
    model_answer_structure TEXT,
    ai_evaluator_type VARCHAR(50) DEFAULT 'gemini-or-rubric',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES practice_sessions(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Seed default categories
INSERT IGNORE INTO categories (id, name, slug, icon, description) VALUES
(1, 'National & Polity (UPSC)', 'polity', '🇮🇳', 'Governance, constitutional amendments, public policy, and national developments'),
(2, 'International Relations', 'world', '🌍', 'Geopolitics, multilateral summits, treaties, and global diplomacy'),
(3, 'Tech, AI & Cybersecurity', 'tech', '💻', 'Artificial intelligence, cybersecurity breaches, digital data sovereignty, and space tech'),
(4, 'Economy & Sustainable Growth', 'economy', '📈', 'Fiscal policy, inflation, climate economics, infrastructure, and markets'),
(5, 'Sports, Society & Culture', 'sports', '⚽', 'Major sporting events, social ethics, cultural heritage, and institutional reforms'),
(6, 'General / Live News Mix', 'general', '🎲', 'Eclectic top breaking headlines for spontaneous debate');
