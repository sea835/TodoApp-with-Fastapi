from pydantic import BaseModel, Field
from typing import Optional

class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: Optional[str] = Field(default=None, max_length=100)

class UserCreate(UserBase):
    password: str = Field(..., min_length=6, max_length=128)

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None

class UserOut(UserBase):
    user_id: int
    username: str
    email: str | None = None

    class Config:
        from_attributes = True  # ORM mode