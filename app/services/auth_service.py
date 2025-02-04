from fastapi import HTTPException , Depends
from app.core.config import settings
from app.db.models import users_collection
from passlib.context import CryptContext
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer
import jwt

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = settings.JWT_SECRET
ALGORITHM = settings.ALGORITHM

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def register_user(user_data):
    existing_user = users_collection.find_one({"username": user_data.username})
    if existing_user:
        raise HTTPException(status_code=409, detail="User already exists")  # Use HTTPException
    hashed_password = get_password_hash(user_data.password)
    user_id = users_collection.insert_one({
        "username": user_data.username,
        "password": hashed_password
    }).inserted_id
    return {"message": "User registered successfully", "user_id": str(user_id)}

def authenticate_user(user_data):
    db_user = users_collection.find_one({"username": user_data.username})
    if not db_user or not verify_password(user_data.password, db_user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")  # Use HTTPException
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(data={"sub": user_data.username}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return username
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")