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
            return self.cursor.fetchall()
        except Exception as e:
            print(e)
