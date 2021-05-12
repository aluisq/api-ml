from pydantic import BaseModel
from typing import Optional

class User(BaseModel):
    username: str
    full_name : str
    email : str
    role : str
    status : str

class UserInDB(User):
    hashed_password: str

