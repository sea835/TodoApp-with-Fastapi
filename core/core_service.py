# core/core_service.py
from typing import Generic, TypeVar, Type, Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import or_
from core.basemodel import BaseModel
import datetime

TModel = TypeVar("TModel", bound=BaseModel)

class CoreService(Generic[TModel]):
    def __init__(self, model: Type[TModel]):
        self.model = model
        """
        Lấy cột PK đầu tiên, mục đích để lấy được id của nó
        """
        self.pk = model.__mapper__.primary_key[0]

    # --- CRUD cơ bản ---
    def get_all(self, db: Session) -> List[TModel]:
        return db.query(self.model).filter(self.model.IsDeleted == False).all()

    def get_by_id(self, db: Session, obj_id: int) -> Optional[TModel]:
        return (
            db.query(self.model)
            .filter(self.pk == obj_id, self.model.IsDeleted == False)
            .first()
        )

    def create(self, db: Session, obj_in: dict) -> TModel:
        db_obj = self.model(**obj_in)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, obj_id: int, obj_in: dict) -> Optional[TModel]:
        db_obj = self.get_by_id(db, obj_id)
        if not db_obj:
            return None
        for field, value in obj_in.items():
            setattr(db_obj, field, value)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def soft_delete(self, db: Session, obj_id: int, deleted_by: Optional[str] = None) -> bool:
        db_obj = self.get_by_id(db, obj_id)
        if not db_obj:
            return False
        db_obj.IsDeleted = True
        db_obj.UpdatedBy = deleted_by
        db_obj.UpdatedAt = datetime.datetime.utcnow()
        db.commit()
        return True

    def search(self, db: Session, keyword: str, fields: List[str]) -> List[TModel]:
        filters = [getattr(self.model, f).ilike(f"%{keyword}%") for f in fields]
        return (
            db.query(self.model)
            .filter(self.model.IsDeleted == False)
            .filter(or_(*filters))
            .all()
        )

    def get_page(self, db: Session, skip: int = 0, limit: int = 10) -> List[TModel]:
        return (
            db.query(self.model)
            .filter(self.model.IsDeleted == False)
            .offset(skip)
            .limit(limit)
            .all()
        )
