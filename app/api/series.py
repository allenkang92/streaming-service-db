from fastapi import APIRouter, Depends, HTTPException, status
from ..core.database import get_mongodb_db, get_redis_client
from ..core.security import get_current_user
from ..models.schemas import Series, Episode, ViewingProgress

router = APIRouter()

@router.get("/series", response_model=list[Series])
async def get_series(skip: int = 0, limit: int = 10):
    db = get_mongodb_db()
    series_list = list(db.series.find({}).skip(skip).limit(limit))
    return series_list

@router.get("/series/{series_id}", response_model=Series)
async def get_series_by_id(series_id: str):
    db = get_mongodb_db()
    series = db.series.find_one({"_id": series_id})
    if not series:
        raise HTTPException(status_code=404, detail="Series not found")
    return series

@router.get("/series/{series_id}/episodes", response_model=list[Episode])
async def get_episodes(series_id: str):
    db = get_mongodb_db()
    episodes = list(db.episodes.find({"series_id": series_id}))
    if not episodes:
        raise HTTPException(status_code=404, detail="Episodes not found")
    return episodes

@router.post("/series/{series_id}/progress")
async def update_viewing_progress(
    series_id: str,
    episode_id: str,
    progress: ViewingProgress,
    current_user = Depends(get_current_user)
):
    db = get_mongodb_db()
    redis = get_redis_client()
    
    # Update viewing progress in MongoDB
    result = db.viewing_progress.update_one(
        {
            "user_id": current_user["id"],
            "series_id": series_id,
            "episode_id": episode_id
        },
        {"$set": {"progress": progress.dict()}},
        upsert=True
    )
    
    # Cache recent viewing progress in Redis
    redis.setex(
        f"viewing_progress:{current_user['id']}:{series_id}:{episode_id}",
        3600,  # expire in 1 hour
        progress.json()
    )
    
    return {"status": "success"}
