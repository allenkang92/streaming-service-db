# 쿠팡 플레이 데이터베이스 설계 프로젝트

이 프로젝트는 쿠팡 플레이와 유사한 스트리밍 서비스의 데이터베이스를 설계하고 구현하는 것을 목표로 합니다.

## 프로젝트 구조

```
coupang-play-db-project/
│
├── docs/
│   └── project_plan.md
│
├── sql/
│   └── create_database.sql
│
└── README.md
```

## 주요 기능

- 사용자 관리
- 콘텐츠 관리
- 시청 기록 추적
- 구독 및 결제 관리
- 리뷰 및 평점 시스템

## 기술 스택

- 데이터베이스: MySQL 8.0
- 버전 관리: Git

## 설치 및 실행 방법

1. 이 저장소를 클론합니다.
   ```
   git clone https://github.com/your-username/coupang-play-db-project.git
   ```

2. MySQL 서버에 접속합니다.

3. `sql/create_database.sql` 파일을 실행하여 데이터베이스와 테이블을 생성합니다.
   ```
   mysql -u your_username -p < sql/create_database.sql
   ```

## 프로젝트 문서

자세한 프로젝트 계획 및 설계 문서는 `docs/project_plan.md` 파일을 확인해주세요.
