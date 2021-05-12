import os
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi import Depends, HTTPException, status
from .models.userModel import User, UserInDB
from .models.tokenModel import TokenData
from dotenv import load_dotenv
import pymongo
from bson.json_util import dumps

# Carrega as configurações da variável de ambiente
load_dotenv()

algorithm = os.getenv('ALGORITHM')
secret_key = os.getenv('SECRET_KEY')

# Converte a senha para o formato brcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Cria o scheme do Oauth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# MongoDb
path_mongo = os.getenv('MONGO_CONNECTION')
client = pymongo.MongoClient(path_mongo)
db_user = client.db.users

class UserController():

    def verify_password(plain_password, hashed_password):

        return pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(password):

        return pwd_context.hash(password)

    def get_user(mongo_db, username: str):
        if username in mongo_db:
            user_dict = mongo_db[username]
            return UserInDB(**user_dict)

    def authenticate_user(mongo_db, username: str, password: str):

        user = UserController.get_user(mongo_db, username)

        if not user:

            return False

        if not UserController.verify_password(password, user.hashed_password):

            return False

        return user

    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
        to_encode = data.copy()

        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=algorithm)
        return encoded_jwt

    async def get_current_user(token: str = Depends(oauth2_scheme)):
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            payload = jwt.decode(token, secret_key, algorithms=[algorithm])
            username: str = payload.get("sub")
            if username is None:
                raise credentials_exception
            token_data = TokenData(username=username)
        except JWTError:
            raise credentials_exception


        usernames = []
        list_user = []

        for user in db_user.find():
            usernames.append(user['username'])
            list_user.append(user)

        # Construindo datbase no formato do fastApi
        database_user_mongo = dict(zip(usernames, list_user))

        user = UserController.get_user(
            database_user_mongo, username=token_data.username)
        if user is None:
            raise credentials_exception

        return user

    async def get_current_active_user(current_user: User = Depends(get_current_user)):

        if current_user.status != 'A':

            raise HTTPException(status_code=400, detail="Inactive user")

        return current_user

    def create_user_db(form_data):

        now = datetime.now()

        data = now.strftime("%d/%m/%Y, %H:%M:%S H")

        userData = {
            "username": form_data.username,
            "full_name": form_data.full_name,
            "email": form_data.email,
            "hashed_password": UserController.get_password_hash(form_data.password),
            "role": "standard",
            "status": "A",
            "created_at":  data,
            "updated_at":  data
        }

        try:

            db_user.insert_one(userData)

            msg = f"User {userData['username']} successfully inserted into MongoDB!"

            return msg

        except Exception as e:
            print("Uma exceção ocorreu: ", e)
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"{e}",
                headers={"WWW-Authenticate": "Bearer"},
            )

    def get_user_db(username):

        username_exception = HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username dont exists",
            headers={"WWW-Authenticate": "Bearer"},
        )

        try:

            user = db_user.find_one({"username": f"{username}"})

            if user is None:
                raise username_exception

            user_json = dumps(user, indent=2)

            return user_json

        except Exception as e:
            raise username_exception

    def get_all_user_db():

        try:
            usernames = []
            list_user = []

            for user in db_user.find():
                usernames.append(user['username'])
                list_user.append(user)

            # Construindo datbase no formato do fastApi
            database_user_mongo = dict(zip(usernames, list_user))

            users = dumps(database_user_mongo, indent=2)

            return users

        except Exception as e:
            print("Uma exceção ocorreu: ", e)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"{e}",
                headers={"WWW-Authenticate": "Bearer"},
            )

    def update_user_db(form_data):

        username_exception = HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username dont exists",
            headers={"WWW-Authenticate": "Bearer"},
        )

        now = datetime.now()

        data = now.strftime("%d/%m/%Y, %H:%M:%S H")

        try: 
            user = db_user.find_one({"username": f"{form_data.username}"})

            if user is None:
                raise username_exception
                
            userData = {
                "username" : user['username'] if form_data.newUsername is None else form_data.newUsername,
                "full_name" : user['full_name'] if form_data.full_name is None else form_data.full_name,
                "email" : user['email'] if form_data.email is None else form_data.email,
                "hashed_password" : user['hashed_password'] if form_data.password is None else UserController.get_password_hash(form_data.password),
                "role" : user['role'] if form_data.role is None else form_data.role,
                "status" : user['status'] if form_data.status is  None else form_data.status,
                "created_at":  user['created_at'],
                "updated_at":  data
                }

        except Exception as e:
            raise username_exception

        try:

            if db_user.find_one({"email": form_data.email}) is None:

                mongo_query = {"username": form_data.username}

                db_user.update_one({"username": f"{form_data.username}"}, {"$set" : userData})

                msg = f"User {userData['username']} updated successfully into MongoDB!"

                return msg

            else:
                msg = "Email already registered!"

                return msg

        except Exception as e:
            print("Uma exceção ocorreu: ", e)
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"{e}",
                headers={"WWW-Authenticate": "Bearer"},
            )

    def delete_user_db(username):

        delete_user_exception = HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This user does not exist so it cannot be deleted",
            headers={"WWW-Authenticate": "Bearer"},
        )

        user = db_user.find_one({"username": f"{username}"})

        try: 

            if user is None:
                raise delete_user_exception

            db_user.delete_one({"username": f"{username}"})

            msg = f"User {username} successfully deleted"

            return msg

        except Exception as e:
            raise delete_user_exception
