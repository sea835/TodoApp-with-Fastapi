# user/user_controller.py
from core.core_controller import CoreController
from user.user_service import user_service
from user.user_schema import UserCreate, UserUpdate, UserOut
from user.user_model import UserModel

user_controller = CoreController(
    service=user_service,
    create_schema=UserCreate,
    update_schema=UserUpdate,
    out_schema=UserOut,
    prefix="/users",
    tag="Users"
)
router = user_controller.router
