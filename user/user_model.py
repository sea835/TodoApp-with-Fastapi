from sqlalchemy import Column, Integer, String

from core.basemodel import BaseModel

class UserModel(BaseModel):
    __tablename__ = 'users'
    user_id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    password = Column(String(128), nullable=False)
    email = Column(String(100), unique=True, nullable=True)