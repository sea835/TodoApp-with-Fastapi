# user/user_controller.py
from core.core_controller import CoreController
from modules.user.user_service import user_service
from modules.user.user_schema import UserCreate, UserUpdate, UserOut

user_controller = CoreController(
    service=user_service,
    create_schema=UserCreate,
    update_schema=UserUpdate,
    out_schema=UserOut,
    prefix="/users",
    tag="Users"
)
router = user_controller.router
