from fastapi import APIRouter, Depends, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from schemas import NewUser, ComReturn, TokenPayload, TokenReturn, LoginUser, UpUser
from sqlalchemy.orm import Session
from database import get_sesston
from crud import check_user, add_new_user_with_pw, query_pw_with_user_id, query_all_pw, add_pw, change_pw
from auth import create_token
from typing import Union
from auth import verify_password
from collections import deque
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
    print(is_exsit)
    if not is_exsit:
        JSONResponse(status_code=status.HTTP_404_NOT_FOUND,
                     content=ComReturn(message=f'email {user.email} 用户不存在'))

    db_pw = await query_pw_with_user_id(db, is_exsit.id)

    if not verify_password(user.password, db_pw.hashed_password):
        return JSONResponse(status_code=status.HTTP_403_FORBIDDEN, content=ComReturn(message='password 错误'))

    payload = jsonable_encoder(TokenPayload.model_validate(is_exsit))
    token = create_token(payload)

    return JSONResponse(status_code=status.HTTP_201_CREATED, content=TokenReturn(token=token).model_dump())


@users_router.put('/user/password')
async def update_pw(up_user: UpUser, db: Session = Depends(get_sesston)):
    user = await check_user(db, up_user.email)

    if not user:
        JSONResponse(status_code=status.HTTP_404_NOT_FOUND,
                     content=ComReturn(message=f'email {up_user.email} 用户不存在').model_dump_json())
    all_pw = await query_all_pw(db=db, user_id=user.id)
    all_pw_list = [pw.hashed_password for pw in all_pw]

    for pw in all_pw_list:
        if verify_password(up_user.new_password, pw):
            return JSONResponse(status_code=status.HTTP_403_FORBIDDEN,
                                content=ComReturn(message=f'{up_user.new_password}已经存在').model_dump_json())

    all_pw_deque = deque(all_pw, maxlen=settings.PW_CHANGE_LIMIT)
    if len(all_pw_deque) < 3:
        pw = all_pw_deque.pop()
        await add_pw(db=db, user_id=user.id, pw_new=up_user.new_password, record=pw.record+1)
    else:
        pw = all_pw_deque.popleft()
        await change_pw(db=db, user_id=user.id, pw_new=up_user.new_password, record=pw.record)

    return JSONResponse(status_code=status.HTTP_200_OK,
                        content=ComReturn(message=f'密码已经修改成功').model_dump_json())
