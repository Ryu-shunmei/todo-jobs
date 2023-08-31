from pydantic import BaseModel, Field, ConfigDict
from .common import UserStatus
from uuid import UUID


class BaseUser(BaseModel):
    email: str = Field(
        ...,
        pattern=r"^[a-zA-Z0-9_.+-]+@([a-zA-Z0-9][a-zA-Z0-9-]*[a-zA-Z0-9]*\.)+[a-zA-Z]{2,}$",
    )


class LoginUser(BaseUser):
    password: str


class UpdateUser(BaseUser):
    password: str = Field(..., min_length=6, max_length=16)


class NewUser(BaseUser):
    last_name: str = Field(..., max_length=48)
    first_name: str = Field(..., max_length=48)
    password: str = Field(..., min_length=6, max_length=16)


class TokenPayload(BaseUser):
    id: UUID
    status: UserStatus

    model_config = ConfigDict(from_attributes=True)


class TokenReturn(BaseModel):
    type: str = Field(default="Bearer")
    token: str
