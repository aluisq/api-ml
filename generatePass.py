from jose import jwt

from passlib.context import CryptContext

password = '!@rthur'

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

senha = pwd_context.hash(password)


print("MINHA SENHA: ", senha)