import secrets
from pydantic_settings import BaseSettings, SettingsConfigDict


class __Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env', env_file_encoding='utf8', case_sensitive=True)

    DB_HOST: str
    DB_PORT: str
    DB_USER: str
    DB_NAME: str
    DB_PASSWORD: str

    PW_CHANGE_LIMIT: int

    SECRET_KEY: str = secrets.token_urlsafe(32)
    ALGORITHM: str
    TOKEN_EXPIRE_MINUTES: int

    @property
    def SQLALCHEMY_DATABASE_URI(self):
        return f'postgresql+psycopg2://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}'


settings = __Settings()
