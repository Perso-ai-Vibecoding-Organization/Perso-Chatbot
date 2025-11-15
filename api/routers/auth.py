from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from api.core.database import get_db
from api.models.user import User
from api.schemas.user import UserCreate, UserLogin
from passlib.context import CryptContext

router = APIRouter()
pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")

@router.post("/signup")
def signup(user: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == user.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="이미 존재하는 이메일입니다.")

    new_user = User(
        email=user.email,
        password=pwd.hash(user.password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "회원가입 성공"}


@router.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()

    if not db_user:
        raise HTTPException(status_code=400, detail="회원이 아닙니다.")

    if not pwd.verify(user.password, db_user.password):
        raise HTTPException(status_code=400, detail="비밀번호가 일치하지 않습니다.")

    return {"message": "로그인 성공"}