from typing import Any, List, Union
from datetime import datetime
import peewee
from pydantic import BaseModel, EmailStr
from pydantic.utils import GetterDict


class PeeweeGetterDict(GetterDict):
    def get(self, key: Any, default: Any = None):
        res = getattr(self._obj, key, default)
        if isinstance(res, peewee.ModelSelect):
            return list(res)
        return res

class TodoBase(BaseModel):
    isDone: Union[bool, None] = None
    created_at: Union[datetime, None] = None
    completed_at: Union[datetime, None] = None
    set_completed_at: Union[datetime, None] = None
    
class TodoCreateBase(TodoBase):
    todo: str
    

class TodoCreate(BaseModel):
    todo: str

class TodoUpdate(TodoBase):
    todo: Union[str, None] = None

class Todo(TodoCreateBase):
    id: int
    owner_id: int

    class Config:
        orm_mode = True
        getter_dict = PeeweeGetterDict


class UserBase(BaseModel):
    username: str
    email: EmailStr
    


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    full_name: Union[str, None] = None
    verified: Union[bool, None] = None
    todos: List[Todo] = []

    class Config:
        orm_mode = True
        getter_dict = PeeweeGetterDict

