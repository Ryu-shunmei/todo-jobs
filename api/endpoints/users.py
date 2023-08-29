from fastapi import APIRouter, Depends, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from schemas import NewUser, ComReturn, TokenPayload, TokenReturn, LoginUser, UpdatePwd
from sqlalchemy.orm import Session
from database import get_sesston
from crud import (
    check_user,
    add_new_user_with_pw,
    query_pw_with_user_id,
    query_pws_with_user_id,
    insert_pw,
    update_pw,
)
from auth import create_token
from typing import Union
from auth import verify_password
from config import settings

users_router = APIRouter()


@users_router.post("/user", response_model=Union[ComReturn, TokenReturn])
async def register(new_user: NewUser, db: Session = Depends(get_sesston)):
    is_exsit = await check_user(db, new_user.email)
    if is_exsit:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=ComReturn(message=f"Email {new_user.email} 已经存在").model_dump(),
        )
    new_db_user = await add_new_user_with_pw(db, new_user)
    payload = jsonable_encoder(TokenPayload.model_validate(new_db_user))
    token = create_token(payload)

    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content=TokenReturn(token=token).model_dump(),
    )


@users_router.post("/user/token", response_model=Union[ComReturn, TokenReturn])
async def login(user: LoginUser, db: Session = Depends(get_sesston)):
    is_exsit = await check_user(db, user.email)
    if not is_exsit:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=ComReturn(message=f"email {user.email} 用户不存在").model_dump(),
        )

    db_pw = await query_pw_with_user_id(db, is_exsit.id)

    if not verify_password(user.password, db_pw.hashed_password):
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content=ComReturn(message="password 错误").model_dump(),
        )

    payload = jsonable_encoder(TokenPayload.model_validate(is_exsit))
    token = create_token(payload)

    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content=TokenReturn(token=token).model_dump(),
    )


@users_router.put("/user/password", response_model=Union[ComReturn, TokenReturn])
async def pw_update(user: UpdatePwd, db: Session = Depends(get_sesston)):
    is_exsit = await check_user(db, user.email)
    if not is_exsit:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=ComReturn(message=f"email {user.email} 用户不存在").model_dump(),
        )
    db_pwds = await query_pws_with_user_id(db, is_exsit.id)

    for db_pwd in db_pwds:
        if verify_password(user.password, db_pwd.hashed_password):
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content=ComReturn(message="password already exist").model_dump(),
            )

    if len(db_pwds) == settings.PW_CHANGE_LIMIT:
        await update_pw(db, is_exsit.id, user.password)
    else:
        await insert_pw(db, is_exsit.id, len(db_pwds) + 1, user.password)

    payload = jsonable_encoder(TokenPayload.model_validate(is_exsit))
    token = create_token(payload)

    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content=TokenReturn(token=token).model_dump(),
    )
