from fastapi import APIRouter, HTTPException, status, Depends, BackgroundTasks, Path, Security
from pydantic import BaseModel
from fastapi.security import (
    OAuth2PasswordBearer,
    OAuth2PasswordRequestForm,
    SecurityScopes,
)
from uuid import UUID
from jose import JWTError, jwt
from typing import Union, List, Any
from datetime import datetime, timedelta
from fastapi.encoders import jsonable_encoder
from dotenv import dotenv_values
# handing database

import crud
import models
import os
import schemas
from dependencies import get_db

config = dotenv_values(".env")
# auth conig

ACCESS_TOKEN_EXPIRE_MINUTES = 30  # 30 minutes
REFRESH_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7 # 7 days
REFRESH_SECRET_KEY = os.getenv('REFRESH_SECRET_KEY')
SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = "HS256"


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class TokenData(BaseModel):
    username: Union[str, None] = None

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


router = APIRouter()


def create_access_token(subject: Union[str, Any], expires_delta: int = None) -> str:
    if expires_delta is not None:
        expires_delta = datetime.utcnow() + expires_delta
    else:
        expires_delta = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {"exp": expires_delta, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, ALGORITHM)
    return encoded_jwt

def create_refresh_token(subject: Union[str, Any], expires_delta: int = None) -> str:
    if expires_delta is not None:
        expires_delta = datetime.utcnow() + expires_delta
    else:
        expires_delta = datetime.utcnow() + timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {"exp": expires_delta, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, REFRESH_SECRET_KEY, ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme), dependencies= Depends(get_db)) -> schemas.User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        
        payload = jwt.decode(token, SECRET_KEY, ALGORITHM)
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError as e:
        raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail= f"Could not validate credentials due to: {e}",
        headers={"WWW-Authenticate": "Bearer"},
    )
    user = crud.get_user_by_username(username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(current_user: schemas.User = Depends(get_current_user)) -> schemas.User:
    if not current_user.verified:
        raise HTTPException(status_code=400, detail="unverified user")
    return current_user





@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), dependencies= Depends(get_db)) -> Token:
    user = crud.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    refresh_token = create_refresh_token(user.username)
    access_token = create_access_token(user.username)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

# getting a user
@router.get("/users/me/", response_model=schemas.User, description="to check if you have being verified")
async def read_users_me(current_user: schemas.User = Security(get_current_active_user)):
    return current_user

@router.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: int, dependencies= Depends(get_db)):
    db_user = crud.get_user(user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@router.get("/users/", response_model=List[schemas.User])
def read_users(skip: int = 0, limit: int = 100, dependencies= Depends(get_db)):
    users = crud.get_users(skip=skip, limit=limit)
    return users



# background task
def write_notification(email: str, message=""):
    with open("log.txt", mode="a") as email_file:
        content = f"{email}: {message}"
        email_file.write(content + "\n")
# to be implemented
def verify_user(user):
    user["verified"] = True


@router.post("/users/", response_model=schemas.User, status_code=status.HTTP_201_CREATED)
async def register(*, user: schemas.UserCreate, dependencies = Depends(get_db), background_tasks: BackgroundTasks) -> schemas.User:
    
    db_user_username = crud.get_user_by_username(username=user.username)
    db_user_email = crud.get_user_by_email(email=user.email)
    if db_user_username:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="The username is alredy taken, please try a different one")
    if db_user_email:
        raise HTTPException(status_code=400, detail="Email already registered")
    background_tasks.add_task(write_notification, user.email, message="please check your email to verify account")
    # background_tasks.add_task(verify_user, fake_users_db[user.username])
    return crud.create_user(user=user)
