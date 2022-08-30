
from typing import Union, List 
from passlib.context import CryptContext
from fastapi import HTTPException, status
import datetime
from uuid import UUID
import schemas
import models


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# users config passward
def verify_password(plain_password, hashed_password) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password) -> str:
    return pwd_context.hash(password)


def get_user(user_id: UUID) -> schemas.User:
    return models.User.filter(models.User.id == user_id).first()

def get_user_by_username(username: str) -> schemas.User:
    return models.User.filter(models.User.username == username).first()
def authenticate_user(username: str, password: str) -> schemas.User:
    # checking first if the user is in the database
    user = get_user_by_username(username=username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def get_user_by_email(email: str) -> schemas.User:
    return models.User.filter(models.User.email == email).first()


def get_users(skip: int = 0, limit: int = 100) -> List[schemas.User]:
    return list(models.User.select().offset(skip).limit(limit))


def create_user(user: schemas.UserCreate) -> schemas.User:
    hashed_password = get_password_hash(user.password)
    db_user = models.User(username=user.username, email=user.email, full_name="", verified=True, hashed_password=hashed_password)
    db_user.save()
    return db_user


# //handling todo

def get_todo(todo_id: int) -> schemas.Todo:
    return models.Todo.filter(models.Todo.id == todo_id).first()

def get_todos(user_id: UUID) -> List[schemas.Todo]:
    return list(models.Todo.filter(models.Todo.owner_id == user_id))


def create_user_todo(*, todo: schemas.TodoCreate, user_id: int) -> schemas.Todo:
    db_todo = models.Todo(**todo.dict(), owner_id=user_id)
    db_todo.save()
    return db_todo

def update_user_todo(todo_data: schemas.Todo, payload: schemas.TodoUpdate) -> schemas.Todo:
    update_data = payload.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(todo_data, key, value)
    
    if todo_data.isDone:
        todo_data.completed_at = datetime.datetime.now()
    else:
        todo_data.completed_at = None
        todo_data.set_completed_at = None
    todo_data.save()
    return todo_data

def delete_todo(todo_data: schemas.Todo):
    db_todo = models.Todo.get_by_id(todo_data.id)
    db_todo.delete_instance()