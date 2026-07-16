from fastapi import APIRouter, HTTPException, Depends
from ..schemas import LoginRequest, Token
from ..auth import authenticate_user, create_access_token

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/login", response_model=Token)
def login(data: LoginRequest):
    if not authenticate_user(data.password):
        raise HTTPException(status_code=401, detail="كلمة المرور غير صحيحة")
    access_token = create_access_token({"sub": "admin"})
    return {"access_token": access_token, "token_type": "bearer"}
