# core/core_controller.py
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Generic, TypeVar, List
from sqlalchemy.orm import Session
from database.db import get_db
from core.core_service import CoreService

TModel = TypeVar("TModel")
TCreate = TypeVar("TCreate")
TUpdate = TypeVar("TUpdate")
TOut = TypeVar("TOut")

class CoreController(Generic[TModel, TCreate, TUpdate, TOut]):
    def __init__(
        self,
        service: CoreService,
        create_schema,
        update_schema,
        out_schema,
        prefix: str,
        tag: str,
        search_fields: List[str] = None
    ):
        self.router = APIRouter(prefix=prefix, tags=[tag])
        self.service = service

        CreateSchema = create_schema
        UpdateSchema = update_schema
        OutSchema = out_schema

        # --- CRUD ---
        @self.router.get("", response_model=List[OutSchema])
        def get_all(db: Session = Depends(get_db)):
            return self.service.get_all(db)

        @self.router.post("", response_model=OutSchema, status_code=201)
        def create(item: CreateSchema, db: Session = Depends(get_db)):
            return self.service.create(db, item.dict())

        @self.router.delete("/{obj_id}")
        def delete(obj_id: int, db: Session = Depends(get_db)):
            ok = self.service.soft_delete(db, obj_id)
            if not ok:
                raise HTTPException(status_code=404, detail="Not found")
            return {"status": "deleted"}

        # --- Search (nếu có truyền search_fields) ---
        if search_fields:
            @self.router.get("/search", response_model=List[OutSchema])
            def search(q: str = Query(...), db: Session = Depends(get_db)):
                return self.service.search(db, q, fields=search_fields)

        # --- Pagination ---
        @self.router.get("/page", response_model=List[OutSchema])
        def get_page(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
            return self.service.get_page(db, skip=skip, limit=limit)

        @self.router.get("/{obj_id}", response_model=OutSchema)
        def get_by_id(obj_id: int, db: Session = Depends(get_db)):
            obj = self.service.get_by_id(db, obj_id)
            if not obj:
                raise HTTPException(status_code=404, detail="Not found")
            return obj

        @self.router.put("/{obj_id}", response_model=OutSchema)
        def update(obj_id: int, item: UpdateSchema, db: Session = Depends(get_db)):
            obj = self.service.update(db, obj_id, item.dict(exclude_unset=True))
            if not obj:
                raise HTTPException(status_code=404, detail="Not found")
            return obj
