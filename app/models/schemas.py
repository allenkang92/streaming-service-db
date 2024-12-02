from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

# Auth Models
class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

# Content Models
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

# Subscription Models
class SubscriptionCreate(BaseModel):
    plan_type: str = Field(..., regex='^(basic|standard|premium)$')
    auto_renewal: bool = True

# MongoDB Schemas
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
