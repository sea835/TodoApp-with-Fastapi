from sqlalchemy import Column, DateTime, Boolean, String, func
from sqlalchemy.orm import declared_attr

from database.db import Base


class BaseModel(Base):
    __abstract__ = True  # Quan trọng: không tạo bảng cho lớp này

    @declared_attr.directive
    def __tablename__(cls) -> str:
        # Tự động tạo tên bảng = tên class thường -> lowercase
        return cls.__name__.lower()

    CreatedAt = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    UpdatedAt = Column(DateTime(timezone=True), onupdate=func.now())
    CreatedBy = Column(String(50), nullable=True)
    UpdatedBy = Column(String(50), nullable=True)
    IsDeleted = Column(Boolean, default=False, nullable=False)
    IsActive = Column(Boolean, default=True, nullable=False)
