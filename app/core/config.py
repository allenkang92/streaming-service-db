import os

class Settings:
    PROJECT_NAME = "스트리밍 서비스 API"
    VERSION = "1.0.0"
    
    # Security
    SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30
    
    # Database
    MYSQL_HOST = os.getenv("MYSQL_HOST", "mysql")
    MYSQL_PORT = int(os.getenv("MYSQL_PORT", 3306))
    MYSQL_USER = os.getenv("MYSQL_USER", "streaming_user")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "userpassword")
    MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "streaming_db")
    
    # MongoDB
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://root:rootpassword@mongodb:27017/")
    
    # Redis
    REDIS_HOST = os.getenv("REDIS_HOST", "redis")
    REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

settings = Settings()
