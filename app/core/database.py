import mysql.connector
from pymongo import MongoClient
import redis
from .config import settings

def get_mysql_connection():
    return mysql.connector.connect(
        host=settings.MYSQL_HOST,
        port=settings.MYSQL_PORT,
        user=settings.MYSQL_USER,
        password=settings.MYSQL_PASSWORD,
        database=settings.MYSQL_DATABASE
    )

def get_mongo_client():
    return MongoClient(settings.MONGO_URI)

def get_redis():
    return redis.Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        decode_responses=True
    )
