-- 데이터베이스 생성
CREATE DATABASE coupang_play;
USE coupang_play;

-- 사용자 테이블 생성
CREATE TABLE user (
    user_id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_login DATETIME,
    is_active BOOLEAN DEFAULT TRUE
);

-- 콘텐츠 테이블 생성
CREATE TABLE content (
    content_id INT PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    release_date DATE,
    duration INT,
    genre VARCHAR(50),
    rating VARCHAR(10),
    view_count INT DEFAULT 0
);

-- 시청 기록 테이블 생성
CREATE TABLE view_history (
    view_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT,
    content_id INT,
    watch_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    watch_duration INT,
    FOREIGN KEY (user_id) REFERENCES user(user_id),
    FOREIGN KEY (content_id) REFERENCES content(content_id)
);

-- 구독 테이블 생성
CREATE TABLE subscription (
    subscription_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT,
    plan_name VARCHAR(50),
    start_date DATE,
    end_date DATE,
    is_active BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (user_id) REFERENCES user(user_id)
);

-- 결제 테이블 생성
CREATE TABLE payment (
    payment_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT,
    subscription_id INT,
    amount DECIMAL(10, 2),
    payment_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    payment_method VARCHAR(50),
    FOREIGN KEY (user_id) REFERENCES user(user_id),
    FOREIGN KEY (subscription_id) REFERENCES subscription(subscription_id)
);

-- 리뷰 테이블 생성
CREATE TABLE review (
    review_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT,
    content_id INT,
    rating INT CHECK (rating >= 1 AND rating <= 5),
    review_text TEXT,
    review_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user(user_id),
    FOREIGN KEY (content_id) REFERENCES content(content_id)
);

-- 인덱스 생성
CREATE INDEX idx_content_title ON content(title);
CREATE INDEX idx_view_history_user ON view_history(user_id);
CREATE INDEX idx_view_history_content ON view_history(content_id);
CREATE INDEX idx_subscription_user ON subscription(user_id);
CREATE INDEX idx_payment_user ON payment(user_id);
CREATE INDEX idx_review_content ON review(content_id);