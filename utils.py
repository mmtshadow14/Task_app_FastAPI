# python packages
from passlib.hash import bcrypt
import random

# fastapi packages
from fastapi import APIRouter, Depends, HTTPException, status, Cookie, Response

# app models
from tasks.models import OtpcodeModel


def generate_hash_password(password):
    hashed_password = bcrypt.hash(password)
    return hashed_password


def verify_password(password, hashed_password):
    is_valid = bcrypt.verify(password, hashed_password)
    return is_valid


def generate_otpcode(user_id, response):
    otp_obj = OtpcodeModel(user_id=user_id, code=random.randint(1000, 9999))
    response.set_cookie(key='user_id', value=user_id)
    print('==============================')
    print(otp_obj.code)
    print('==============================')
    return otp_obj
