# user/user_service.py
from core.core_service import CoreService
from modules.user.user_model import UserModel

user_service = CoreService(UserModel)
