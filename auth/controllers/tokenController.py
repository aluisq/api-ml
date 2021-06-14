import os
from fastapi import HTTPException, status
from dotenv import load_dotenv
from .userController import UserController
import pymongo
from datetime import datetime, timedelta

load_dotenv()  # take environment variables from .env.

# Time to expires token
expires_minutes = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES'))

# MongoDb
path_mongo= os.getenv('MONGO_CONNECTION')
client = pymongo.MongoClient(path_mongo)
db_user =  client.db.users


class TokenController():

    def access_token(form_data):

        usernames = []
        list_user = []

        for user in db_user.find():
            usernames.append(user['username'])
            list_user.append(user)

        # Construindo datbase no formato do fastApi 
        database_user_mongo = dict(zip(usernames, list_user))

        # # Instância de um usuário
        user = UserController.authenticate_user(database_user_mongo, form_data.username, form_data.password)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        access_token_expires = timedelta(minutes=expires_minutes)
        access_token = UserController.create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)

        return {"access_token": access_token, "token_type": "bearer"}

