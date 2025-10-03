from typing import Generic, TypeVar, Optional, Any
from pydantic import BaseModel

T = TypeVar("T")

class ResponseSchema(BaseModel, Generic[T]):
    status_code: int = 200          # HTTP status code (200, 404, 500,...)
    is_success: bool = True         # True nếu thành công, False nếu lỗi
    message: str = "Success"        # Nội dung kèm theo
    data: Optional[T] = None        # Payload (có thể None)

    # Helper methods để tạo response nhanh
    @classmethod
    def success(cls, data: Optional[T] = None, message: str = "Success", status_code: int = 200):
        return cls(status_code=status_code, is_success=True, message=message, data=data)

    @classmethod
    def fail(cls, message: str = "Failed", status_code: int = 400, data: Optional[Any] = None):
        return cls(status_code=status_code, is_success=False, message=message, data=data)
