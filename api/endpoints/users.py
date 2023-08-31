from fastapi import APIRouter, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from config import settings
import schemas
from database.users import DB_User
from schemas.common import ComReturn
from auth import create_token, verify_password, get_password_hash

users_router = APIRouter()


@users_router.post("/user")
async def register(new_user: schemas.NewUser):
    db_user_op = DB_User()

    is_exist = await db_user_op.check_user_with_email(email=new_user.email)

    if is_exist:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=ComReturn(message=f"{new_user.email} already existed").model_dump(),
        )

    payload = jsonable_encoder(
        schemas.TokenPayload.model_validate(
            await db_user_op.add_user_with_email(new_user=new_user)
        )
    )

    await db_user_op.add_pw_with_email(user_id=payload["id"], new_user=new_user)

    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content=schemas.TokenReturn(token=create_token(payload)).model_dump(),
    )


@users_router.post("/user/token")
async def login(user_login: schemas.LoginUser):
    db_user_op = DB_User()

    is_exist = await db_user_op.check_user_with_email(email=user_login.email)
    if not is_exist:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=ComReturn(
                message=f"{user_login.email} is not existed"
            ).model_dump(),
        )
    db_pw = await db_user_op.get_pw_by_id(id=is_exist["id"])

    if not verify_password(user_login.password, db_pw["hashed_password"]):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=ComReturn(message="wrong password").model_dump(),
        )

    payload = jsonable_encoder(schemas.TokenPayload.model_validate(is_exist))

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=schemas.TokenReturn(token=create_token(payload)).model_dump(),
    )


@users_router.put("/user/password")
async def update_pw(user_update: schemas.UpdateUser):
    db_user_op = DB_User()

    is_exist = await db_user_op.check_user_with_email(email=user_update.email)
    if not is_exist:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=ComReturn(
                message=f"{user_update.email} is not existed"
            ).model_dump(),
        )

    pws = await db_user_op.get_pws_by_id(id=is_exist["id"])
    for pw in pws:
        if verify_password(user_update.password, pw["hashed_password"]):
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content=ComReturn(
                    message="This password has been used 3 times recently"
                ).model_dump(),
            )

    if len(pws) == settings.PW_CHANGE_LIMIT:
        await db_user_op.update_pw_by_updated_at(
            user_id=is_exist["id"], user_update=user_update
        )
    else:
        await db_user_op.add_pw_into_pws(
            user_id=is_exist["id"], record=len(pws) + 1, user_update=user_update
        )

    payload = jsonable_encoder(schemas.TokenPayload.model_validate(is_exist))

    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content=schemas.TokenReturn(token=create_token(payload)).model_dump(),
    )
