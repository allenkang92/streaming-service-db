from fastapi import APIRouter, Depends, HTTPException, status
from datetime import datetime, timedelta
from ..core.database import get_mysql_db
from ..core.security import get_current_user
from ..models.schemas import Subscription, SubscriptionCreate

router = APIRouter()

@router.post("/subscriptions", response_model=Subscription)
async def create_subscription(
    subscription: SubscriptionCreate,
    current_user = Depends(get_current_user)
):
    db = get_mysql_db()
    cursor = db.cursor(dictionary=True)
    
    # Check if user already has an active subscription
    cursor.execute(
        "SELECT * FROM subscriptions WHERE user_id = %s AND end_date > NOW()",
        (current_user["id"],)
    )
    if cursor.fetchone():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already has an active subscription"
        )
    
    # Create new subscription
    start_date = datetime.now()
    end_date = start_date + timedelta(days=30)  # 30-day subscription
    
    cursor.execute(
        """
        INSERT INTO subscriptions 
        (user_id, plan_id, start_date, end_date, status)
        VALUES (%s, %s, %s, %s, 'active')
        """,
        (current_user["id"], subscription.plan_id, start_date, end_date)
    )
    db.commit()
    
    subscription_id = cursor.lastrowid
    return {
        "id": subscription_id,
        "user_id": current_user["id"],
        "plan_id": subscription.plan_id,
        "start_date": start_date,
        "end_date": end_date,
        "status": "active"
    }

@router.get("/subscriptions/current", response_model=Subscription)
async def get_current_subscription(current_user = Depends(get_current_user)):
    db = get_mysql_db()
    cursor = db.cursor(dictionary=True)
    
    cursor.execute(
        """
        SELECT * FROM subscriptions 
        WHERE user_id = %s AND end_date > NOW()
        ORDER BY end_date DESC LIMIT 1
        """,
        (current_user["id"],)
    )
    
    subscription = cursor.fetchone()
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active subscription found"
        )
    
    return subscription

@router.delete("/subscriptions/current")
async def cancel_subscription(current_user = Depends(get_current_user)):
    db = get_mysql_db()
    cursor = db.cursor()
    
    cursor.execute(
        """
        UPDATE subscriptions 
        SET status = 'cancelled', end_date = NOW()
        WHERE user_id = %s AND status = 'active'
        """,
        (current_user["id"],)
    )
    db.commit()
    
    if cursor.rowcount == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active subscription found"
        )
    
    return {"status": "success", "message": "Subscription cancelled"}
