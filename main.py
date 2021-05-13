import os
import pymongo
from fastapi import Depends, FastAPI, HTTPException, status
from datetime import datetime, timedelta
from typing import Optional
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from auth.userController import UserController
from auth.tokenController import TokenController
from auth.models.userModel import User
from auth.models.tokenModel import Token
from forms.userForm import UserForm
from forms.updateUserForm import UpdateUser
from dotenv import load_dotenv
from bson.json_util import dumps
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()  # take environment variables from .env.

# Instance  APP
app = FastAPI()


origins = [
    "http://localhost:3000",
]



# add CORS

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



# Create Token
@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):

    token = TokenController.access_token(form_data)

    return token

# Insert User
@app.post('/mongo/users/new-user')
async def create_one_user_db(current_user: User = Depends(UserController.get_current_active_user),form_data: UserForm = Depends()):

    # Execute the method to create
    response = UserController.create_user_db(form_data)

    return response

# Get All Users
@app.get('/mongo/users')
async def get_all_users_db(current_user: User = Depends(UserController.get_current_active_user)):

    users = UserController.get_all_user_db()

    return users

# Get One User
@app.get('/mongo/users/{username}')
async def get_one_user_db(username: str, current_user: User = Depends(UserController.get_current_active_user)):
    
    user = UserController.get_user_db(username)

    return user

#  Update One User
@app.put('/mongo/users/')
async def update_one_user_db(current_user: User = Depends(UserController.get_current_active_user), form_data: UpdateUser = Depends()):

    if current_user.role == "adm":

        response = UserController.update_user_db(form_data)
    else:
        response = "You dont have permission to update an user."

    return response

# Delete One User
@app.delete('/mongo/users/{username}')
async def delete_one_user_db(username: str, current_user: User = Depends(UserController.get_current_active_user)):

    if current_user.role == "adm":
        response = UserController.delete_user_db(username)
    else:
        response = "You dont have permission to delete an user."

    return response

#testeAPI

@app.get('/teste')
async def teste():

    json = {
        "meu teste" : "testando!",
        "oto teste" : "eae?"
    }

    return json