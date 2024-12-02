-- Users table
CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Subscriptions table
CREATE TABLE subscriptions (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    plan_type ENUM('basic', 'standard', 'premium') NOT NULL,
    start_date TIMESTAMP NOT NULL,
    end_date TIMESTAMP NOT NULL,
    auto_renewal BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Series table
CREATE TABLE series (
    id INT PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    release_year INT NOT NULL,
    genre VARCHAR(50) NOT NULL,
    rating VARCHAR(10) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Seasons table
CREATE TABLE seasons (
    id INT PRIMARY KEY AUTO_INCREMENT,
    series_id INT NOT NULL,
    season_number INT NOT NULL,
    title VARCHAR(255) NOT NULL,
    release_date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (series_id) REFERENCES series(id),
    UNIQUE KEY series_season (series_id, season_number)
);

-- Episodes table
CREATE TABLE episodes (
    id INT PRIMARY KEY AUTO_INCREMENT,
    season_id INT NOT NULL,
    episode_number INT NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    duration INT NOT NULL, -- in seconds
    release_date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (season_id) REFERENCES seasons(id),
    UNIQUE KEY season_episode (season_id, episode_number)
);

-- Reviews table
CREATE TABLE reviews (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    series_id INT NOT NULL,
    rating INT NOT NULL CHECK (rating >= 1 AND rating <= 5),
    comment TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (series_id) REFERENCES series(id),
    UNIQUE KEY user_series_review (user_id, series_id)
);

-- Viewing Progress table
CREATE TABLE viewing_progress (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    episode_id INT NOT NULL,
    progress INT NOT NULL, -- in seconds
    completed BOOLEAN DEFAULT FALSE,
    last_watched TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (episode_id) REFERENCES episodes(id),
    UNIQUE KEY user_episode_progress (user_id, episode_id)
);
