# 쿠팡 플레이 데이터베이스 설계 프로젝트

## 프로젝트 개요

쿠팡 플레이와 같은 대규모 스트리밍 서비스의 데이터베이스를 설계하고 구현하는 것을 목표로 합니다. 
사용자 경험 최적화와 효율적인 콘텐츠 관리를 위한 확장 가능한 데이터베이스 구조를 제공하고자 합니다.

## 주요 기능

### 핵심 기능
- 사용자 계정 및 프로필 관리
- 콘텐츠 **메타데이터 관리** (시리즈/에피소드 포함)
- 시청 기록 추적 및 분석
- 구독 및 결제 관리
- 리뷰 및 평점 시스템

### 고급 기능
- 시리즈/에피소드 관계 관리
- 다중 장르 지원
- 콘텐츠 라이선스 및 지역 제한 관리
- 사용자 활동 감사(Audit) 추적
- 성능 모니터링 및 분석

## 데이터베이스 구조

### 핵심 테이블
```sql
- user (사용자 정보)
- content (콘텐츠 정보)
- series (시리즈 정보)
- genre (장르 정보)
- view_history (시청 기록)
- subscription (구독 정보)
- payment (결제 정보)
- review (리뷰 정보)
```

### 보조 테이블
```sql
- content_series (시리즈-에피소드 관계)
- content_genre (콘텐츠-장르 관계)
- audit_log (변경 이력 추적)
```

## 성능 최적화

### 인덱싱 전략
- 자주 조회되는 컬럼에 대한 인덱스 생성
- 조인 성능 향상을 위한 외래키 인덱싱
- 복합 인덱스를 통한 쿼리 최적화

### 성능 개선 방안
- 시청 기록 테이블 파티셔닝
- 자주 사용되는 쿼리를 위한 materialized view
- 시계열 데이터 아카이빙 전략



## 설치 및 설정

1. 저장소 클론
```bash
git clone https://github.com/your-username/coupang-play-db-project.git
```

2. MySQL 8.0 설치 (필요한 경우)
```bash
# Ubuntu
sudo apt-get install mysql-server

# macOS
brew install mysql@8.0
```

3. 데이터베이스 생성
```bash
mysql -u root -p < sql/create_database.sql
```

4. 초기 데이터 로드 (선택사항)
```bash
mysql -u root -p coupang_play < sql/sample_data.sql
```

## 모니터링 및 분석

### 주요 지표
- 동시 접속자 수
- 콘텐츠별 시청 시간
- 구독 갱신율
- 사용자당 평균 시청 시간

### 분석용 뷰
- content_popularity (콘텐츠 인기도 분석)
- user_engagement (사용자 참여도 분석)
- subscription_metrics (구독 지표 분석)

## 향후 계획
0. 보안 기능

- 사용자 정보 암호화
- 결제 정보 분리 저장
- 접근 권한 관리
- 변경 이력 추적 시스템

1. 단기 목표
- 시리즈/에피소드 관리 시스템 고도화
- 메타데이터 관리 기능 확장
- 성능 모니터링 시스템 구축

2. 장기 목표
- NoSQL 데이터베이스 통합
- 머신러닝 기반 추천 시스템 도입
- 실시간 데이터 처리 시스템 구축

