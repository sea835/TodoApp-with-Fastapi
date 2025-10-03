from fastapi import APIRouter, Depends, Query
from typing import Generic, TypeVar, List
from sqlalchemy.orm import Session
from database.db import get_db
from core.core_service import CoreService
from core.response_schema import ResponseSchema

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
        self.router = APIRouter(prefix="/api" + prefix, tags=[tag])
        self.service = service

        CreateSchema = create_schema
        UpdateSchema = update_schema
        OutSchema = out_schema

        # --- CRUD ---
        @self.router.get("", response_model=ResponseSchema[List[OutSchema]])
        def get_all(db: Session = Depends(get_db)):
            try:
                items = self.service.get_all(db)
                return ResponseSchema.success(data=items, message="Fetched successfully")
            except Exception as e:
                return ResponseSchema.fail(message=f"Error fetching data: {str(e)}", status_code=500)

        @self.router.post("", response_model=ResponseSchema[OutSchema], status_code=201)
        def create(item: CreateSchema, db: Session = Depends(get_db)):
            try:
                obj = self.service.create(db, item.dict())
                return ResponseSchema.success(data=obj, message="Created successfully", status_code=201)
            except Exception as e:
                return ResponseSchema.fail(message=f"Error creating: {str(e)}", status_code=500)

        @self.router.delete("/{obj_id}", response_model=ResponseSchema[dict])
        def delete(obj_id: int, db: Session = Depends(get_db)):
            try:
                ok = self.service.soft_delete(db, obj_id)
                if not ok:
                    return ResponseSchema.fail(message="Not found", status_code=404)
                return ResponseSchema.success(data={"status": "deleted"}, message="Deleted successfully")
            except Exception as e:
                return ResponseSchema.fail(message=f"Error deleting: {str(e)}", status_code=500)

        # --- Search (nếu có truyền search_fields) ---
        if search_fields:
            @self.router.get("/search", response_model=ResponseSchema[List[OutSchema]])
            def search(q: str = Query(...), db: Session = Depends(get_db)):
                try:
                    results = self.service.search(db, q, fields=search_fields)
                    return ResponseSchema.success(data=results, message="Search results")
                except Exception as e:
                    return ResponseSchema.fail(message=f"Error searching: {str(e)}", status_code=500)

        # --- Pagination ---
        @self.router.get("/page", response_model=ResponseSchema[List[OutSchema]])
        def get_page(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
            try:
                items = self.service.get_page(db, skip=skip, limit=limit)
                return ResponseSchema.success(data=items, message="Paged results")
            except Exception as e:
                return ResponseSchema.fail(message=f"Error pagination: {str(e)}", status_code=500)

        @self.router.get("/{obj_id}", response_model=ResponseSchema[OutSchema])
        def get_by_id(obj_id: int, db: Session = Depends(get_db)):
            try:
                obj = self.service.get_by_id(db, obj_id)
                if not obj:
                    return ResponseSchema.fail(message="Not found", status_code=404)
                return ResponseSchema.success(data=obj, message="Found")
            except Exception as e:
                return ResponseSchema.fail(message=f"Error fetching by id: {str(e)}", status_code=500)

        @self.router.put("/{obj_id}", response_model=ResponseSchema[OutSchema])
        def update(obj_id: int, item: UpdateSchema, db: Session = Depends(get_db)):
            try:
                obj = self.service.update(db, obj_id, item.dict(exclude_unset=True))
                if not obj:
                    return ResponseSchema.fail(message="Not found", status_code=404)
                return ResponseSchema.success(data=obj, message="Updated successfully")
            except Exception as e:
                return ResponseSchema.fail(message=f"Error updating: {str(e)}", status_code=500)
