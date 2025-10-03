from fastapi import APIRouter, HTTPException
from fastapi.params import Depends
from sqlalchemy.orm import Session

from modules.auths.auth_service import verify_password, generate_token
from modules.auths.login_request_model import LoginRequest

from database.db import get_db

router = APIRouter(
    prefix="/auths",
    tags=["auths"],
)

@router.post('/login')
def login(request_data: LoginRequest, db: Session = Depends(get_db)):
    print(f'[x] request_data: {request_data.__dict__}')
    if verify_password(db, username=request_data.username, password=request_data.password):
        token = generate_token(request_data.username, request_data.role)
        return {
            'token': token
        }
    else:
        raise HTTPException(status_code=404, detail="User not found")