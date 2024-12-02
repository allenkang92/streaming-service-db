# 스트리밍 서비스 데이터베이스 설계 프로젝트 (쿠팡 플레이)

## 프로젝트 개요

쿠팡 플레이와 같은 대규모 스트리밍 서비스를 위한 확장 가능하고 안전한 데이터베이스 시스템을 설계하고 구현하고자 합니다.
보안 표준을 준수하면서 효율적인 콘텐츠 전송과 개인화된 사용자 경험을 제공하고자 합니다.

### 핵심 목표
- 대규모 동시 접속 처리를 위한 확장 가능한 아키텍처
- 실시간 데이터 처리 및 분석
- 효율적인 콘텐츠 전송 및 캐싱 전략

## 기술 스택

### 데이터베이스
- MySQL 8.0: 사용자, 구독, 시리즈 등 구조화된 데이터 저장
- Redis 6.2: 캐싱, 세션 관리, 실시간 데이터 처리
- MongoDB: 시청 기록, 분석 데이터 저장

### 백엔드
- FastAPI: 고성능 Python 웹 프레임워크
- JWT: 토큰 기반 인증
- Pydantic: 데이터 검증

### 인프라
- Docker: 컨테이너화
- Docker Compose: 서비스 오케스트레이션

### 모니터링 (구현 예정)
- Prometheus: 메트릭 수집
- Grafana: 대시보드

## 프로젝트 구조

```
streaming-service-db/
├── app/                    # 애플리케이션 메인 디렉터리
│   ├── api/               # API 엔드포인트
│   │   ├── __init__.py
│   │   ├── auth.py       # 인증 관련 엔드포인트
│   │   ├── series.py     # 시리즈/에피소드 관리
│   │   └── subscriptions.py  # 구독 관리
│   ├── core/             # 핵심 기능
│   │   ├── __init__.py
│   │   ├── config.py     # 애플리케이션 설정
│   │   ├── security.py   # 보안 유틸리티
│   │   └── database.py   # 데이터베이스 연결
│   ├── models/           # 데이터 모델
│   │   ├── __init__.py
│   │   └── schemas.py    # Pydantic 모델
│   ├── main.py          # FastAPI 애플리케이션
│   ├── requirements.txt  # 프로젝트 의존성
│   └── Dockerfile       # API 서비스 Dockerfile
├── db/                   # 데이터베이스 관련 파일
│   ├── mysql/
│   │   └── schema.sql   # MySQL 스키마
│   └── mongodb/
│       └── init-mongo.js # MongoDB 초기화
├── docs/                 # 문서
│   └── project_plan.md  # 프로젝트 문서
└── docker-compose.yml   # Docker 서비스 설정
```

## 주요 기능

### 1. 사용자 관리 및 보안 (구현 완료)
- JWT 토큰 기반 인증
- 비밀번호 해싱 (bcrypt)
- 세션 관리
- 접근 제어

### 2. 콘텐츠 관리 (구현 완료)
- 시리즈 및 에피소드 관리
- 시청 진행률 추적
- 메타데이터 관리
- 구독 기반 접근 제어

### 3. 구독 관리 (구현 완료)
- 구독 생성 및 취소
- 구독 상태 확인
- 구독 기간 관리

### 4. 개인화 및 추천 (미구현)
- 협업 필터링 기반 추천
- 시청 기록 기반 개인화
- 인기 콘텐츠 추천

## API 엔드포인트

### 인증
- `POST /api/register`: 새 사용자 등록
- `POST /api/token`: 로그인 및 토큰 발급

### 시리즈
- `GET /api/series`: 시리즈 목록 조회
- `GET /api/series/{series_id}`: 특정 시리즈 조회
- `GET /api/series/{series_id}/episodes`: 시리즈의 에피소드 목록 조회
- `POST /api/series/{series_id}/progress`: 시청 진행률 업데이트

### 구독
- `POST /api/subscriptions`: 새 구독 생성
- `GET /api/subscriptions/current`: 현재 구독 정보 조회
- `DELETE /api/subscriptions/current`: 현재 구독 취소

## 데이터베이스 설계

### MySQL 테이블
```sql
-- 사용자 테이블
CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    email VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 구독 테이블
CREATE TABLE subscriptions (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    plan_id INT NOT NULL,
    start_date TIMESTAMP NOT NULL,
    end_date TIMESTAMP NOT NULL,
    status VARCHAR(20) NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- 시리즈 테이블
CREATE TABLE series (
    id INT PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    release_year INT,
    genre VARCHAR(50),
    rating VARCHAR(10)
);
```

### MongoDB 컬렉션
- ViewingLogs: 시청 기록
- Analytics: 사용자 행동 및 선호도

### Redis
- 시청 진행률 캐싱
- 세션 관리
- 인기 콘텐츠

## 설치 및 실행

1. 저장소 복제:
   ```bash
   git clone https://github.com/yourusername/streaming-service-db.git
   cd streaming-service-db
   ```

2. 환경 파일 생성:
   ```bash
   # .env 파일을 프로젝트 루트에 생성
   MYSQL_HOST=mysql
   MYSQL_PORT=3306
   MYSQL_USER=streaming_user
   MYSQL_PASSWORD=userpassword
   MYSQL_DATABASE=streaming_db
   MONGO_URI=mongodb://root:rootpassword@mongodb:27017/
   REDIS_HOST=redis
   REDIS_PORT=6379
   SECRET_KEY=your-secret-key-here
   ```

3. 서비스 시작:
   ```bash
   docker-compose up --build
   ```

4. API 접속:
   - API 문서: http://localhost:8000/docs
   - ReDoc 문서: http://localhost:8000/redoc

## 실행해보기

1. 의존성 설치:
   ```bash
   pip install -r app/requirements.txt
   ```

2. 테스트 실행:
   ```bash
   pytest
   ```

3. 코드 포맷팅:
   ```bash
   black app/
   ```

