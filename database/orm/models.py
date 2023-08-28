# coding: utf-8
from sqlalchemy import Column, ForeignKey, SmallInteger, String, text
from sqlalchemy.dialects.postgresql import TIMESTAMP, UUID
from .base import Base


class JobStatusMaster(Base):
    __tablename__ = 'job_status_master'

    code = Column(SmallInteger, primary_key=True)
    mark = Column(String(255), nullable=False)


class UserStatusMaster(Base):
    __tablename__ = 'user_status_master'

    code = Column(SmallInteger, primary_key=True)
    mark = Column(String(255), nullable=False)


class User(Base):
    __tablename__ = 'users'

    id = Column(UUID, primary_key=True, default=text('gen_random_uuid()'))
    email = Column(String(255), nullable=False)
    last_name = Column(String(48), nullable=False)
    first_name = Column(String(48), nullable=False)
    status = Column(ForeignKey('user_status_master.code'), nullable=False)


class TodoJob(Base):
    __tablename__ = 'todo_jobs'

    user_id = Column(ForeignKey('users.id'), primary_key=True)
    content = Column(String(512), nullable=False)
    finish = Column(TIMESTAMP(precision=0), nullable=False)
    start = Column(TIMESTAMP(precision=0), nullable=False)
    finished = Column(TIMESTAMP(precision=0), nullable=False)
    status = Column(ForeignKey('job_status_master.code'), nullable=False)


class Password(Base):
    __tablename__ = 'passwords'

    user_id = Column(ForeignKey('users.id'), primary_key=True, nullable=False)
    record = Column(SmallInteger, primary_key=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
