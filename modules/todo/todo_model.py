from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, func
from core.basemodel import BaseModel

class TodoModel(BaseModel):
    __tablename__ = 'todo'
    todo_id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    complete = Column(Boolean)
    deadline = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

