from fastapi import APIRouter, Depends, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from schemas import NewUser, ComReturn, TokenPayload, TokenReturn, LoginUser, PwUser
from collections import deque
from sqlalchemy.orm import Session
from database import get_sesston
from crud import (
    check_user, add_new_user_with_pw,
    query_pw_with_user_id, query_all_pws, upsert_pw,
)
from typing import Union
from auth import verify_password, get_password_hash, create_token
from config import settings

users_router = APIRouter()


@users_router.post('/user', response_model=Union[ComReturn, TokenReturn])
async def register(new_user: NewUser, db: Session = Depends(get_sesston)):
    is_exsit = await check_user(db, new_user.email)
    if is_exsit:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,
                            content=ComReturn(message=f'Email {new_user.email} 已经存在').model_dump_json())
    new_db_user = await add_new_user_with_pw(db, new_user)
    payload = jsonable_encoder(TokenPayload.model_validate(new_db_user))
    token = create_token(payload)

    return JSONResponse(status_code=status.HTTP_201_CREATED, content=TokenReturn(token=token).model_dump())


@users_router.post('/user/token', response_model=Union[ComReturn, TokenReturn])
async def login(user: LoginUser, db: Session = Depends(get_sesston)):
    is_exsit = await check_user(db, user.email)
    if not is_exsit:
        JSONResponse(status_code=status.HTTP_404_NOT_FOUND,
                     content=ComReturn(message=f'email {user.email} 用户不存在'))

    db_pw = await query_pw_with_user_id(db, is_exsit.id)

    if not verify_password(user.password, db_pw.hashed_password):
        return JSONResponse(status_code=status.HTTP_403_FORBIDDEN, content=ComReturn(message='password 错误'))

    payload = jsonable_encoder(TokenPayload.model_validate(is_exsit))
    token = create_token(payload)

    return JSONResponse(status_code=status.HTTP_201_CREATED, content=TokenReturn(token=token).model_dump())


@users_router.put('/user/password', response_model=ComReturn)
async def change_pw(new_user: PwUser, db: Session = Depends(get_sesston)):
    new_hashed_pw = get_password_hash(new_user.password)
    user = await check_user(db, new_user.email)
    if not user:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,
                            content=ComReturn(message=f'email {user.email} 用户不存在').model_dump_json())

    prev_pws = await query_all_pws(db, user.id)
    pw_deque = deque(prev_pws, maxlen=settings.PW_CHANGE_LIMIT)
    pw_list = [verify_password(
        new_user.password, pw.hashed_password) for pw in prev_pws]

    if any(pw_list):
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,
                            content=ComReturn(message='密码不能和最近三次内设置的密码相同').model_dump_json())

    if len(pw_deque) == settings.PW_CHANGE_LIMIT:
        try:
            left = pw_deque.popleft()
            await upsert_pw(db, left.user_id, new_hashed_pw, left.record)
        except Exception as error:
            print("密码修改失败")
            raise error

    else:
        try:
            last = pw_deque.pop()
            await upsert_pw(db, last.user_id, new_hashed_pw, last.record+1)
        except Exception as error:
            print("密码修改失败")
            raise error

    return JSONResponse(status_code=status.HTTP_200_OK,
                        content=ComReturn(message='密码修改成功').model_dump_json())
