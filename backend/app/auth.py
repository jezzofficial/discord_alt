# app/auth.py

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session, select
from . import models, schemas, utils
from .database import get_session

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

@router.post("/register", response_model=schemas.Token)
def register(user: schemas.UserCreate, db: Session = Depends(get_session)):
    existing_user = db.query(models.User).filter(models.User.username == user.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")

    hashed_password = utils.get_password_hash(user.password)
    db_user = models.User(username=user.username, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    access_token = utils.create_access_token(data={"sub": db_user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/login", response_model=schemas.Token)
def login(user: schemas.UserLogin, db: Session = Depends(get_session)):
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if not db_user or not utils.verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect username or password")

    access_token = utils.create_access_token(data={"sub": db_user.username})
    return {"access_token": access_token, "token_type": "bearer"}

# Получение информации о текущем пользователе
@router.get("/me", response_model=schemas.UserCreate)
def get_me(token: str = Depends(oauth2_scheme), session: Session = Depends(get_session)):
    try:
        payload = utils.decode_jwt_token(token)  # Декодируем токен
        username = payload.get("sub")  # Извлекаем имя пользователя
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")

        user = session.exec(select(models.User).where(models.User.username == username)).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        return schemas.UserCreate(username=user.username, password="***")  # Не возвращаем пароль
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token or expired")
