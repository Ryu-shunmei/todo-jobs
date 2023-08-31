from typing import List
from pydantic import TypeAdapter
from fastapi import APIRouter, Depends, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from auth import create_token, get_password_hash
import schemas
from database.users import DB_User
from auth import verify_password
from collections import deque


users_router = APIRouter()


@users_router.post('/user')
async def register(new_user: schemas.NewUser):
    db_user_op = DB_User()

    is_exist = await db_user_op.check_user_with_email(email=new_user.email)
    if is_exist:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=jsonable_encoder(schemas.common.ComReturn(
                message=f'Email: {new_user.email} 已存在'))
        )

    new_db_user = await db_user_op.add_user_with_pw(new_user=new_user)
    payload = jsonable_encoder(
        schemas.TokenPayload.model_validate(new_db_user))
    token = create_token(payload)
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content=schemas.TokenReturn(
            type='Bearer', token=token
        ).model_dump()
    )


@users_router.post('/user/token')
async def login(login_user: schemas.LoginUser):
    db_user_op = DB_User()

    is_exist = await db_user_op.check_user_with_email(email=login_user.email)
    if not is_exist:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=jsonable_encoder(schemas.common.ComReturn(
                message=f'Email: {login_user.email} 不存在'))
        )

    db_pw = await db_user_op.query_pw_by_user_id(user_id=is_exist["id"])
    if not verify_password(login_user.password, db_pw["hashed_password"]):
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content=jsonable_encoder(schemas.common.ComReturn(
                message=f'密码错误'))
        )

    payload = jsonable_encoder(
        schemas.TokenPayload.model_validate(is_exist))
    token = create_token(payload)
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content=schemas.TokenReturn(
            type='Bearer', token=token
        ).model_dump()
    )


@users_router.put('/user/password')
async def change_password(new_user: schemas.UpdateUser):
    db_user_op = DB_User()
    is_exist = await db_user_op.check_user_with_email(email=new_user.email)
    if not is_exist:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=jsonable_encoder(schemas.common.ComReturn(
                message=f'Email: {new_user.email} 不存在'))
        )
    pws = await db_user_op.query_pws_by_user_id(user_id=is_exist["id"])
    pw_deque = deque(schemas.PwUserList.validate_python(pws), maxlen=3)

    for pw in pw_deque:
        if verify_password(new_user.password, pw.hashed_password):
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content=jsonable_encoder(schemas.common.ComReturn(
                    message="不能和最近三次的密码相同"
                ))
            )

    new_hashed_pw = get_password_hash(new_user.password)
    if (len(pw_deque) == 3):
        try:
            first_pw = pw_deque.popleft()
            await db_user_op.upsert_pw_by_user_id(user_id=first_pw.user_id,
                                                  hashed_password=new_hashed_pw, record=first_pw.record)
        except Exception as e:
            print("密码修改失败")
            raise e
    else:
        try:
            last_pw = pw_deque.pop()
            await db_user_op.upsert_pw_by_user_id(user_id=last_pw.user_id,
                                                  hashed_password=new_hashed_pw, record=last_pw.record+1)
        except Exception as e:
            print("密码修改失败")
            raise e
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=schemas.common.ComReturn(message="密码修改成功").model_dump()
    )
