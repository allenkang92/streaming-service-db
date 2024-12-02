from fastapi import FastAPI
from .api import auth, series, subscriptions
from .core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Streaming Service API"
)

# Include routers
app.include_router(auth.router, prefix="/api", tags=["auth"])
app.include_router(series.router, prefix="/api", tags=["series"])
app.include_router(subscriptions.router, prefix="/api", tags=["subscriptions"])

@app.get("/")
async def root():
    return {
        "message": "Welcome to Streaming Service API",
        "documentation": "/docs",
        "redoc": "/redoc"
    }

from fastapi import FastAPI, HTTPException, Depends
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import mysql.connector
from pymongo import MongoClient
from pydantic import BaseModel, Field
import os
import redis
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

# MySQL Connection
def get_mysql_connection():
    return mysql.connector.connect(
        host=os.getenv("MYSQL_HOST", "localhost"),
        port=int(os.getenv("MYSQL_PORT", 3306)),
        user=os.getenv("MYSQL_USER", "streaming_user"),
        password=os.getenv("MYSQL_PASSWORD", "userpassword"),
        database=os.getenv("MYSQL_DATABASE", "streaming_db")
    )

# MongoDB Schema Validation
viewing_logs_schema = {
    "bsonType": "object",
    "required": ["user_id", "episode_id", "timestamp", "action", "device_info"],
    "properties": {
        "user_id": {"bsonType": "int"},
        "episode_id": {"bsonType": "int"},
        "timestamp": {"bsonType": "date"},
        "action": {"enum": ["play", "pause", "stop", "seek"]},
        "device_info": {"bsonType": "object"},
        "streaming_quality": {"bsonType": "object"},
    }
}

user_behaviors_schema = {
    "bsonType": "object",
    "required": ["user_id", "action_type", "timestamp"],
    "properties": {
        "user_id": {"bsonType": "int"},
        "action_type": {"enum": ["search", "browse", "rate", "bookmark", "share"]},
        "timestamp": {"bsonType": "date"},
        "details": {"bsonType": "object"}
    }
}

performance_metrics_schema = {
    "bsonType": "object",
    "required": ["timestamp", "metric_type", "value"],
    "properties": {
        "timestamp": {"bsonType": "date"},
        "metric_type": {"enum": ["cdn_latency", "server_load", "streaming_quality", "error_rate"]},
        "value": {"bsonType": "double"},
        "details": {"bsonType": "object"}
    }
}

error_logs_schema = {
    "bsonType": "object",
    "required": ["timestamp", "error_type", "severity", "message"],
    "properties": {
        "timestamp": {"bsonType": "date"},
        "error_type": {"bsonType": "string"},
        "severity": {"enum": ["low", "medium", "high", "critical"]},
        "message": {"bsonType": "string"},
        "stack_trace": {"bsonType": "string"}
    }
}

# Database Connections
def get_mongo_client():
    client = MongoClient(os.getenv("MONGO_URI", "mongodb://root:rootpassword@localhost:27017/"))
    db = client.streaming_analytics
    
    # Create collections with schema validation if they don't exist
    if "viewing_logs" not in db.list_collection_names():
        db.create_collection("viewing_logs", validator={"$jsonSchema": viewing_logs_schema})
    
    if "user_behaviors" not in db.list_collection_names():
        db.create_collection("user_behaviors", validator={"$jsonSchema": user_behaviors_schema})
    
    if "performance_metrics" not in db.list_collection_names():
        db.create_collection("performance_metrics", validator={"$jsonSchema": performance_metrics_schema})
    
    if "error_logs" not in db.list_collection_names():
        db.create_collection("error_logs", validator={"$jsonSchema": error_logs_schema})
    
    return client

# Redis Connection
def get_redis():
    return redis.Redis(
        host=os.getenv("REDIS_HOST", "localhost"),
        port=int(os.getenv("REDIS_PORT", 6379)),
        decode_responses=True
    )

# Security
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# Models
class Series(BaseModel):
    title: str
    description: str
    release_year: int
    genre: str
    rating: str

class Episode(BaseModel):
    series_id: int
    season_number: int
    episode_number: int
    title: str
    duration: int
    description: str

class User(BaseModel):
    username: str
    email: str
    password: str

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class SubscriptionCreate(BaseModel):
    plan_type: str = Field(..., regex='^(basic|standard|premium)$')
    auto_renewal: bool = True

# Auth Functions
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception

    conn = get_mysql_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE username = %s", (token_data.username,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()

    if user is None:
        raise credentials_exception
    return user

# Series Endpoints
@app.get("/series")
async def get_series(
    skip: int = 0, 
    limit: int = 10,
    current_user: dict = Depends(get_current_user)
):
    conn = get_mysql_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM series LIMIT %s, %s", (skip, limit))
    series = cursor.fetchall()
    cursor.close()
    conn.close()
    return series

@app.post("/series")
async def create_series(series: Series):
    conn = get_mysql_connection()
    cursor = conn.cursor()
    query = """
    INSERT INTO series (title, description, release_year, genre, rating)
    VALUES (%s, %s, %s, %s, %s)
    """
    values = (series.title, series.description, series.release_year, 
              series.genre, series.rating)
    cursor.execute(query, values)
    conn.commit()
    series_id = cursor.lastrowid
    cursor.close()
    conn.close()
    return {"id": series_id, **series.dict()}

# Episodes Endpoints
@app.get("/series/{series_id}/episodes")
async def get_episodes(series_id: int):
    conn = get_mysql_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT e.*, s.season_number 
        FROM episodes e
        JOIN seasons s ON e.season_id = s.id
        WHERE s.series_id = %s
    """, (series_id,))
    episodes = cursor.fetchall()
    cursor.close()
    conn.close()
    return episodes

# Viewing Progress
@app.post("/viewing-progress")
async def update_viewing_progress(
    episode_id: int,
    progress: int,
    current_user: dict = Depends(get_current_user)
):
    # 구독 확인
    conn = get_mysql_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 1 FROM subscriptions 
        WHERE user_id = %s AND end_date > NOW()
    """, (current_user["id"],))
    
    if not cursor.fetchone():
        raise HTTPException(status_code=403, detail="Active subscription required")
    
    # 시청 진행률 업데이트
    query = """
    INSERT INTO viewing_progress (user_id, episode_id, progress, updated_at)
    VALUES (%s, %s, %s, NOW())
    ON DUPLICATE KEY UPDATE progress = %s, updated_at = NOW()
    """
    cursor.execute(query, (current_user["id"], episode_id, progress, progress))
    conn.commit()
    cursor.close()
    conn.close()

    # MongoDB에 로그 기록
    mongo_client = get_mongo_client()
    db = mongo_client.streaming_analytics
    db.viewing_logs.insert_one({
        "user_id": current_user["id"],
        "episode_id": episode_id,
        "progress": progress,
        "timestamp": datetime.now()
    })
    
    return {"status": "success"}

# User Behavior Analytics
@app.get("/analytics/user/{user_id}")
async def get_user_analytics(user_id: int):
    mongo_client = get_mongo_client()
    db = mongo_client.streaming_analytics
    
    viewing_history = list(db.viewing_logs.find(
        {"user_id": user_id},
        {"_id": 0}
    ).sort("timestamp", -1).limit(10))
    
    return viewing_history

# Redis를 활용한 새로운 엔드포인트들
@app.get("/trending")
async def get_trending_content():
    """인기 콘텐츠 목록 조회 (Redis 캐시 사용)"""
    r = get_redis()
    trending = r.zrevrange("trending_content", 0, 9, withscores=True)
    
    if not trending:
        # 캐시가 없으면 DB에서 조회하고 캐시 업데이트
        conn = get_mysql_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT s.id, s.title, COUNT(*) as view_count
            FROM viewing_progress vp
            JOIN episodes e ON vp.episode_id = e.id
            JOIN seasons se ON e.season_id = se.id
            JOIN series s ON se.series_id = s.id
            WHERE vp.last_watched >= DATE_SUB(NOW(), INTERVAL 24 HOUR)
            GROUP BY s.id
            ORDER BY view_count DESC
            LIMIT 10
        """)
        results = cursor.fetchall()
        cursor.close()
        conn.close()

        # Redis에 결과 캐싱
        for result in results:
            r.zadd("trending_content", {str(result["id"]): result["view_count"]})
        r.expire("trending_content", 3600)  # 1시간 후 만료
        
        return results
    
    return [{"id": int(id), "score": score} for id, score in trending]

@app.post("/viewing-session/start")
async def start_viewing_session(user_id: int, episode_id: int):
    """시청 세션 시작 (동시 시청 제한 관리)"""
    r = get_redis()
    session_key = f"viewing_session:{user_id}"
    
    # 현재 시청 중인 세션 확인
    current_sessions = r.scard(session_key)
    if current_sessions >= 2:  # 최대 2개 기기에서 동시 시청 가능
        raise HTTPException(status_code=400, detail="Maximum concurrent viewing sessions reached")
    
    # 새로운 세션 추가
    session_id = f"{user_id}:{episode_id}:{datetime.now().timestamp()}"
    r.sadd(session_key, session_id)
    r.expire(session_key, 4 * 3600)  # 4시간 후 만료
    
    return {"session_id": session_id}

@app.post("/viewing-session/end")
async def end_viewing_session(user_id: int, session_id: str):
    """시청 세션 종료"""
    r = get_redis()
    session_key = f"viewing_session:{user_id}"
    r.srem(session_key, session_id)
    return {"status": "success"}

# Subscription Endpoints
@app.post("/subscriptions")
async def create_subscription(
    subscription: SubscriptionCreate,
    current_user: dict = Depends(get_current_user)
):
    conn = get_mysql_connection()
    cursor = conn.cursor()
    
    # 현재 활성 구독이 있는지 확인
    cursor.execute(
        "SELECT id FROM subscriptions WHERE user_id = %s AND end_date > NOW()",
        (current_user["id"],)
    )
    if cursor.fetchone():
        raise HTTPException(status_code=400, detail="Active subscription already exists")
    
    # 새 구독 생성
    start_date = datetime.now()
    end_date = start_date + timedelta(days=30)  # 30일 구독
    
    cursor.execute("""
        INSERT INTO subscriptions 
        (user_id, plan_type, start_date, end_date, auto_renewal)
        VALUES (%s, %s, %s, %s, %s)
    """, (current_user["id"], subscription.plan_type, start_date, end_date, subscription.auto_renewal))
    
    conn.commit()
    cursor.close()
    conn.close()
    
    return {"message": "Subscription created successfully"}

@app.get("/subscriptions/current")
async def get_current_subscription(current_user: dict = Depends(get_current_user)):
    conn = get_mysql_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT * FROM subscriptions 
        WHERE user_id = %s AND end_date > NOW()
        ORDER BY end_date DESC LIMIT 1
    """, (current_user["id"],))
    
    subscription = cursor.fetchone()
    cursor.close()
    conn.close()
    
    if not subscription:
        raise HTTPException(status_code=404, detail="No active subscription found")
    
    return subscription

@app.post("/subscriptions/cancel")
async def cancel_subscription(current_user: dict = Depends(get_current_user)):
    conn = get_mysql_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        UPDATE subscriptions 
        SET auto_renewal = FALSE
        WHERE user_id = %s AND end_date > NOW()
    """, (current_user["id"],))
    
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="No active subscription found")
    
    conn.commit()
    cursor.close()
    conn.close()
    
    return {"message": "Subscription auto-renewal cancelled"}

# Auth Endpoints
@app.post("/register", response_model=Token)
async def register_user(user: UserCreate):
    conn = get_mysql_connection()
    cursor = conn.cursor()
    
    # 이메일 중복 체크
    cursor.execute("SELECT id FROM users WHERE email = %s", (user.email,))
    if cursor.fetchone():
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # 사용자 생성
    hashed_password = get_password_hash(user.password)
    cursor.execute(
        "INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)",
        (user.username, user.email, hashed_password)
    )
    conn.commit()
    cursor.close()
    conn.close()
    
    # 토큰 생성
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/login", response_model=Token)
async def login(username: str, password: str):
    conn = get_mysql_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    
    if not user or not verify_password(password, user["password_hash"]):
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": username})
    return {"access_token": access_token, "token_type": "bearer"}

# Protected Endpoint Example
@app.get("/users/me")
async def read_users_me(current_user: dict = Depends(get_current_user)):
    return current_user
