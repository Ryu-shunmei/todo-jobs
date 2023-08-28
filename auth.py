from jose import jwt
from datetime import datetime, timedelta
from config import settings
from passlib.context import CryptContext

__pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_token(data: dict, expires_delta: timedelta = None) -> str:
    to_encode = data.copy()
    print(to_encode)
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.TOKEN_EXPIRE_MINUTES
        )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def verify_password(plain_password, hashed_password):
    return __pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return __pwd_context.hash(password)
