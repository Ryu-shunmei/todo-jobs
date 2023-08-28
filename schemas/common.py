from pydantic import BaseModel
from enum import IntEnum


class ComReturn(BaseModel):
    message: str 


class UserStatus(IntEnum):
    ok = 1
    stop = 9