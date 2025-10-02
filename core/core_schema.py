from typing import Generic, TypeVar, Optional
from pydantic import BaseModel
from datetime import datetime

TId = TypeVar("TId", bound=int)

class CoreSchema(BaseModel, Generic[TId]):
    id: Optional[TId] = None
    CreatedAt: Optional[datetime] = None
    UpdatedAt: Optional[datetime] = None
    CreatedBy: Optional[str] = None
    UpdatedBy: Optional[str] = None
    IsDeleted: Optional[bool] = False
    IsActive: Optional[bool] = True

    class Config:
        from_attributes = True

class CoreCreateSchema(BaseModel):
    CreatedBy: Optional[str] = None

class CoreUpdateSchema(BaseModel):
    UpdatedBy: Optional[str] = None
    IsActive: Optional[bool] = None