from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

class UserBase(BaseModel):
    email: str
    username: str
    full_name: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    role: str
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class PostBase(BaseModel):
    title: str
    content: str
    category: str  

class PostCreate(PostBase):
    pass

class Post(PostBase):
    id: int
    author_id: int
    created_at: datetime
    updated_at: datetime
    author: User
    
    class Config:
        from_attributes = True

class CommentBase(BaseModel):
    content: str

class CommentCreate(CommentBase):
    pass

class Comment(CommentBase):
    id: int
    author_id: int
    post_id: int
    created_at: datetime
    author: User
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class CategoryBase(BaseModel):
    name: str
    description: Optional[str] = None

class Category(CategoryBase):
    id: int
    
    class Config:
        from_attributes = True

class DocumentBase(BaseModel):
    title: str
    description: Optional[str] = None
    category: str

class DocumentCreate(DocumentBase):
    pass

class Document(DocumentBase):
    id: int
    file_name: str
    file_type: str
    file_size: int
    author_id: int
    download_count: int
    view_count: int
    created_at: datetime
    author: User
    
    class Config:
        from_attributes = True

# THÊM SCHEMA FORUM CATEGORY
class ForumCategoryBase(BaseModel):
    name: str
    description: Optional[str] = None
    color: Optional[str] = "#007bff"
    icon: Optional[str] = "📁"

class ForumCategory(ForumCategoryBase):
    id: int
    order: int
    created_at: datetime
    
    class Config:
        from_attributes = True