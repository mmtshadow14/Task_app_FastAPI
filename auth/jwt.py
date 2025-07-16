# python packages
import jwt
import datetime
import time

# fastapi packages
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# sqlalchemy packages
from sqlalchemy.orm import Session


# application files
from core.config import settings
from core.database import Session
from tasks.models import UserModel
from core.database import get_db


db = Session()


# create a JWT token
def create_access_token(user_id):
    """
    we will generate a JWT token for the user with placing his account ID in the payload of the JWT token.
    """
    pyload = {
        'user_id': user_id,
        'iat': datetime.datetime.utcnow(),
        'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=5)
    }
    return jwt.encode(pyload, settings.JWT_SECRET_KEY, algorithm='HS256')


# retrieve the user
def retrieve_user_via_jwt(token):
    """
    retrieve the user from the JWT token that is sent in the head of the request to use it in the routes
     to do CRUD operations.
    """
    payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms='HS256')
    if payload['exp'] < int(time.time()):
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail='Token expired')
    user = db.query(UserModel).filter(UserModel.id == payload['user_id']).one_or_none()
    if user:
        return user
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')
