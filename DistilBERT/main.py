import os
import jwt
import bcrypt
import uuid
from datetime import datetime, timedelta
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from transformers import pipeline
from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from peft import PeftModel
from transformers import AutoModelForSequenceClassification, AutoTokenizer
# --- 1. إعداد قاعدة البيانات ---
DATABASE_URL = "sqlite:///./users.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=False)
    verification_token = Column(String, unique=True)

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- 2. إعدادات الأمان ---
SECRET_KEY = "super_secret_key_for_my_api" 
ALGORITHM = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def verify_password(plain_password: str, hashed_password: str):
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def get_password_hash(password: str):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def create_access_token(data: dict):
    expire = datetime.utcnow() + timedelta(minutes=30)
    to_encode = data.copy()
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None: raise HTTPException(status_code=401, detail="Invalid token")
    except: raise HTTPException(status_code=401, detail="Invalid token")
    
    user = db.query(User).filter(User.email == email).first()
    if not user: raise HTTPException(status_code=401, detail="User not found")
    return user

# --- 3. إعداد الذكاء الاصطناعي مع LoRA ---
app = FastAPI(title="DistilBERT Emotion API")

# مسار الموديل الأصلي (الذي تدربت عليه في البداية)
base_model_path = os.path.join(os.path.dirname(__file__), "distilbert_emotion_model")

# تحميل الموديل الأساسي ثم تركيب الـ LoRA Adapter عليه
base_model = AutoModelForSequenceClassification.from_pretrained(base_model_path)
model = PeftModel.from_pretrained(base_model, base_model_path) 
tokenizer = AutoTokenizer.from_pretrained(base_model_path)

# تحويل الموديل لـ pipeline
classifier = pipeline("text-classification", model=model, tokenizer=tokenizer, device=-1)

EMOTION_MAPPING = {"LABEL_0": "Sadness 😢", "LABEL_1": "Joy 😃", "LABEL_2": "Love 🥰", "LABEL_3": "Anger 😠", "LABEL_4": "Fear 😨", "LABEL_5": "Surprise 😲"}

# --- 4. المسارات (Endpoints) ---
class UserCreate(BaseModel):
    email: EmailStr
    password: str

@app.post("/auth/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    token = str(uuid.uuid4())
    new_user = User(email=user.email, hashed_password=get_password_hash(user.password), verification_token=token)
    db.add(new_user); db.commit()
    return {"message": "User registered! Please verify your email.", "verification_token": token}

@app.post("/auth/verify-email")
def verify_email(token: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.verification_token == token).first()
    if not user: raise HTTPException(status_code=400, detail="Invalid verification token")
    user.is_active = True; db.commit()
    return {"message": "Email verified successfully!"}

@app.post("/auth/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not user.is_active or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Account not verified or invalid credentials")
    return {"access_token": create_access_token(data={"sub": user.email}), "token_type": "bearer"}

@app.post("/ml/classify")
def classify_text(text: str, current_user: User = Depends(get_current_user)):
    prediction = classifier(text)
    return {"Category": EMOTION_MAPPING.get(prediction[0]['label']), "Confidence": prediction[0]['score']}