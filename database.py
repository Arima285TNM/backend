import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Lấy DATABASE_URL từ environment variables
DATABASE_URL = os.environ.get('DATABASE_URL')

# Debug: In ra để kiểm tra (sẽ thấy trong logs)
print(f"DATABASE_URL: {DATABASE_URL}")

# Nếu không có DATABASE_URL, dùng SQLite fallback
if not DATABASE_URL:
    DATABASE_URL = "sqlite:///./local_db.db"
    print("Using SQLite fallback database")

# Fix PostgreSQL URL format for Railway
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    print("Fixed PostgreSQL URL format")

# Tạo engine - ĐẢM BẢO LUÔN CÓ DATABASE_URL
try:
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        pool_recycle=300,
        connect_args={"connect_timeout": 10} if DATABASE_URL.startswith("postgresql") else {}
    )
    print("Database engine created successfully")
except Exception as e:
    print(f"Error creating engine: {e}")
    # Fallback cứng
    engine = create_engine("sqlite:///./fallback.db")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
