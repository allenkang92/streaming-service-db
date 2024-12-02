-- 데이터베이스 생성
CREATE DATABASE coupang_play;
USE coupang_play;

-- -----------------------------------------------------
-- 핵심 테이블 영역 시작
-- -----------------------------------------------------

-- 사용자 테이블
-- 기본적인 사용자 정보와 인증 관련 데이터 저장
-- JSON 타입을 활용해 유연한 사용자 설정 저장
CREATE TABLE user (
    user_id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL COMMENT '해시된 비밀번호',
    password_salt VARCHAR(255) NOT NULL COMMENT '비밀번호 솔트',
    two_factor_enabled BOOLEAN DEFAULT FALSE,
    two_factor_secret VARCHAR(255),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_login DATETIME,
    is_active BOOLEAN DEFAULT TRUE,
    profile_preferences JSON COMMENT '사용자 설정 및 선호도 (자막, 화질 등)',
    failed_login_attempts INT DEFAULT 0,
    account_locked_until DATETIME
) COMMENT '사용자 기본 정보 테이블';

-- 시리즈 테이블
-- TV 프로그램, 시리즈물 등의 정보 저장
CREATE TABLE series (
    series_id INT PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    release_date DATE,
    total_episodes INT,
    status ENUM('ongoing', 'completed', 'upcoming') DEFAULT 'ongoing'
) COMMENT '시리즈 정보 테이블';

-- 장르 테이블
-- 콘텐츠 분류를 위한 장르 정보
CREATE TABLE genre (
    genre_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT
) COMMENT '장르 마스터 테이블';

-- 콘텐츠 테이블
-- 영화, 에피소드 등 실제 재생 가능한 콘텐츠 정보
CREATE TABLE content (
    content_id INT PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    release_date DATE,
    duration INT COMMENT '콘텐츠 길이(초)',
    rating VARCHAR(10) COMMENT '시청 등급',
    view_count INT DEFAULT 0,
    license_info JSON COMMENT '라이선스 정보 (시작일, 종료일, 조건 등)',
    region_restrictions JSON COMMENT '지역별 시청 제한 정보',
    metadata JSON COMMENT '배우, 감독, 제작사 등 추가 정보',
    video_quality JSON COMMENT '지원되는 해상도 및 비트레이트 정보',
    audio_tracks JSON COMMENT '지원되는 오디오 트랙 정보',
    subtitle_tracks JSON COMMENT '지원되는 자막 정보',
    content_hash VARCHAR(255) COMMENT '콘텐츠 무결성 검증용 해시',
    cdn_info JSON COMMENT 'CDN 배포 정보',
    encryption_info JSON COMMENT 'DRM 및 암호화 정보'
) COMMENT '콘텐츠 기본 정보 테이블';

-- 다국어 지원을 위한 테이블 추가
CREATE TABLE content_translations (
    translation_id INT PRIMARY KEY AUTO_INCREMENT,
    content_id INT,
    language_code VARCHAR(5),
    title VARCHAR(255),
    description TEXT,
    metadata JSON COMMENT '해당 언어의 메타데이터',
    UNIQUE KEY unique_content_lang (content_id, language_code),
    FOREIGN KEY (content_id) REFERENCES content(content_id) ON DELETE CASCADE
) COMMENT '콘텐츠 다국어 정보 테이블';

-- 추천 시스템을 위한 테이블 추가
CREATE TABLE content_similarity (
    content_id1 INT,
    content_id2 INT,
    similarity_score FLOAT,
    similarity_factors JSON COMMENT '유사도 계산 요소들',
    last_updated DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (content_id1, content_id2),
    FOREIGN KEY (content_id1) REFERENCES content(content_id) ON DELETE CASCADE,
    FOREIGN KEY (content_id2) REFERENCES content(content_id) ON DELETE CASCADE
) COMMENT '콘텐츠 간 유사도 정보 테이블';

CREATE TABLE user_preferences (
    user_id INT PRIMARY KEY,
    genre_preferences JSON COMMENT '선호 장르 가중치',
    watch_history_summary JSON COMMENT '시청 이력 요약 정보',
    recommendation_feedback JSON COMMENT '추천 피드백 정보',
    last_updated DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user(user_id) ON DELETE CASCADE
) COMMENT '사용자 선호도 분석 테이블';

-- -----------------------------------------------------
-- 관계 테이블 영역 시작
-- -----------------------------------------------------

-- 콘텐츠-시리즈 관계 테이블
-- 시리즈물의 에피소드 정보 관리
CREATE TABLE content_series (
    content_id INT,
    series_id INT,
    episode_number INT,
    PRIMARY KEY (content_id, series_id),
    FOREIGN KEY (content_id) REFERENCES content(content_id) ON DELETE CASCADE,
    FOREIGN KEY (series_id) REFERENCES series(series_id) ON DELETE CASCADE
) COMMENT '시리즈와 에피소드 매핑 테이블';

-- 콘텐츠-장르 관계 테이블
-- 하나의 콘텐츠가 여러 장르에 속할 수 있음
CREATE TABLE content_genre (
    content_id INT,
    genre_id INT,
    PRIMARY KEY (content_id, genre_id),
    FOREIGN KEY (content_id) REFERENCES content(content_id) ON DELETE CASCADE,
    FOREIGN KEY (genre_id) REFERENCES genre(genre_id) ON DELETE CASCADE
) COMMENT '콘텐츠와 장르 매핑 테이블';

-- -----------------------------------------------------
-- 활동 기록 테이블 영역 시작
-- -----------------------------------------------------

-- 시청 기록 테이블
-- 실제 운영에서는 최근 데이터만 보관, 오래된 데이터는 아카이브 처리
CREATE TABLE view_history (
    view_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT,
    content_id INT,
    watch_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    watch_duration INT COMMENT '시청 시간(초)',
    watch_progress FLOAT COMMENT '시청 진행률 (0-100%)',
    device_info JSON COMMENT '시청 디바이스 정보',
    FOREIGN KEY (user_id) REFERENCES user(user_id) ON DELETE CASCADE,
    FOREIGN KEY (content_id) REFERENCES content(content_id) ON DELETE CASCADE
) COMMENT '최근 시청 기록 테이블';

-- 시청 기록 아카이브 테이블
-- 오래된 시청 기록 저장용 (예: 1년 이상 된 데이터)
CREATE TABLE view_history_archive (
    view_id INT PRIMARY KEY,
    user_id INT,
    content_id INT,
    watch_date DATETIME,
    watch_duration INT,
    watch_progress FLOAT,
    device_info JSON,
    archived_at DATETIME DEFAULT CURRENT_TIMESTAMP
) COMMENT '과거 시청 기록 보관 테이블';

-- -----------------------------------------------------
-- 구독 및 결제 영역 시작
-- -----------------------------------------------------

-- 구독 테이블
CREATE TABLE subscription (
    subscription_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT,
    plan_name VARCHAR(50),
    price DECIMAL(10, 2),
    start_date DATE,
    end_date DATE,
    is_active BOOLEAN DEFAULT TRUE,
    auto_renewal BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (user_id) REFERENCES user(user_id)
) COMMENT '구독 정보 테이블';

-- 결제 테이블
-- 실제 운영에서는 결제 정보를 별도 시스템이나 외부 서비스로 관리하는 것을 권장
CREATE TABLE payment (
    payment_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT,
    subscription_id INT,
    amount DECIMAL(10, 2),
    payment_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    payment_method VARCHAR(50),
    payment_status ENUM('pending', 'completed', 'failed', 'refunded') DEFAULT 'pending',
    FOREIGN KEY (user_id) REFERENCES user(user_id),
    FOREIGN KEY (subscription_id) REFERENCES subscription(subscription_id)
) COMMENT '결제 내역 테이블';

-- 결제 기록 아카이브 테이블
CREATE TABLE payment_archive (
    payment_id INT PRIMARY KEY,
    user_id INT,
    subscription_id INT,
    amount DECIMAL(10, 2),
    payment_date DATETIME,
    payment_method VARCHAR(50),
    payment_status VARCHAR(20),
    archived_at DATETIME DEFAULT CURRENT_TIMESTAMP
) COMMENT '과거 결제 내역 보관 테이블';

-- -----------------------------------------------------
-- 사용자 활동 영역 시작
-- -----------------------------------------------------

-- 리뷰 테이블
CREATE TABLE review (
    review_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT,
    content_id INT,
    rating INT CHECK (rating >= 1 AND rating <= 5),
    review_text TEXT,
    review_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    likes_count INT DEFAULT 0,
    is_spoiler BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (user_id) REFERENCES user(user_id) ON DELETE CASCADE,
    FOREIGN KEY (content_id) REFERENCES content(content_id) ON DELETE CASCADE
) COMMENT '콘텐츠 리뷰 테이블';

-- 세션 관리 테이블
-- 동시 접속 제한, 보안 관리 등에 사용
CREATE TABLE user_session (
    session_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT,
    session_token VARCHAR(255) UNIQUE NOT NULL,
    device_info JSON,
    login_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    expire_time DATETIME,
    is_active BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (user_id) REFERENCES user(user_id) ON DELETE CASCADE
) COMMENT '사용자 세션 관리 테이블';

-- 감사 로그 테이블
-- 중요 데이터 변경 이력 추적
CREATE TABLE audit_log (
    audit_id INT PRIMARY KEY AUTO_INCREMENT,
    table_name VARCHAR(50) NOT NULL,
    record_id INT NOT NULL,
    action_type ENUM('INSERT', 'UPDATE', 'DELETE') NOT NULL,
    action_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    action_user INT,
    old_value JSON COMMENT '변경 전 데이터',
    new_value JSON COMMENT '변경 후 데이터',
    FOREIGN KEY (action_user) REFERENCES user(user_id)
) COMMENT '데이터 변경 이력 추적 테이블';

-- -----------------------------------------------------
-- 인덱스 생성
-- -----------------------------------------------------

-- 콘텐츠 검색 최적화
CREATE INDEX idx_content_title ON content(title);
CREATE INDEX idx_series_title ON series(title);

-- 시청 기록 조회 최적화
CREATE INDEX idx_view_history_user ON view_history(user_id, watch_date);
CREATE INDEX idx_view_history_content ON view_history(content_id);

-- 구독 및 결제 조회 최적화
CREATE INDEX idx_subscription_user ON subscription(user_id, is_active);
CREATE INDEX idx_payment_user ON payment(user_id, payment_date);

-- 리뷰 조회 최적화
CREATE INDEX idx_review_content ON review(content_id, rating);
CREATE INDEX idx_session_user ON user_session(user_id, is_active);

-- 성능 최적화를 위한 인덱스 추가
CREATE INDEX idx_content_popularity ON content(view_count DESC, release_date DESC);
CREATE INDEX idx_content_metadata ON content((JSON_EXTRACT(metadata, '$.genre')));
CREATE INDEX idx_view_history_user_date ON view_history(user_id, watch_date);
CREATE INDEX idx_content_translations_lang ON content_translations(language_code, content_id);

-- -----------------------------------------------------
-- 분석용 뷰 생성
-- -----------------------------------------------------

-- 콘텐츠 인기도 분석 뷰
CREATE VIEW content_popularity AS
SELECT 
    c.content_id,
    c.title,
    COUNT(DISTINCT vh.user_id) as unique_viewers,
    AVG(vh.watch_duration) as avg_watch_duration,
    COUNT(r.review_id) as review_count,
    AVG(r.rating) as avg_rating
FROM content c
LEFT JOIN view_history vh ON c.content_id = vh.content_id
LEFT JOIN review r ON c.content_id = r.content_id
GROUP BY c.content_id, c.title;

-- 사용자 참여도 분석 뷰
CREATE VIEW user_engagement AS
SELECT 
    u.user_id,
    u.username,
    COUNT(vh.view_id) as total_views,
    SUM(vh.watch_duration) as total_watch_time,
    COUNT(r.review_id) as review_count,
    DATEDIFF(NOW(), u.created_at) as days_since_signup
FROM user u
LEFT JOIN view_history vh ON u.user_id = vh.user_id
LEFT JOIN review r ON u.user_id = r.user_id
GROUP BY u.user_id, u.username, u.created_at;

-- 구독 지표 분석 뷰
CREATE VIEW subscription_metrics AS
SELECT 
    plan_name,
    COUNT(*) as total_subscriptions,
    COUNT(CASE WHEN is_active = 1 THEN 1 END) as active_subscriptions,
    AVG(CASE WHEN is_active = 1 THEN price END) as avg_active_price
FROM subscription
GROUP BY plan_name;

-- -----------------------------------------------------
-- 데이터 아카이빙을 위한 저장 프로시저 예시
-- -----------------------------------------------------

DELIMITER //

CREATE PROCEDURE archive_old_views()
BEGIN
    -- 1년 이상 된 시청 기록을 아카이브
    INSERT INTO view_history_archive 
    SELECT *, NOW() as archived_at
    FROM view_history 
    WHERE watch_date < DATE_SUB(NOW(), INTERVAL 1 YEAR);
    
    -- 아카이브된 데이터 삭제
    DELETE FROM view_history 
    WHERE watch_date < DATE_SUB(NOW(), INTERVAL 1 YEAR);
END //

DELIMITER ;

-- 캐싱을 위한 테이블 추가
CREATE TABLE content_cache (
    cache_key VARCHAR(255) PRIMARY KEY,
    content_data JSON,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    expires_at DATETIME,
    last_accessed DATETIME,
    access_count INT DEFAULT 0
) COMMENT '콘텐츠 캐시 테이블';
