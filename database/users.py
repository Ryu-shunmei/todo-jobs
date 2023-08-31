from .base import Base
from schemas.users import NewUser, UpdateUser
from schemas.common import UserStatus
from auth import get_password_hash


class DB_User(Base):
    async def check_user_with_email(self, *, email: str):
        sql = f"""-- 基于邮件查询用户
        SELECT
            id,
            email,
            last_name,
            first_name,
            status
        FROM
            users
        WHERE
            users.email = '{email}'
        """
        try:
            self.cursor.execute(sql)
            return self.cursor.fetchone()
        except Exception as e:
            print(e)

    async def add_user_with_email(self, *, new_user: NewUser):
        sql_user = """-- add user into users
        INSERT INTO users (email,last_name,first_name,status)
        VALUES (%s,%s,%s,%s)
        RETURNING id, email, status
        """

        values_user = (
            new_user.email,
            new_user.last_name,
            new_user.first_name,
            UserStatus.ok.value,
        )

        try:
            self.cursor.execute(sql_user, values_user)
            self.connection.commit()
            return self.cursor.fetchone()
        except Exception as e:
            print(e)

    async def add_pw_with_email(self, *, user_id, new_user: NewUser):
        sql_pw = """-- add pw into passwords
        INSERT INTO passwords (user_id,record,hashed_password)
        VALUES (%s,%s,%s)
        """

        values_pw = (user_id, 1, get_password_hash(new_user.password))

        try:
            self.cursor.execute(sql_pw, values_pw)
            self.connection.commit()
        except Exception as e:
            print(e)

    async def get_pw_by_id(self, *, id):
        sql = f"""-- get hashed_password by user_id
        SELECT
            hashed_password
        FROM
            passwords
        WHERE
            passwords.user_id = '{id}'
        """

        try:
            self.cursor.execute(sql)
            return self.cursor.fetchone()
        except Exception as e:
            print(e)

    async def get_pws_by_id(self, *, id):
        sql_pws = f"""-- get pws order by update time
        SELECT
            record,
            hashed_password
        FROM
            passwords
        WHERE
            passwords.user_id = '{id}'
        ORDER BY
            passwords.updated_at
        """
        try:
            self.cursor.execute(sql_pws)
            return self.cursor.fetchall()
        except Exception as e:
            print(e)

    async def add_pw_into_pws(self, *, user_id, record, user_update: UpdateUser):
        sql_update_pw = """-- add new pw into passwords
        INSERT INTO passwords (user_id,record,hashed_password)
        VALUES (%s,%s,%s)
        """

        values_update_pw = (user_id, record, get_password_hash(user_update.password))

        try:
            self.cursor.execute(sql_update_pw, values_update_pw)
            self.connection.commit()
        except Exception as e:
            print(e)

    async def update_pw_by_updated_at(self, *, user_id, user_update: UpdateUser):
        sql_update = f"""-- update pw by update time
        UPDATE
            passwords
        SET
            hashed_password = '{get_password_hash(user_update.password)}'
        WHERE
            record = (
            SELECT record
            FROM passwords
            WHERE user_id = '{user_id}'
            ORDER BY updated_at ASC
            LIMIT 1
            )
        """
        try:
            self.cursor.execute(sql_update)
            self.connection.commit()
        except Exception as e:
            print(e)
