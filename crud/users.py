from database.orm import User, Password
from sqlalchemy.orm import Session
from typing import Optional
from schemas import NewUser, UserStatus
from auth import get_password_hash
from uuid import UUID


async def check_user(db:Session, email:str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()

async def add_new_user_with_pw(db:Session, new_user:NewUser) -> Optional[User]:
    new_db_user = User(
        email = new_user.email,
        first_name = new_user.first_name,
        last_name = new_user.last_name,
        status = UserStatus.ok.value
    )

    db.add(new_db_user)
    db.commit()
    db.refresh(new_db_user)

    new_db_pw = Password(
        user_id = new_db_user.id,
        record = 1,
        hashed_password = get_password_hash(new_user.password)
    )

    db.add(new_db_pw)
    db.commit()

    return new_db_user


async def query_pw_with_user_id(db:Session, user_id:UUID) -> Optional[Password]:
    return db.query(Password).filter(Password.user_id == user_id).order_by(Password.updated_at.desc()).first()
