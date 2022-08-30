from fastapi import Body, APIRouter, Query, Path, File, Form,UploadFile, HTTPException, status, Depends, Security, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Union, List
from datetime import datetime, timedelta
from random import randint
import dependencies
import main
# from users import get_current_user
from schemas import User, Todo, TodoCreate, TodoUpdate
import users
import crud
import models
from dependencies import get_db
router = APIRouter(
    prefix="/todos",
)



async def todo_dependency_check(todo_id: int = Path(default=None), owner: User = Depends(users.get_current_active_user), dependencies=Depends(get_db)):
    todo_db = crud.get_todo(todo_id=todo_id)
    if not todo_db:
        raise HTTPException(detail="the data with these id does not exist", status_code=status.HTTP_404_NOT_FOUND)
    if todo_db.owner_id != owner.id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="you are not the owner of these todo")
    return todo_db

# get all blog todo
@router.get("/", response_model=List[Todo], status_code=status.HTTP_200_OK)
async def get_todos( current_user: User = Depends(users.get_current_user), dependencies=Depends(get_db)) -> List[Todo]:
    return crud.get_todos(user_id=current_user.id)




# todo a blog todo
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=Todo)
async def create_todo(todo: TodoCreate, current_user: User = Depends(users.get_current_user), dependencies=Depends(get_db)) -> Todo:
  
    return crud.create_user_todo(todo=todo, user_id=current_user.id)

# # get a to
# @router.get("/{todo_id}", response_model=todo)
# async def blog_todo(todo_id: int = Path(default=None), dependencies=Depends(get_db)):
#     todo_data = crud.get_todo(todo_id=todo_id)
#     if not todo_data:
#         raise HTTPException(detail="the data with these id was not found", status_code=status.HTTP_404_NOT_FOUND)
#     return todo_data


@router.patch("/{todo_id}", response_model=Todo)
async def update_todo_for_user(*, todo_data: Todo = Depends(todo_dependency_check), 
todo: TodoUpdate, dependencies=Depends(get_db), current_user: User = Depends(users.get_current_user)) -> Todo:
    return crud.update_user_todo(payload=todo, todo_data=todo_data)


@router.delete("/{todo_id}")
async def delete_todos(todo_data: Todo = Depends(todo_dependency_check), dependencies=Depends(get_db)) -> str:
    crud.delete_todo(todo_data=todo_data)
    return 'successfully deleted'

