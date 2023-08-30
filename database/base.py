import psycopg2
from psycopg2.extras import RealDictCursor
from config import settings


class Base:
    def __init__(self) -> None:
        self.connection = psycopg2.connect(settings.DATABASE_URI)
        self.cursor = self.connection.cursor(cursor_factory=RealDictCursor)


    def __del__(self) -> None:
        self.cursor.close()
        self.connection.close()
