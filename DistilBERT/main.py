import os
import jwt
import bcrypt
from datetime import datetime, timedelta
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from transformers import pipeline
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base, Session

# --- 1. إعداد قاعدة البيانات (SQLite) ---
DATABASE_URL = "sqlite:///./users.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- 2. إعدادات الأمان والتشفير ---
SECRET_KEY = "super_secret_key_for_my_api" 
ALGORITHM = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def verify_password(plain_password: str, hashed_password: str):
    # استخدام bcrypt مباشرة للمقارنة
    password_bytes = plain_password.encode('utf-8')
    hashed_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hashed_bytes)

def get_password_hash(password: str):
    # استخدام bcrypt مباشرة للتشفير
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=30) # التوكن صالح لمدة نص ساعة
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user

# --- 3. إعداد الذكاء الاصطناعي ---
app = FastAPI(title="Emotion Detection API (Secured)")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.normpath(os.path.join(BASE_DIR, "distilbert_emotion_model"))

print(f"Loading model from: {MODEL_DIR}")
try:
    classifier = pipeline("text-classification", model=MODEL_DIR, tokenizer=MODEL_DIR)
    print("Model loaded successfully!")
except Exception as e:
    print(f"Failed to load model: {e}")

EMOTION_MAPPING = {
    "LABEL_0": "Sadness 😢", "LABEL_1": "Joy 😃",
    "LABEL_2": "Love 🥰", "LABEL_3": "Anger 😠",
    "LABEL_4": "Fear 😨", "LABEL_5": "Surprise 😲"
}

# --- 4. المسارات (Endpoints) ---
class UserCreate(BaseModel):
    username: str
    password: str

@app.post("/register", tags=["Authentication"])
def register(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    hashed_password = get_password_hash(user.password)
    new_user = User(username=user.username, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    return {"message": "User created successfully!"}

@app.post("/login", tags=["Authentication"])
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

class TextRequest(BaseModel):
    text: str

@app.post("/ml/classify", tags=["AI Prediction"])
def classify_text(request: TextRequest, current_user: User = Depends(get_current_user)):
    prediction = classifier(request.text)
    original_label = prediction[0]['label']
    score = prediction[0]['score']
    readable_label = EMOTION_MAPPING.get(original_label, original_label)
    
    return {
        "User": current_user.username,
        "Category": readable_label, 
        "Confidence": score
    }