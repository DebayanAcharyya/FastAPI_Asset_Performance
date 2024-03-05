from fastapi import FastAPI, status, HTTPException, APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import RedirectResponse
from models.user import UserOut, UserAuth
from models.auth import TokenSchema
from authentication.utils import (
    get_hashed_password,
    create_access_token,
    create_refresh_token,
    verify_password
)
from uuid import uuid4
from config.db import Database
from motor.motor_asyncio import  AsyncIOMotorDatabase

auth = APIRouter()

# Access the 'db' attribute of the Database singleton
db: AsyncIOMotorDatabase = Database().db # type: ignore

@auth.post('/signup', summary="Create new user", response_model=UserOut)
async def create_user(data: UserAuth):
    user = await db.users.find_one({"email": data.email})
    if user is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exist"
        )
    
    user = {
        'email': data.email,
        'username' : data.username,
        'password': get_hashed_password(data.password)
        
    }
    result = await db.users.insert_one(user)
    return user

@auth.post('/login', summary="Create access and refresh tokens for user", response_model=TokenSchema)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await db.users.find_one({"username": form_data.username})
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password"
        )

    hashed_pass = user['password']
    if not verify_password(form_data.password, hashed_pass):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password"
        )
    
    return {
        "access_token": create_access_token(user['email']),
        "refresh_token": create_refresh_token(user['email']),
    }




    
