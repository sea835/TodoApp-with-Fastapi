from typing import Generic, TypeVar, Type, Optional, List, Iterable, Any, Dict
from sqlalchemy.orm import Session
from sqlalchemy import or_, inspect as sa_inspect
from core.basemodel import BaseModel
import datetime

TModel = TypeVar("TModel", bound=BaseModel)


class CoreService(Generic[TModel]):
    def __init__(self, model: Type[TModel]):
        """
        Khởi tạo service cho 1 model.

        Args:
            model (Type[TModel]): SQLAlchemy model kế thừa từ BaseModel.
        """
        self.model = model
        self.pk = model.__mapper__.primary_key[0]

    def get_all(self, db: Session) -> List[TModel]:
        """
        Lấy tất cả record còn tồn tại (IsDeleted=False).

        Args:
            db (Session): SQLAlchemy session.

        Returns:
            List[TModel]: Danh sách bản ghi.

        Example:
            user_service.get_all(db)
        """
        return db.query(self.model).filter(self.model.IsDeleted == False).all()

    def get_by_id(self, db: Session, obj_id: int) -> Optional[TModel]:
        """
        Lấy 1 record theo id (chỉ lấy bản chưa xoá mềm).

        Args:
            db (Session): SQLAlchemy session.
            obj_id (int): Id bản ghi.

        Returns:
            Optional[TModel]: Bản ghi hoặc None nếu không tìm thấy.

        Example:
            user_service.get_by_id(db, 5)
        """
        return (
            db.query(self.model)
            .filter(self.pk == obj_id, self.model.IsDeleted == False)
            .first()
        )

    def create(self, db: Session, obj_in: dict) -> TModel:
        """
        Tạo mới 1 record.

        Args:
            db (Session): SQLAlchemy session.
            obj_in (dict): Dữ liệu khởi tạo.

        Returns:
            TModel: Record vừa tạo.

        Example:
            user_service.create(db, {"username": "admin"})
        """
        db_obj = self.model(**obj_in)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, obj_id: int, obj_in: dict) -> Optional[TModel]:
        """
        Cập nhật record với toàn bộ field trong obj_in.

        Args:
            db (Session): SQLAlchemy session.
            obj_id (int): Id bản ghi cần update.
            obj_in (dict): Dữ liệu mới.

        Returns:
            Optional[TModel]: Record sau khi update hoặc None nếu không tìm thấy.

        Example:
            user_service.update(db, 5, {"username": "new_name"})
        """
        db_obj = self.get_by_id(db, obj_id)
        if not db_obj:
            return None
        for field, value in obj_in.items():
            setattr(db_obj, field, value)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def soft_delete(self, db: Session, obj_id: int, deleted_by: Optional[str] = None) -> bool:
        """
        Xoá mềm 1 record (IsDeleted=True).

        Args:
            db (Session): SQLAlchemy session.
            obj_id (int): Id bản ghi cần xoá.
            deleted_by (str, optional): Người thực hiện xoá.

        Returns:
            bool: True nếu xoá thành công, False nếu không tìm thấy.

        Example:
            user_service.soft_delete(db, 5, deleted_by="admin")
        """
        db_obj = self.get_by_id(db, obj_id)
        if not db_obj:
            return False
        db_obj.IsDeleted = True
        db_obj.UpdatedBy = deleted_by
        db_obj.UpdatedAt = datetime.datetime.utcnow()
        db.commit()
        return True

    def search(self, db: Session, keyword: str, fields: List[str]) -> List[TModel]:
        """
        Tìm kiếm record theo từ khoá trong nhiều field.

        Args:
            db (Session): SQLAlchemy session.
            keyword (str): Từ khoá cần tìm.
            fields (List[str]): Danh sách tên cột để tìm kiếm.

        Returns:
            List[TModel]: Các bản ghi phù hợp.

        Example:
            user_service.search(db, "admin", ["username", "email"])
        """
        filters = [getattr(self.model, f).ilike(f"%{keyword}%") for f in fields]
        return (
            db.query(self.model)
            .filter(self.model.IsDeleted == False)
            .filter(or_(*filters))
            .all()
        )

    def get_page(self, db: Session, skip: int = 0, limit: int = 10) -> List[TModel]:
        """
        Phân trang dữ liệu.

        Args:
            db (Session): SQLAlchemy session.
            skip (int): Số bản ghi bỏ qua.
            limit (int): Số bản ghi lấy.

        Returns:
            List[TModel]: Danh sách record.

        Example:
            user_service.get_page(db, skip=0, limit=20)
        """
        return (
            db.query(self.model)
            .filter(self.model.IsDeleted == False)
            .offset(skip)
            .limit(limit)
            .all()
        )

    @staticmethod
    def _as_dict(obj: Any) -> Dict[str, Any]:
        """
        Chuyển object về dict.

        Args:
            obj (Any): dict, Pydantic model hoặc ORM instance.

        Returns:
            Dict[str, Any]: Dữ liệu dạng dict.
        """
        if obj is None:
            return {}
        if isinstance(obj, dict):
            return obj
        if hasattr(obj, "model_dump") and callable(obj.model_dump):
            return obj.model_dump(exclude_unset=True)
        if hasattr(obj, "dict") and callable(obj.dict):
            return obj.dict(exclude_unset=True)
        return {k: getattr(obj, k) for k in dir(obj) if not k.startswith("_") and not callable(getattr(obj, k))}

    def _writable_columns(self) -> set[str]:
        """
        Lấy danh sách cột cho phép ghi (loại bỏ PK & audit fields).

        Returns:
            set[str]: Các cột hợp lệ để update.
        """
        audit = {"CreatedAt", "UpdatedAt", "CreatedBy", "UpdatedBy", "IsDeleted"}
        mapper = sa_inspect(self.model)
        cols = {c.key for c in mapper.columns}
        cols.discard(self.pk.key)
        cols = cols.difference(audit)
        return cols

    def clone(self, db: Session, obj_id: int, overrides: Optional[Dict[str, Any]] = None) -> Optional[TModel]:
        """
        Nhân bản 1 record.

        Args:
            db (Session): SQLAlchemy session.
            obj_id (int): Id bản ghi cần clone.
            overrides (Dict[str, Any], optional): Giá trị ghi đè.

        Returns:
            Optional[TModel]: Record mới được clone.

        Example:
            user_service.clone(db, 5, overrides={"username": "copy_user"})
        """
        src = self.get_by_id(db, obj_id)
        if not src:
            return None
        writable = self._writable_columns()
        payload = {col: getattr(src, col) for col in writable}
        if overrides:
            payload.update({k: v for k, v in overrides.items() if k in writable})
        if "IsActive" in sa_inspect(self.model).columns:
            payload.setdefault("IsActive", True)
        return self.create(db, payload)

    def update_from(self, db: Session, obj_id: int, source_obj: Any, fields: Iterable[str]) -> Optional[TModel]:
        """
        Cập nhật record từ 1 object nguồn (dict/Pydantic/ORM) theo danh sách field.

        Args:
            db (Session): SQLAlchemy session.
            obj_id (int): Id record cần cập nhật.
            source_obj (Any): Object chứa dữ liệu nguồn.
            fields (Iterable[str]): Danh sách field cần copy.

        Returns:
            Optional[TModel]: Record đã cập nhật hoặc None nếu không có.

        Example:
            user_service.update_from(db, 5, user_update_schema, ["username", "email"])
        """
        db_obj = self.get_by_id(db, obj_id)
        if not db_obj:
            return None
        src = self._as_dict(source_obj)
        writable = self._writable_columns()
        for name in fields:
            if name in src and name in writable:
                setattr(db_obj, name, src[name])
        db_obj.UpdatedAt = datetime.datetime.utcnow()
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update_fields(self, db: Session, obj_id: int, values: Dict[str, Any]) -> Optional[TModel]:
        """
        Cập nhật record bằng dict field->value.

        Args:
            db (Session): SQLAlchemy session.
            obj_id (int): Id record cần cập nhật.
            values (Dict[str, Any]): Dữ liệu mới.

        Returns:
            Optional[TModel]: Record đã cập nhật hoặc None nếu không có.

        Example:
            user_service.update_fields(db, 5, {"username": "new_name"})
        """
        db_obj = self.get_by_id(db, obj_id)
        if not db_obj:
            return None
        writable = self._writable_columns()
        for k, v in values.items():
            if k in writable:
                setattr(db_obj, k, v)
        db_obj.UpdatedAt = datetime.datetime.utcnow()
        db.commit()
        db.refresh(db_obj)
        return db_obj
