from fastapi import APIRouter, Depends, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
import schemas
from database.users import DB_User

users_router = APIRouter()

from pydantic import TypeAdapter
from typing import List

@users_router.post('/user')
async def register(new_user:schemas.NewUser):
    db_user_op = DB_User()

    is_exist = await db_user_op.check_user_with_email(email=new_user.email)

    UserList = TypeAdapter(List[schemas.TokenPayload])
   
    print(jsonable_encoder(UserList.validate_python(is_exist)))
    # print(schemas.TokenPayload.model_validate(is_exist).model_dump())



