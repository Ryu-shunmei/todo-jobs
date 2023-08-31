from auth import get_password_hash
from schemas.common import UserStatus
from .base import Base


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
            users.email = '{email}';
        """
        try:
            self.cursor.execute(sql)
            return self.cursor.fetchone()
        except Exception as e:
            print(e)

    async def add_user_with_pw(self, *, new_user):
        insert_user_sql = """
        INSERT INTO users
            (email,
            last_name,
            first_name,
            status)
        VALUES
            (%s, %s, %s, %s)
        RETURNING id,status,email;
        """
        user_values = (
            new_user.email,
            new_user.last_name,
            new_user.first_name,
            UserStatus.ok.value
        )

        insert_pw_sql = """
        INSERT INTO passwords
            (user_id, hashed_password, record)
        VALUES
            (%s, %s, %s);
        """

        try:
            self.cursor.execute(insert_user_sql, user_values)
            self.connection.commit()
            new_db_user = self.cursor.fetchone()
            new_db_user_id = new_db_user["id"]

            pw_values = (
                new_db_user_id,
                get_password_hash(new_user.password),
                1
            )
            self.cursor.execute(insert_pw_sql, pw_values)
            self.connection.commit()
            return new_db_user

        except Exception as e:
            print(e)

    async def query_pw_by_user_id(self, *, user_id):
        sql = f"""
        SELECT
            hashed_password
        FROM
            passwords
        WHERE
            user_id = '{user_id}'
        ORDER BY updated_at DESC;
        """
        try:
            self.cursor.execute(sql)
            return self.cursor.fetchone()
        except Exception as e:
            print(e)

    async def query_pws_by_user_id(self, *, user_id):
        sql = f"""
        SELECT
            user_id,
            hashed_password,
            record
        FROM
            passwords
        WHERE
            user_id = '{user_id}'
        ORDER BY record ASC;
        """
        try:
            self.cursor.execute(sql)
            return self.cursor.fetchall()
        except Exception as e:
            print(e)

    async def upsert_pw_by_user_id(self, *, user_id, hashed_password, record):
        sql = f"""
                MERGE INTO passwords p
                USING (values('{user_id}',{record})) as np(user_id, record)
                ON p.user_id = uuid(np.user_id) AND p.record = np.record
                WHEN MATCHED THEN 
                    UPDATE SET hashed_password = '{hashed_password}', record = {record}
                WHEN NOT MATCHED THEN
                    INSERT (user_id, hashed_password, record)
                    VALUES ('{user_id}', '{hashed_password}', {record})
            """
        try:
            self.cursor.execute(sql)
            self.connection.commit()
        except Exception as e:
            print(e)
