import datetime as dt

from pydantic import BaseModel, EmailStr
from core.core_schema import CoreSchema, CoreCreateSchema, CoreUpdateSchema

class TodoCreate(CoreCreateSchema):
    name: str
    description: str
    complete: bool = False
    deadline: dt.datetime

class TodoUpdate(CoreUpdateSchema):
    name: str | None = None
    description: str | None = None
    complete: bool | None = None
    deadline: dt.datetime | None = None

class TodoOut(CoreSchema[int]):
    name: str
    description: str
    complete: bool = False
    deadline: dt.datetime

    class Config:
        from_attributes = True