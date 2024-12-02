from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from ..core.security import create_access_token, get_password_hash, verify_password
from ..core.database import get_mysql_db
from ..models.schemas import UserCreate, UserInDB, Token

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@router.post("/register", response_model=Token)
async def register(user: UserCreate):
    db = get_mysql_db()
    cursor = db.cursor(dictionary=True)
    
    # Check if user exists
    cursor.execute("SELECT * FROM users WHERE email = %s", (user.email,))
    if cursor.fetchone():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    hashed_password = get_password_hash(user.password)
    cursor.execute(
        "INSERT INTO users (email, hashed_password) VALUES (%s, %s)",
        (user.email, hashed_password)
    )
    db.commit()
    
    # Create access token
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    db = get_mysql_db()
    cursor = db.cursor(dictionary=True)
    
    cursor.execute("SELECT * FROM users WHERE email = %s", (form_data.username,))
    user = cursor.fetchone()
    
    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": user["email"]})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/users/me")
async def read_users_me(current_user: dict = Depends(get_current_user)):
    return current_user
