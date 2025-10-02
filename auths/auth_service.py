from datetime import datetime, timedelta
from typing import Union, Any
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from user.user_model import UserModel

import jwt

SECURITY_ALGORITHM = 'HS256'
SECRET_KEY = '123456'

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def generate_token(username: Union[str, Any]) -> str:
    expire = datetime.utcnow() + timedelta(
        seconds=60 * 60 * 24 * 3  # Expired after 3 days
    )
    to_encode = {
        "exp": expire, "username": username
    }
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=SECURITY_ALGORITHM)
    return encoded_jwt

def verify_password(db: Session, username: str, password: str) -> bool:
    # Tìm user trong DB
    user = db.query(UserModel).filter(UserModel.username == username).first()
    if not user:
        return False

    # So sánh password nhập với password hash trong DB
    return pwd_context.verify(password, user.password)