from sqlalchemy import Column, DateTime, text
from sqlalchemy.ext.declarative import as_declarative


@as_declarative()
class Base:
    created_at = Column(DateTime, nullable=False, server_default=text("now()"))
    updated_at = Column(DateTime, nullable=False, server_default=text("now()"))
