import os
from fastapi import FastAPI, Depends, HTTPException, status, Form, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from database import SessionLocal, engine, get_db
import models
import schemas
import auth

# Health check trước khi import database
print("🚀 Starting StudyHub API...")

# Chỉ tạo tables nếu engine tồn tại
try:
    if engine:
        print("📦 Creating database tables...")
        models.Base.metadata.create_all(bind=engine)
        print("✅ Database tables created")
    else:
        print("❌ No database engine available")
except Exception as e:
    print(f"❌ Error creating tables: {e}")

app = FastAPI(title="StudyHub API", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check - không phụ thuộc database
@app.get("/")
def read_root():
    return {
        "message": "StudyHub API is running!", 
        "status": "healthy",
        "timestamp": datetime.utcnow()
    }

@app.get("/health")
def health_check():
    db_status = "unknown"
    try:
        # Kiểm tra kết nối database
        db = SessionLocal()
        db.execute("SELECT 1")
        db_status = "connected"
        db.close()
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    return {
        "status": "healthy", 
        "timestamp": datetime.utcnow(),
        "database": db_status
    }
# Auth endpoints
@app.post("/register")
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # Check if user exists
    db_user = db.query(models.User).filter(
        (models.User.email == user.email) | 
        (models.User.username == user.username)
    ).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email or username already registered")
    
    # Create new user
    hashed_password = auth.get_password_hash(user.password)
    db_user = models.User(
        email=user.email,
        username=user.username,
        full_name=user.full_name,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.post("/login")
def login(
    username: str = Form(...),
    password: str = Form(...), 
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user or not auth.verify_password(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    
    access_token = auth.create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

# Posts endpoints
@app.get("/posts")
def get_posts(db: Session = Depends(get_db)):
    posts = db.query(models.Post).all()
    return posts

@app.post("/posts")
def create_post(post: schemas.PostCreate, db: Session = Depends(get_db)):
    db_post = models.Post(
        title=post.title,
        content=post.content,
        category=post.category,
        author_id=1  # Tạm thời fix author_id
    )
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post

# Categories endpoints
@app.get("/categories")
def get_categories(db: Session = Depends(get_db)):
    return db.query(models.Category).all()

# Tạo dữ liệu mẫu
@app.on_event("startup")
def startup():
    db = SessionLocal()
    try:
        # Tạo categories mặc định
        if not db.query(models.Category).first():
            categories = [
                models.Category(name="Technology", description="Technology related posts"),
                models.Category(name="Mathematics", description="Mathematics discussions"),
            ]
            db.add_all(categories)
            db.commit()
    except Exception as e:
        print(f"Startup error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
